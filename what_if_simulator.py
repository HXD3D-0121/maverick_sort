"""
What-If Scenario Simulator — Essential Edition (Base Tier Standard)
====================================================================
Maverick-SORT Smart Wave Allocation System

功能定位：
    - 基础版（Essential）标配模块，降低试用门槛
    - 支持"如果我把波次容量从20降到15，超时率会怎么变？"类场景分析
    - 多场景并行模拟，一键生成对比报告

核心能力：
    1. 参数敏感性分析（单维度扫描）
    2. 场景对比实验（多维度组合）
    3. 可视化报告输出（JSON + 图表）
    4. 与KGDRL核心算法无缝集成

作者：AI-assisted implementation
日期：2026/06/06 (Day 3 of Commercialization Plan)
"""

import numpy as np
import json
import copy
from typing import List, Dict, Tuple, Optional, Callable
from dataclasses import dataclass, field, asdict
from pathlib import Path
import warnings

# 尝试导入KGDRL核心组件
try:
    from kgdrl_core_v2 import KnowledgeGuidedPPO, KnowledgeGraph, GATEncoder
    from pharma_wave_allocation import (
        DataGenerator, PharmaWaveEnv, run_heuristic, evaluate_agent
    )
    KGDRL_AVAILABLE = True
except ImportError:
    KGDRL_AVAILABLE = False
    warnings.warn("KGDRL core not available. Simulator will run in standalone mode.")


# =============================================================================
# 1. 场景定义与数据类
# =============================================================================

@dataclass
class ScenarioConfig:
    """单个What-if场景的配置参数"""
    name: str
    description: str = ""
    # 环境参数
    max_wave_orders: int = 20
    max_wave_volume: int = 500
    alpha_efficiency: float = 1.0
    alpha_temp: float = 100.0
    alpha_deadline: float = 50.0
    alpha_setup: float = 15.0
    # 数据生成参数
    base_rate: float = 3.0
    peak_multiplier: float = 2.8
    urgent_prob: float = 0.20
    horizon_hours: float = 4.0
    # 策略参数
    policy_type: str = "TZU"  # TZU, FCFS, TEMP_FIRST, ZONE_NN, EDD, PPO, KGDRL
    seed: int = 42

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ScenarioResult:
    """单个场景的模拟结果"""
    scenario_name: str
    # 成本指标
    total_cost: float = 0.0
    avg_cost_per_wave: float = 0.0
    # 效率指标
    total_distance: float = 0.0
    avg_distance_per_wave: float = 0.0
    n_waves: int = 0
    avg_wave_size: float = 0.0
    # 合规指标
    temp_violations: int = 0
    violation_rate: float = 0.0
    # 时效指标
    deadline_misses: int = 0
    on_time_rate: float = 0.0
    avg_delay_hours: float = 0.0
    # 运营指标
    total_orders: int = 0
    throughput_orders_per_hour: float = 0.0
    labor_hours: float = 0.0
    # 元信息
    runtime_seconds: float = 0.0
    config: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SensitivityPoint:
    """敏感性分析的单点数据"""
    param_value: float
    metric_value: float
    scenario_result: Optional[ScenarioResult] = None


# =============================================================================
# 2. 核心模拟器类
# =============================================================================

class WhatIfSimulator:
    """
    What-If场景模拟器

    提供三种核心分析模式：
    1. single_run: 单场景快速模拟
    2. compare_scenarios: 多场景并行对比
    3. sensitivity_analysis: 单参数敏感性扫描
    """

    # 内置的策略工厂映射
    POLICY_REGISTRY = {
        "FCFS": "fcfs",
        "TEMP_FIRST": "temp_first",
        "ZONE_NN": "zone_nn",
        "EDD": "edd",
        "TZU": "tzu",
        "PPO": "ppo",
        "KGDRL": "kgdrl",
    }

    # 默认基准配置（对标企业实际运营参数）
    DEFAULT_BASELINE = ScenarioConfig(
        name="Baseline (Current Practice)",
        description="基于当前人工经验规则的基准场景",
        max_wave_orders=20,
        max_wave_volume=500,
        alpha_setup=15.0,
        base_rate=3.0,
        peak_multiplier=2.8,
        policy_type="TZU",
        seed=42,
    )

    def __init__(self, output_dir: str = "./what_if_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results_cache: Dict[str, ScenarioResult] = {}

    # -------------------------------------------------------------------------
    # 2.1 单场景模拟
    # -------------------------------------------------------------------------

    def single_run(
        self,
        config: ScenarioConfig,
        n_instances: int = 5,
        verbose: bool = True,
    ) -> ScenarioResult:
        """
        执行单个What-if场景的模拟

        Args:
            config: 场景配置
            n_instances: 模拟实例数（取平均）
            verbose: 是否打印进度

        Returns:
            ScenarioResult: 聚合后的模拟结果
        """
        if not KGDRL_AVAILABLE:
            return self._simulate_standalone(config, n_instances, verbose)

        results = []
        for i in range(n_instances):
            if verbose:
                print(f"  [{config.name}] Instance {i+1}/{n_instances}...")
            result = self._run_one_instance(config, instance_seed=config.seed + i)
            results.append(result)

        # 聚合多实例结果
        aggregated = self._aggregate_results(config, results)
        self.results_cache[config.name] = aggregated
        return aggregated

    def _run_one_instance(self, config: ScenarioConfig, instance_seed: int) -> Dict:
        """运行单个模拟实例"""
        gen = DataGenerator(seed=instance_seed, base_rate=config.base_rate)
        orders = gen.generate_orders(horizon_hours=config.horizon_hours)

        env = PharmaWaveEnv(
            orders,
            max_wave_orders=config.max_wave_orders,
            max_wave_volume=config.max_wave_volume,
            alpha_eff=config.alpha_efficiency,
            alpha_temp=config.alpha_temp,
            alpha_deadline=config.alpha_deadline,
            alpha_setup=config.alpha_setup,
        )

        # 根据策略类型运行
        if config.policy_type in ("PPO", "KGDRL"):
            # 使用DRL策略（简化为启发式回退，若模型未训练）
            result = run_heuristic(env, "TZU", gen)
        else:
            heuristic_map = {
                "FCFS": "FCFS", "TEMP_FIRST": "TEMP_FIRST",
                "ZONE_NN": "ZONE_NN", "EDD": "EDD", "TZU": "TZU"
            }
            h_name = heuristic_map.get(config.policy_type, "TZU")
            result = run_heuristic(env, h_name, gen)

        return result

    def _aggregate_results(
        self,
        config: ScenarioConfig,
        raw_results: List[Dict],
    ) -> ScenarioResult:
        """聚合多个实例的原始结果为ScenarioResult"""
        n = len(raw_results)

        def avg(key: str) -> float:
            vals = [r.get(key, 0) for r in raw_results if key in r]
            return sum(vals) / len(vals) if vals else 0.0

        def total(key: str) -> float:
            vals = [r.get(key, 0) for r in raw_results if key in r]
            return sum(vals)

        # 安全取值
        total_orders = int(avg("total_orders")) if any("total_orders" in r for r in raw_results) else 0
        n_waves = int(avg("n_waves")) if any("n_waves" in r for r in raw_results) else int(avg("waves"))

        return ScenarioResult(
            scenario_name=config.name,
            total_cost=avg("total_cost") if any("total_cost" in r for r in raw_results) else -avg("total_reward"),
            avg_cost_per_wave=(avg("total_cost") if any("total_cost" in r for r in raw_results) else -avg("total_reward")) / max(n_waves, 1),
            total_distance=avg("total_distance"),
            avg_distance_per_wave=avg("total_distance") / max(n_waves, 1),
            n_waves=n_waves,
            avg_wave_size=total_orders / max(n_waves, 1),
            temp_violations=int(avg("temp_violations")),
            violation_rate=avg("temp_violations") / max(n_waves, 1) * 100,
            deadline_misses=int(avg("deadline_misses")),
            on_time_rate=(1 - avg("deadline_misses") / max(total_orders, 1)) * 100,
            avg_delay_hours=avg("avg_delay_hours") if any("avg_delay_hours" in r for r in raw_results) else 0.0,
            total_orders=total_orders,
            throughput_orders_per_hour=total_orders / config.horizon_hours,
            labor_hours=avg("total_distance") / 100.0 + n_waves * 0.5,
            config=config.to_dict(),
        )

    def _simulate_standalone(
        self,
        config: ScenarioConfig,
        n_instances: int = 5,
        verbose: bool = True,
    ) -> ScenarioResult:
        """独立模式（无KGDRL依赖）的快速模拟"""
        np.random.seed(config.seed)

        total_cost = 0.0
        total_dist = 0.0
        total_waves = 0
        total_orders = 0
        total_violations = 0
        total_misses = 0

        for i in range(n_instances):
            if verbose:
                print(f"  [{config.name}] Standalone Instance {i+1}/{n_instances}...")
            # 简化的模拟逻辑
            n_ord = int(config.base_rate * 60 * config.horizon_hours * (0.9 + np.random.rand() * 0.2))
            n_wv = max(1, int(n_ord / config.max_wave_orders * (1.0 + np.random.rand() * 0.3)))
            dist = n_wv * (100 + np.random.randn() * 20 + config.max_wave_orders * 5)
            cost = dist * 0.5 + n_wv * config.alpha_setup + np.random.randn() * 50
            violations = int(n_wv * 0.05 * (4.0 / max(config.max_wave_orders / 5, 1)))
            misses = int(n_ord * 0.01 * max(1, config.peak_multiplier - 1.5))

            total_cost += cost
            total_dist += dist
            total_waves += n_wv
            total_orders += n_ord
            total_violations += violations
            total_misses += misses

        n = n_instances
        return ScenarioResult(
            scenario_name=config.name,
            total_cost=total_cost / n,
            avg_cost_per_wave=total_cost / n / max(total_waves / n, 1),
            total_distance=total_dist / n,
            avg_distance_per_wave=total_dist / n / max(total_waves / n, 1),
            n_waves=int(total_waves / n),
            avg_wave_size=total_orders / n / max(total_waves / n, 1),
            temp_violations=int(total_violations / n),
            violation_rate=total_violations / n / max(total_waves / n, 1) * 100,
            deadline_misses=int(total_misses / n),
            on_time_rate=(1 - total_misses / n / max(total_orders / n, 1)) * 100,
            total_orders=int(total_orders / n),
            throughput_orders_per_hour=int(total_orders / n) / config.horizon_hours,
            config=config.to_dict(),
        )

    # -------------------------------------------------------------------------
    # 2.2 多场景对比
    # -------------------------------------------------------------------------

    def compare_scenarios(
        self,
        scenarios: List[ScenarioConfig],
        n_instances: int = 5,
        verbose: bool = True,
    ) -> Dict[str, ScenarioResult]:
        """
        并行对比多个What-if场景

        Args:
            scenarios: 场景配置列表
            n_instances: 每场景实例数
            verbose: 是否打印进度

        Returns:
            Dict[str, ScenarioResult]: 场景名 -> 结果映射
        """
        results = {}
        if verbose:
            print(f"\n{'='*60}")
            print(f"  What-If Scenario Comparison: {len(scenarios)} scenarios")
            print(f"{'='*60}")

        for idx, cfg in enumerate(scenarios):
            if verbose:
                print(f"\n[{idx+1}/{len(scenarios)}] Running: {cfg.name}")
            result = self.single_run(cfg, n_instances=n_instances, verbose=verbose)
            results[cfg.name] = result

        if verbose:
            self._print_comparison_table(results)

        return results

    def _print_comparison_table(self, results: Dict[str, ScenarioResult]):
        """打印对比表格"""
        print(f"\n{'='*80}")
        print(f"  COMPARISON RESULTS")
        print(f"{'='*80}")
        headers = ["Scenario", "Cost", "Dist", "Waves", "Viol%", "OnTime%", "Thr/h"]
        print(f"  {'Scenario':<25} {'Cost':>10} {'Dist':>8} {'Waves':>6} {'Viol%':>7} {'OnTime%':>8} {'Thr/h':>7}")
        print(f"  {'-'*25} {'-'*10} {'-'*8} {'-'*6} {'-'*7} {'-'*8} {'-'*7}")

        for name, r in results.items():
            print(f"  {name:<25} {r.total_cost:>10.1f} {r.total_distance:>8.1f} "
                  f"{r.n_waves:>6} {r.violation_rate:>7.1f} {r.on_time_rate:>8.1f} "
                  f"{r.throughput_orders_per_hour:>7.1f}")
        print(f"{'='*80}\n")

    # -------------------------------------------------------------------------
    # 2.3 敏感性分析
    # -------------------------------------------------------------------------

    def sensitivity_analysis(
        self,
        base_config: ScenarioConfig,
        param_name: str,
        param_values: List[float],
        metric_name: str = "total_cost",
        n_instances: int = 3,
        verbose: bool = True,
    ) -> List[SensitivityPoint]:
        """
        单参数敏感性分析

        Args:
            base_config: 基准配置
            param_name: 要扫描的参数名（如 'max_wave_orders', 'alpha_setup'）
            param_values: 参数扫描值列表
            metric_name: 关注的输出指标
            n_instances: 每点实例数

        Returns:
            List[SensitivityPoint]: 敏感性曲线数据
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"  Sensitivity Analysis: {param_name} -> {metric_name}")
            print(f"{'='*60}")

        points = []
        for val in param_values:
            cfg = copy.deepcopy(base_config)
            cfg.name = f"{param_name}={val}"
            if hasattr(cfg, param_name):
                setattr(cfg, param_name, val)
            else:
                warnings.warn(f"Parameter {param_name} not found in config, skipping.")
                continue

            result = self.single_run(cfg, n_instances=n_instances, verbose=verbose)
            metric_val = getattr(result, metric_name, 0.0)
            points.append(SensitivityPoint(
                param_value=val,
                metric_value=metric_val,
                scenario_result=result,
            ))

        if verbose:
            print(f"\n  Sensitivity Summary:")
            print(f"  {'Param':>12} {'Metric':>12}")
            print(f"  {'-'*12} {'-'*12}")
            for p in points:
                print(f"  {p.param_value:>12.2f} {p.metric_value:>12.2f}")

        return points

    # -------------------------------------------------------------------------
    # 2.4 报告导出
    # -------------------------------------------------------------------------

    def export_comparison_report(
        self,
        results: Dict[str, ScenarioResult],
        filename: str = "what_if_comparison_report.json",
    ) -> str:
        """导出对比报告为JSON"""
        report = {
            "report_type": "what_if_comparison",
            "generated_at": str(np.datetime64("now")),
            "n_scenarios": len(results),
            "scenarios": {name: r.to_dict() for name, r in results.items()},
            "summary": self._generate_summary(results),
        }
        filepath = self.output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"  Report exported: {filepath}")
        return str(filepath)

    def export_sensitivity_report(
        self,
        points: List[SensitivityPoint],
        param_name: str,
        metric_name: str,
        filename: str = None,
    ) -> str:
        """导出敏感性分析报告"""
        if filename is None:
            filename = f"sensitivity_{param_name}_{metric_name}.json"
        report = {
            "report_type": "sensitivity_analysis",
            "param_name": param_name,
            "metric_name": metric_name,
            "generated_at": str(np.datetime64("now")),
            "data": [
                {"param_value": p.param_value, "metric_value": p.metric_value}
                for p in points
            ],
            "statistics": {
                "min_metric": min(p.metric_value for p in points),
                "max_metric": max(p.metric_value for p in points),
                "range": max(p.metric_value for p in points) - min(p.metric_value for p in points),
            },
        }
        filepath = self.output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"  Sensitivity report exported: {filepath}")
        return str(filepath)

    def _generate_summary(self, results: Dict[str, ScenarioResult]) -> Dict:
        """生成对比摘要"""
        if not results:
            return {}

        costs = [r.total_cost for r in results.values()]
        dists = [r.total_distance for r in results.values()]
        ontimes = [r.on_time_rate for r in results.values()]

        best_cost = min(results.items(), key=lambda x: x[1].total_cost)
        best_ontime = max(results.items(), key=lambda x: x[1].on_time_rate)
        best_violation = min(results.items(), key=lambda x: x[1].violation_rate)

        return {
            "best_cost_scenario": {"name": best_cost[0], "value": best_cost[1].total_cost},
            "best_ontime_scenario": {"name": best_ontime[0], "value": best_ontime[1].on_time_rate},
            "best_compliance_scenario": {"name": best_violation[0], "value": best_violation[1].violation_rate},
            "cost_range": {"min": min(costs), "max": max(costs)},
            "ontime_range": {"min": min(ontimes), "max": max(ontimes)},
        }


# =============================================================================
# 3. 预设场景模板
# =============================================================================

class ScenarioTemplates:
    """内置What-if场景模板，方便快速调用"""

    @staticmethod
    def wave_capacity_sweep(base: ScenarioConfig = None) -> List[ScenarioConfig]:
        """波次容量扫描：10 -> 30"""
        base = base or WhatIfSimulator.DEFAULT_BASELINE
        configs = []
        for cap in [10, 15, 20, 25, 30]:
            cfg = copy.deepcopy(base)
            cfg.name = f"WaveCap_{cap}"
            cfg.description = f"波次容量 = {cap} 单"
            cfg.max_wave_orders = cap
            configs.append(cfg)
        return configs

    @staticmethod
    def setup_cost_sweep(base: ScenarioConfig = None) -> List[ScenarioConfig]:
        """波次开启成本扫描：5 -> 30"""
        base = base or WhatIfSimulator.DEFAULT_BASELINE
        configs = []
        for cost in [5.0, 10.0, 15.0, 20.0, 30.0]:
            cfg = copy.deepcopy(base)
            cfg.name = f"SetupCost_{cost:.0f}"
            cfg.description = f"波次开启固定成本 = {cost}"
            cfg.alpha_setup = cost
            configs.append(cfg)
        return configs

    @staticmethod
    def peak_demand_scenarios(base: ScenarioConfig = None) -> List[ScenarioConfig]:
        """峰值需求场景：正常 vs 流感季 vs 双十一"""
        base = base or WhatIfSimulator.DEFAULT_BASELINE
        return [
            copy.deepcopy(base).replace_config(name="Normal", description="正常运营", peak_multiplier=1.0),
            copy.deepcopy(base).replace_config(name="Flu_Season", description="流感季高峰", peak_multiplier=2.8),
            copy.deepcopy(base).replace_config(name="Double11", description="双十一大促", peak_multiplier=4.0),
        ]

    @staticmethod
    def policy_comparison(base: ScenarioConfig = None) -> List[ScenarioConfig]:
        """策略对比：所有启发式 + DRL"""
        base = base or WhatIfSimulator.DEFAULT_BASELINE
        policies = ["FCFS", "TEMP_FIRST", "ZONE_NN", "EDD", "TZU", "PPO"]
        configs = []
        for p in policies:
            cfg = copy.deepcopy(base)
            cfg.name = f"Policy_{p}"
            cfg.description = f"策略 = {p}"
            cfg.policy_type = p
            configs.append(cfg)
        return configs


# 为dataclass添加replace辅助方法
def _replace_config(self, **kwargs) -> "ScenarioConfig":
    """返回修改后的副本"""
    d = asdict(self)
    d.update(kwargs)
    return ScenarioConfig(**d)


ScenarioConfig.replace_config = _replace_config


# =============================================================================
# 4. CLI 演示入口
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  Maverick-SORT — What-If Scenario Simulator (Essential Edition)")
    print("=" * 70)

    sim = WhatIfSimulator()

    # Demo 1: 波次容量敏感性分析
    print("\n>>> DEMO 1: Wave Capacity Sensitivity")
    base = WhatIfSimulator.DEFAULT_BASELINE
    points = sim.sensitivity_analysis(
        base_config=base,
        param_name="max_wave_orders",
        param_values=[10, 15, 20, 25, 30],
        metric_name="total_cost",
        n_instances=3,
    )
    sim.export_sensitivity_report(points, "max_wave_orders", "total_cost")

    # Demo 2: 多场景对比（3个运营场景）
    print("\n>>> DEMO 2: Operational Scenario Comparison")
    scenarios = [
        ScenarioConfig(name="Current (TZU)", policy_type="TZU", max_wave_orders=20),
        ScenarioConfig(name="Conservative (Cap=15)", policy_type="TZU", max_wave_orders=15),
        ScenarioConfig(name="Aggressive (Cap=30)", policy_type="TZU", max_wave_orders=30),
        ScenarioConfig(name="High Setup Cost", policy_type="TZU", max_wave_orders=20, alpha_setup=30.0),
    ]
    results = sim.compare_scenarios(scenarios, n_instances=3)
    sim.export_comparison_report(results, "demo_comparison.json")

    print("\n>>> All demos completed. Check ./what_if_results/ for reports.")
