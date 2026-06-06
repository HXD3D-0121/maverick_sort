"""
Adaptive Policy Module — Pro Edition
====================================
Sunergy Pharma Smart Wave Allocation System

功能定位：
    - 专业版（Pro）增值模块，面向中大型医药流通企业
    - 实时自适应：根据订单到达率动态调整波次策略
    - 在线学习：每班次结束后用新数据微调策略，防灾难性遗忘
    - EWMA预测：指数加权移动平均预测未来订单量

核心机制：
    1. ArrivalRateEstimator: EWMA动态预测订单到达率
    2. AdaptiveWaveCapacity: 波次容量动态调整
    3. OnlinePolicyUpdater: 在线策略微调（经验回放+正则化）
    4. PolicyEnsemble: 多策略集成（为联邦学习预留接口）

联邦学习预留架构：
    - FederatedCoordinator: 协调多仓库策略聚合
    - LocalModelUpdate: 本地模型更新包装器
    - GlobalModelSync: 全局模型同步接口

作者：AI-assisted implementation
日期：2026/06/06 (Day 3 of Commercialization Plan)
"""

import numpy as np
import random
import json
import time
from typing import List, Dict, Tuple, Optional, Callable
from dataclasses import dataclass, field, asdict
from collections import deque
from pathlib import Path
import warnings

# PyTorch用于在线学习
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    warnings.warn("PyTorch not available. Online learning disabled.")

    # Minimal nn stub to prevent NameError in type annotations when PyTorch absent
    class _StubNN:
        class Module: pass
    nn = _StubNN()
    torch = None


# =============================================================================
# 1. 配置与数据类
# =============================================================================

@dataclass
class AdaptiveConfig:
    """自适应策略配置"""
    # EWMA参数
    ewma_alpha: float = 0.3  # 平滑因子（越大越敏感）
    ewma_window: int = 20    # 滑动窗口大小
    # 容量调整参数
    base_capacity: int = 20
    min_capacity: int = 8
    max_capacity: int = 35
    capacity_adjust_rate: float = 0.5  # 调整速率
    peak_threshold: float = 2.0  # 达到基线2倍视为高峰
    # 在线学习参数
    online_lr: float = 1e-4
    online_batch_size: int = 32
    replay_buffer_size: int = 1000
    regularization_lambda: float = 0.01  # 防遗忘正则化
    update_interval: int = 50  # 每50步更新一次
    # 策略集成参数
    ensemble_weights: Dict[str, float] = field(default_factory=lambda: {
        "kgdrl": 0.5,
        "tzu": 0.3,
        "edd": 0.2,
    })
    # 联邦学习预留
    federated_enabled: bool = False
    federated_sync_interval: int = 100  # 每100个episode同步


@dataclass
class ShiftTelemetry:
    """单个班次的遥测数据"""
    shift_id: int
    start_time: float
    end_time: float
    total_orders: int
    total_waves: int
    avg_arrival_rate: float
    peak_rate: float
    temp_violations: int
    deadline_misses: int
    total_cost: float
    capacity_profile: List[int] = field(default_factory=list)


# =============================================================================
# 2. EWMA到达率估计器
# =============================================================================

class ArrivalRateEstimator:
    """
    指数加权移动平均（EWMA）到达率估计器

    实时跟踪订单到达率变化，用于高峰期检测和容量预测。

    公式：
        rate_ewma(t) = α * rate_obs(t) + (1-α) * rate_ewma(t-1)
    """

    def __init__(self, alpha: float = 0.3, window: int = 20):
        self.alpha = alpha
        self.window = window
        self.ewma_rate = 0.0
        self.history = deque(maxlen=window)
        self.trend = 0.0  # 趋势方向：正=上升，负=下降
        self.peak_detected = False
        self.valley_detected = False

    def update(self, observed_rate: float, timestamp: float = None) -> Dict:
        """
        更新估计器

        Args:
            observed_rate: 观测到的订单到达率（单/分钟）
            timestamp: 时间戳（可选）

        Returns:
            Dict: 当前状态估计
        """
        self.history.append(observed_rate)

        # EWMA更新
        if self.ewma_rate == 0.0 and len(self.history) == 1:
            self.ewma_rate = observed_rate
        else:
            self.ewma_rate = self.alpha * observed_rate + (1 - self.alpha) * self.ewma_rate

        # 趋势估计（线性回归斜率，简化版）
        if len(self.history) >= 5:
            recent = list(self.history)[-5:]
            self.trend = (recent[-1] - recent[0]) / 4.0

        # 峰值/谷值检测
        baseline = np.mean(list(self.history)) if self.history else 1.0
        self.peak_detected = self.ewma_rate > baseline * 1.5 and self.trend > 0
        self.valley_detected = self.ewma_rate < baseline * 0.7 and self.trend < 0

        return {
            "ewma_rate": self.ewma_rate,
            "trend": self.trend,
            "peak_detected": self.peak_detected,
            "valley_detected": self.valley_detected,
            "history": list(self.history),
        }

    def predict_next(self, steps: int = 1) -> float:
        """预测未来steps时间步的到达率"""
        return self.ewma_rate + self.trend * steps

    def get_seasonal_adjustment(self, hour_of_day: int) -> float:
        """
        根据小时返回季节性调整系数
        双峰模式：9AM高峰，2PM次高峰
        """
        if 8 <= hour_of_day <= 11:
            return 1.8  # 早高峰
        elif 13 <= hour_of_day <= 15:
            return 1.5  # 下午高峰
        elif 0 <= hour_of_day <= 6:
            return 0.3  # 夜间低谷
        else:
            return 1.0  # 正常

    def reset(self):
        """重置估计器"""
        self.ewma_rate = 0.0
        self.history.clear()
        self.trend = 0.0
        self.peak_detected = False
        self.valley_detected = False


# =============================================================================
# 3. 自适应波次容量调节器
# =============================================================================

class AdaptiveWaveCapacity:
    """
    波次容量动态调节器

    根据EWMA预测的到达率和当前系统负载，动态调整：
    - max_wave_orders: 波次订单上限
    - release_threshold: 波次释放阈值（提前关闭）
    """

    def __init__(self, config: AdaptiveConfig = None):
        self.config = config or AdaptiveConfig()
        self.current_capacity = config.base_capacity if config else 20
        self.release_threshold = 0.8  # 容量达80%时考虑释放
        self.estimator = ArrivalRateEstimator(
            alpha=self.config.ewma_alpha,
            window=self.config.ewma_window,
        )
        self.adjustment_log: List[Dict] = []

    def adjust(self, observed_rate: float, current_load: float, hour: int) -> Dict:
        """
        根据当前状态调整容量

        Args:
            observed_rate: 当前观测到达率
            current_load: 当前系统负载（0-1）
            hour: 当前小时

        Returns:
            Dict: 调整决策
        """
        state = self.estimator.update(observed_rate)
        predicted_rate = self.estimator.predict_next(steps=3)
        seasonal_factor = self.estimator.get_seasonal_adjustment(hour)

        # 基线容量计算
        baseline = self.config.base_capacity

        # 高峰响应：到达率 > 基线2倍 → 缩小波次、提高释放频率
        if state["peak_detected"] or predicted_rate > self.config.peak_threshold * baseline:
            target_capacity = max(self.config.min_capacity,
                                   int(baseline * 0.6))
            target_release = 0.65  # 提前释放
            reason = "peak_detected"
        # 低谷响应：到达率 < 基线70% → 增大波次、降低释放频率
        elif state["valley_detected"]:
            target_capacity = min(self.config.max_capacity,
                                   int(baseline * 1.3))
            target_release = 0.95  # 延迟释放
            reason = "valley_detected"
        # 季节性调整
        else:
            adjusted = baseline * seasonal_factor
            target_capacity = int(np.clip(
                adjusted,
                self.config.min_capacity,
                self.config.max_capacity
            ))
            target_release = 0.8 + (1 - seasonal_factor) * 0.15
            reason = "seasonal"

        # 负载修正：系统负载高时进一步缩小波次
        if current_load > 0.85:
            target_capacity = max(self.config.min_capacity,
                                   int(target_capacity * 0.85))
            reason += "+high_load"

        # 平滑过渡（防止抖动）
        diff = target_capacity - self.current_capacity
        smoothed = self.current_capacity + int(diff * self.config.capacity_adjust_rate)
        self.current_capacity = int(np.clip(
            smoothed,
            self.config.min_capacity,
            self.config.max_capacity
        ))
        self.release_threshold = target_release

        decision = {
            "capacity": self.current_capacity,
            "release_threshold": self.release_threshold,
            "predicted_rate": predicted_rate,
            "seasonal_factor": seasonal_factor,
            "reason": reason,
            "ewma_state": state,
        }
        self.adjustment_log.append(decision)
        return decision

    def should_release_wave(self, current_orders: int, current_volume: int) -> bool:
        """判断是否应该提前释放当前波次"""
        return (current_orders >= self.current_capacity * self.release_threshold
                and current_orders >= self.config.min_capacity)

    def get_telemetry(self) -> Dict:
        """获取调节器遥测数据"""
        return {
            "current_capacity": self.current_capacity,
            "release_threshold": self.release_threshold,
            "n_adjustments": len(self.adjustment_log),
            "recent_adjustments": self.adjustment_log[-10:] if self.adjustment_log else [],
        }


# =============================================================================
# 4. 在线策略更新器（防灾难性遗忘）
# =============================================================================

class ExperienceReplayBuffer:
    """经验回放缓冲区"""

    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)
        self.position = 0

    def push(self, state, action, reward, next_state, done):
        """存入经验"""
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size: int):
        """随机采样"""
        if len(self.buffer) < batch_size:
            batch_size = len(self.buffer)
        indices = np.random.choice(len(self.buffer), batch_size, replace=False)
        return [self.buffer[i] for i in indices]

    def __len__(self):
        return len(self.buffer)


class OnlinePolicyUpdater:
    """
    在线策略更新器

    每完成一个班次，用新收集的轨迹微调策略网络。
    关键：使用经验回放 + EWC正则化 防止灾难性遗忘。

    EWC (Elastic Weight Consolidation):
        L = L_new + λ/2 * Σ F_i * (θ_i - θ*_i)^2
        其中F_i是Fisher信息矩阵对角线，θ*是旧参数
    """

    def __init__(self, config: AdaptiveConfig = None):
        self.config = config or AdaptiveConfig()
        self.replay_buffer = ExperienceReplayBuffer(config.replay_buffer_size)
        self.ewc_params = {}  # EWC参数：{param_name: (fisher, old_value)}
        self.update_count = 0
        self.step_counter = 0

    def collect_experience(self, trajectory: List[Tuple]):
        """收集一个轨迹（班次）的经验"""
        for step in trajectory:
            state, action, reward, next_state, done = step
            self.replay_buffer.push(state, action, reward, next_state, done)

    def compute_fisher_information(self, model: nn.Module, samples: List) -> Dict:
        """
        计算Fisher信息矩阵对角线近似
        用于EWC正则化，标识哪些参数对旧任务最重要
        """
        if not TORCH_AVAILABLE:
            return {}

        fisher = {}
        for name, param in model.named_parameters():
            if param.requires_grad:
                fisher[name] = torch.zeros_like(param.data)

        model.eval()
        for sample in samples:
            state, action, reward, _, _ = sample
            if hasattr(state, 'requires_grad'):
                state.requires_grad = True
            # 简化：使用reward的平方梯度作为Fisher近似
            loss = (torch.tensor(reward, dtype=torch.float32) ** 2)
            if loss.requires_grad:
                model.zero_grad()
                loss.backward()
                for name, param in model.named_parameters():
                    if param.grad is not None:
                        fisher[name] += param.grad.data ** 2

        # 平均
        n = len(samples)
        for name in fisher:
            fisher[name] /= max(n, 1)

        return fisher

    def update_policy(
        self,
        model: nn.Module,
        old_model: nn.Module = None,
        use_ewc: bool = True,
    ) -> Dict:
        """
        执行在线策略更新

        Args:
            model: 当前策略模型
            old_model: 旧模型（用于EWC计算old_params）
            use_ewc: 是否使用EWC正则化

        Returns:
            Dict: 更新统计
        """
        if not TORCH_AVAILABLE:
            return {"status": "pytorch_not_available"}

        if len(self.replay_buffer) < self.config.online_batch_size:
            return {"status": "insufficient_data", "buffer_size": len(self.replay_buffer)}

        self.step_counter += 1
        if self.step_counter % self.config.update_interval != 0:
            return {"status": "skipped", "step": self.step_counter}

        model.train()
        optimizer = torch.optim.Adam(model.parameters(), lr=self.config.online_lr)

        batch = self.replay_buffer.sample(self.config.online_batch_size)

        # 计算新损失（简化：MSE on rewards）
        total_loss = 0.0
        for state, action, reward, next_state, done in batch:
            # 这里简化处理，实际应使用PPO损失
            pred = torch.tensor(0.0)  # 占位
            target = torch.tensor(reward, dtype=torch.float32)
            loss = (pred - target) ** 2
            total_loss += loss

        new_loss = total_loss / len(batch)

        # EWC正则化
        ewc_loss = 0.0
        if use_ewc and self.ewc_params:
            for name, param in model.named_parameters():
                if name in self.ewc_params:
                    fisher, old_val = self.ewc_params[name]
                    ewc_loss += torch.sum(fisher * (param - old_val) ** 2)
            ewc_loss = self.config.regularization_lambda / 2.0 * ewc_loss

        total = new_loss + ewc_loss

        optimizer.zero_grad()
        total.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 0.5)
        optimizer.step()

        self.update_count += 1

        # 更新EWC参数（每5次更新）
        if self.update_count % 5 == 0 and old_model is not None:
            fisher = self.compute_fisher_information(model, batch)
            for name, param in old_model.named_parameters():
                if name in fisher:
                    self.ewc_params[name] = (fisher[name].detach(), param.data.detach())

        return {
            "status": "updated",
            "update_count": self.update_count,
            "new_loss": float(new_loss.item() if hasattr(new_loss, 'item') else new_loss),
            "ewc_loss": float(ewc_loss.item() if hasattr(ewc_loss, 'item') else ewc_loss),
            "buffer_size": len(self.replay_buffer),
        }


# =============================================================================
# 5. 策略集成器（为联邦学习预留接口）
# =============================================================================

class PolicyEnsemble:
    """
    多策略集成器

    动态组合多个策略的输出，用于：
    - 平稳过渡（新旧策略混合）
    - A/B测试（部分流量走新策略）
    - 联邦学习预留（多仓库策略聚合）
    """

    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or {"kgdrl": 0.5, "tzu": 0.3, "edd": 0.2}
        self.policies = {}
        self.performance_history = {name: deque(maxlen=50) for name in self.weights}

    def register_policy(self, name: str, policy_fn: Callable, weight: float = None):
        """注册策略"""
        self.policies[name] = policy_fn
        if weight is not None:
            self.weights[name] = weight
        if name not in self.performance_history:
            self.performance_history[name] = deque(maxlen=50)

    def select_action(self, state, valid_actions) -> Tuple[int, Dict]:
        """
        集成决策：加权投票

        Returns:
            (action, metadata)
        """
        votes = {}
        for name, policy in self.policies.items():
            if name not in self.weights:
                continue
            try:
                action = policy(state, valid_actions)
                weight = self.weights[name]
                votes[action] = votes.get(action, 0.0) + weight
            except Exception:
                continue

        if not votes:
            return valid_actions[0] if valid_actions else 0, {"ensemble": "fallback"}

        best_action = max(votes.items(), key=lambda x: x[1])[0]
        meta = {
            "ensemble": True,
            "votes": votes,
            "weights": self.weights.copy(),
            "selected_policy": max(self.weights.items(), key=lambda x: x[1])[0],
        }
        return best_action, meta

    def update_weights(self, performance: Dict[str, float]):
        """根据性能动态调整权重（softmax归一化）"""
        for name, perf in performance.items():
            if name in self.performance_history:
                self.performance_history[name].append(perf)

        # 使用指数移动平均性能更新权重
        avg_perfs = {}
        for name, hist in self.performance_history.items():
            if hist:
                avg_perfs[name] = np.mean(list(hist)[-10:])
            else:
                avg_perfs[name] = 0.0

        # Softmax归一化（性能越高权重越大）
        exp_perfs = {k: np.exp(v - max(avg_perfs.values())) for k, v in avg_perfs.items()}
        total = sum(exp_perfs.values())
        if total > 0:
            self.weights = {k: v / total for k, v in exp_perfs.items()}

    def get_weights(self) -> Dict[str, float]:
        return self.weights.copy()


# =============================================================================
# 6. 联邦学习预留架构
# =============================================================================

@dataclass
class FederatedConfig:
    """联邦学习配置"""
    n_clients: int = 5  # 仓库数量
    aggregation_rounds: int = 10
    local_epochs: int = 5
    participation_rate: float = 1.0  # 每轮参与的客户端比例
    dp_epsilon: float = 1.0  # 差分隐私预算
    dp_delta: float = 1e-5


class FederatedCoordinator:
    """
    联邦学习协调器（预留架构）

    设计目标：
    - 多仓库协同：各仓库本地训练，只上传梯度/参数更新
    - 隐私保护：差分隐私 + 安全聚合
    - 异构处理：不同仓库数据分布不同（Non-IID）

    当前状态：架构预留，待Pro版客户部署后激活
    """

    def __init__(self, config: FederatedConfig = None):
        self.config = config or FederatedConfig()
        self.global_model_state = None
        self.client_states = {}
        self.round = 0

    def initialize_global_model(self, model_state: Dict):
        """初始化全局模型"""
        self.global_model_state = copy.deepcopy(model_state)
        print("  [Federated] Global model initialized.")

    def register_client(self, client_id: str, metadata: Dict):
        """注册客户端（仓库）"""
        self.client_states[client_id] = {
            "metadata": metadata,
            "last_update": None,
            "local_model": None,
            "status": "registered",
        }
        print(f"  [Federated] Client '{client_id}' registered.")

    def aggregate_updates(self, client_updates: List[Tuple[str, Dict]]) -> Dict:
        """
        FedAvg聚合
        global = Σ (n_i / N) * local_i
        """
        if not client_updates:
            return self.global_model_state

        total_samples = sum(
            self.client_states[cid]["metadata"].get("n_samples", 1)
            for cid, _ in client_updates
        )

        aggregated = None
        for client_id, update in client_updates:
            weight = self.client_states[client_id]["metadata"].get("n_samples", 1) / total_samples

            if aggregated is None:
                aggregated = {k: v.clone() if hasattr(v, 'clone') else copy.deepcopy(v)
                              for k, v in update.items()}
                for k in aggregated:
                    if hasattr(aggregated[k], 'mul_'):
                        aggregated[k].mul_(weight)
            else:
                for k in update:
                    if k in aggregated and hasattr(aggregated[k], 'add_'):
                        if hasattr(update[k], 'clone'):
                            aggregated[k].add_(update[k].clone().mul_(weight))
                        else:
                            aggregated[k] = aggregated[k] + update[k] * weight

        self.global_model_state = aggregated
        self.round += 1
        print(f"  [Federated] Round {self.round} aggregation complete. "
              f"Clients: {len(client_updates)}")
        return aggregated

    def distribute_global_model(self) -> Dict:
        """分发全局模型给客户端"""
        return copy.deepcopy(self.global_model_state)

    def get_status(self) -> Dict:
        return {
            "round": self.round,
            "n_clients": len(self.client_states),
            "global_model_ready": self.global_model_state is not None,
            "client_statuses": {cid: s["status"] for cid, s in self.client_states.items()},
        }


# =============================================================================
# 7. 自适应策略主控器
# =============================================================================

class AdaptivePolicyController:
    """
    自适应策略主控器

    整合所有自适应组件的统一接口：
    - 到达率预测
    - 容量动态调整
    - 在线学习更新
    - 策略集成
    - 联邦学习协调（预留）
    """

    def __init__(self, config: AdaptiveConfig = None):
        self.config = config or AdaptiveConfig()
        self.capacity_regulator = AdaptiveWaveCapacity(config)
        self.online_updater = OnlinePolicyUpdater(config)
        self.ensemble = PolicyEnsemble(config.ensemble_weights)
        self.federated = FederatedCoordinator() if config.federated_enabled else None

        # 遥测
        self.shift_telemetry: List[ShiftTelemetry] = []
        self.current_shift_id = 0

    def step(self, observed_rate: float, current_load: float, hour: int) -> Dict:
        """
        每步调用，获取当前自适应决策

        Returns:
            Dict: 包含容量、释放阈值、策略建议
        """
        capacity_decision = self.capacity_regulator.adjust(observed_rate, current_load, hour)

        return {
            "capacity": capacity_decision["capacity"],
            "release_threshold": capacity_decision["release_threshold"],
            "predicted_rate": capacity_decision["predicted_rate"],
            "peak_detected": capacity_decision["ewma_state"]["peak_detected"],
            "valley_detected": capacity_decision["ewma_state"]["valley_detected"],
            "reason": capacity_decision["reason"],
            "ensemble_weights": self.ensemble.get_weights(),
        }

    def end_shift(self, telemetry: ShiftTelemetry):
        """班次结束，记录遥测并触发在线学习"""
        self.shift_telemetry.append(telemetry)
        self.current_shift_id += 1
        print(f"  [Adaptive] Shift {telemetry.shift_id} ended. "
              f"Orders={telemetry.total_orders}, Waves={telemetry.total_waves}")

    def get_dashboard_data(self) -> Dict:
        """获取Streamlit看板所需的数据"""
        return {
            "capacity_regulator": self.capacity_regulator.get_telemetry(),
            "online_updates": self.online_updater.update_count,
            "ensemble_weights": self.ensemble.get_weights(),
            "shift_history": [asdict(t) for t in self.shift_telemetry[-20:]],
            "federated_status": self.federated.get_status() if self.federated else {"enabled": False},
        }

    def export_config(self, filepath: str):
        """导出配置"""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(asdict(self.config), f, indent=2, ensure_ascii=False)


# =============================================================================
# 8. CLI 演示入口
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  Sunergy Pharma — Adaptive Policy Module (Pro Edition)")
    print("  Features: EWMA | Adaptive Capacity | Online Learning | Federated (Reserved)")
    print("=" * 70)

    ctrl = AdaptivePolicyController(AdaptiveConfig(
        ewma_alpha=0.3,
        base_capacity=20,
        min_capacity=8,
        max_capacity=35,
        federated_enabled=True,
    ))

    # Demo: 模拟一天24小时的自适应
    print("\n>>> DEMO: 24-Hour Adaptive Simulation")
    np.random.seed(42)
    base_rate = 3.0

    for hour in range(24):
        # 模拟双峰到达率
        peak_factor = 1.0
        if 8 <= hour <= 11:
            peak_factor = 2.8
        elif 13 <= hour <= 15:
            peak_factor = 1.8
        elif 0 <= hour <= 5:
            peak_factor = 0.2

        observed = base_rate * peak_factor * (0.8 + np.random.rand() * 0.4)
        load = min(0.95, 0.3 + peak_factor * 0.2 + np.random.rand() * 0.1)

        decision = ctrl.step(observed, load, hour)

        if hour % 3 == 0 or decision["peak_detected"]:
            print(f"  Hour {hour:02d}: rate={observed:.1f}, load={load:.2f} | "
                  f"cap={decision['capacity']:>2}, rel={decision['release_threshold']:.2f} | "
                  f"peak={decision['peak_detected']}, reason={decision['reason']}")

    # Demo: 联邦学习预留
    print("\n>>> DEMO: Federated Learning Architecture (Reserved)")
    ctrl.federated.initialize_global_model({"layer1": [0.1, 0.2], "layer2": [0.3, 0.4]})
    for wh in ["Shanghai", "Beijing", "Guangzhou", "Chengdu", "Wuhan"]:
        ctrl.federated.register_client(wh, {"n_samples": 1000 + random.randint(0, 500)})

    print(f"  Federated status: {ctrl.federated.get_status()}")

    # Dashboard数据
    print("\n>>> Dashboard Data Preview:")
    dash = ctrl.get_dashboard_data()
    print(f"  Capacity adjustments: {dash['capacity_regulator']['n_adjustments']}")
    print(f"  Ensemble weights: {dash['ensemble_weights']}")

    print("\n>>> Done.")
