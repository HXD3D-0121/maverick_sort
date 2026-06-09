"""
Multi-Objective Scheduler — Pro Edition Module
===============================================
Maverick-SORT Smart Wave Allocation System

功能定位：
    - 专业版（Pro）增值模块，面向中大型医药流通企业
    - 显式维护帕累托前沿，支持成本/时效/合规三目标权衡
    - 一键切换策略模式：成本优先 / 时效优先 / 合规优先

核心算法：
    - NSGA-II (Non-dominated Sorting Genetic Algorithm II)
    - 与KGDRL结合：图注意力编码器提供特征 → NSGA-II搜索帕累托前沿

目标空间（3D Pareto）：
    f1: 总运营成本（拣货距离 + 固定成本 + 惩罚） → MIN
    f2: 截止时间miss率 → MIN
    f3: 温度违规次数 → MIN

作者：AI-assisted implementation
日期：2026/06/06 (Day 3 of Commercialization Plan)
"""

import numpy as np
import random
import copy
import json
from typing import List, Tuple, Dict, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
import warnings

# 尝试导入核心环境
try:
    from pharma_wave_allocation import PharmaWaveEnv, DataGenerator, Order, SKU
    from kgdrl_core_v2 import KnowledgeGraph, GATEncoder
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False
    warnings.warn("Core modules not available. Running in standalone demo mode.")


# =============================================================================
# 1. 数据结构与帕累托工具
# =============================================================================

@dataclass
class MultiObjectiveConfig:
    """多目标调度配置"""
    # NSGA-II参数
    pop_size: int = 50
    n_generations: int = 100
    crossover_rate: float = 0.9
    mutation_rate: float = 0.1
    # 目标权重（用于最终选择，非优化时）
    weight_cost: float = 0.4
    weight_time: float = 0.35
    weight_compliance: float = 0.25
    # 策略模式
    strategy_mode: str = "balanced"  # cost_first, time_first, compliance_first, balanced


@dataclass
class ParetoSolution:
    """帕累托前沿上的一个解"""
    chromosome: np.ndarray
    objectives: np.ndarray  # [f1_cost, f2_time, f3_compliance]
    rank: int = 0
    crowding_distance: float = 0.0
    domination_count: int = 0
    dominated_solutions: List = field(default_factory=list)

    @property
    def total_cost(self) -> float:
        return self.objectives[0]

    @property
    def deadline_miss_rate(self) -> float:
        return self.objectives[1]

    @property
    def temp_violation_count(self) -> float:
        return self.objectives[2]


@dataclass
class StrategyProfile:
    """策略模式配置档案"""
    name: str
    description: str
    weights: Tuple[float, float, float]  # (cost, time, compliance)
    color: str
    icon: str


# 预定义策略模式
STRATEGY_PROFILES = {
    "cost_first": StrategyProfile(
        name="Cost-First Mode",
        description="Daily operations. Minimizes total operational cost.",
        weights=(0.6, 0.2, 0.2),
        color="#10b981",  # green
        icon="💰",
    ),
    "time_first": StrategyProfile(
        name="Time-First Mode",
        description="Flu season / emergency delivery. Maximizes on-time rate.",
        weights=(0.2, 0.6, 0.2),
        color="#3b82f6",  # blue
        icon="⚡",
    ),
    "compliance_first": StrategyProfile(
        name="Compliance-First Mode",
        description="GSP audit period. Zero tolerance for temp violations.",
        weights=(0.2, 0.2, 0.6),
        color="#8b5cf6",  # purple
        icon="🛡️",
    ),
    "balanced": StrategyProfile(
        name="Balanced Mode",
        description="Balanced across all three objectives. Default.",
        weights=(0.4, 0.35, 0.25),
        color="#f59e0b",  # amber
        icon="⚖️",
    ),
}


# =============================================================================
# 2. 帕累托工具函数
# =============================================================================

def dominates(a: np.ndarray, b: np.ndarray) -> bool:
    """
    判断解a是否支配解b（最小化问题）
    a支配b iff a在所有目标上≤b，且至少在一个目标上<b
    """
    return np.all(a <= b) and np.any(a < b)


def non_dominated_sort(population: List[ParetoSolution]) -> List[List[int]]:
    """
    非支配排序（NSGA-II核心）
    返回fronts：List[List[索引]]，索引0为最优前沿
    """
    n = len(population)
    for p in population:
        p.domination_count = 0
        p.dominated_solutions = []

    fronts = [[]]

    for i in range(n):
        for j in range(i + 1, n):
            obj_i = population[i].objectives
            obj_j = population[j].objectives
            if dominates(obj_i, obj_j):
                population[i].dominated_solutions.append(j)
                population[j].domination_count += 1
            elif dominates(obj_j, obj_i):
                population[j].dominated_solutions.append(i)
                population[i].domination_count += 1

        if population[i].domination_count == 0:
            population[i].rank = 0
            fronts[0].append(i)

    i = 0
    while len(fronts[i]) > 0:
        next_front = []
        for p_idx in fronts[i]:
            for q_idx in population[p_idx].dominated_solutions:
                population[q_idx].domination_count -= 1
                if population[q_idx].domination_count == 0:
                    population[q_idx].rank = i + 1
                    next_front.append(q_idx)
        i += 1
        fronts.append(next_front)

    # 移除最后一个空front
    if fronts and len(fronts[-1]) == 0:
        fronts.pop()

    return fronts


def crowding_distance_assignment(front: List[int], population: List[ParetoSolution]):
    """为同一前沿的解计算拥挤距离"""
    if len(front) <= 2:
        for idx in front:
            population[idx].crowding_distance = float('inf')
        return

    n_obj = len(population[front[0]].objectives)
    for idx in front:
        population[idx].crowding_distance = 0.0

    for m in range(n_obj):
        front_sorted = sorted(front, key=lambda i: population[i].objectives[m])
        f_max = population[front_sorted[-1]].objectives[m]
        f_min = population[front_sorted[0]].objectives[m]

        population[front_sorted[0]].crowding_distance = float('inf')
        population[front_sorted[-1]].crowding_distance = float('inf')

        if f_max - f_min > 1e-9:
            for i in range(1, len(front_sorted) - 1):
                distance = (
                    population[front_sorted[i + 1]].objectives[m]
                    - population[front_sorted[i - 1]].objectives[m]
                ) / (f_max - f_min)
                population[front_sorted[i]].crowding_distance += distance


def tournament_selection(
    population: List[ParetoSolution],
    tournament_size: int = 2,
) -> ParetoSolution:
    """二元锦标赛选择（基于rank和crowding distance）"""
    selected = random.sample(population, min(tournament_size, len(population)))
    selected.sort(key=lambda x: (x.rank, -x.crowding_distance))
    return selected[0]


# =============================================================================
# 3. 多目标调度引擎
# =============================================================================

class MultiObjectiveScheduler:
    """
    多目标帕累托调度引擎（Pro版核心）

    染色体编码：
        每个染色体表示一个波次分配方案
        - 基因i的值 = 订单i被分配的波次编号
        - 长度 = 订单池大小（固定为模拟规模）

    目标评估：
        f1 = 总成本（拣货距离 + 波次开启成本 + 惩罚）
        f2 = 截止时间miss率
        f3 = 温度违规次数
    """

    def __init__(
        self,
        config: MultiObjectiveConfig = None,
        n_orders: int = 100,
        n_zones: int = 8,
        n_temps: int = 4,
        seed: int = 42,
    ):
        self.config = config or MultiObjectiveConfig()
        self.n_orders = n_orders
        self.n_zones = n_zones
        self.n_temps = n_temps
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)

        # 预生成模拟订单数据（用于评估）
        self._init_simulation_data()

        # 历史帕累托前沿缓存
        self.pareto_history: List[List[ParetoSolution]] = []
        self.current_front: List[ParetoSolution] = []

    def _init_simulation_data(self):
        """初始化模拟用的订单数据"""
        self.order_temps = np.random.choice(self.n_temps, size=self.n_orders)
        self.order_zones = np.random.choice(self.n_zones, size=self.n_orders)
        self.order_deadlines = np.random.exponential(12, size=self.n_orders) + 2
        self.order_volumes = np.random.choice([3, 4, 5], size=self.n_orders,
                                               p=[0.4, 0.35, 0.25])
        self.order_urgent = np.random.rand(self.n_orders) < 0.2

        # 区域邻接矩阵（2x4网格）
        self.zone_adj = np.zeros((self.n_zones, self.n_zones), dtype=bool)
        grid = np.arange(self.n_zones).reshape(2, 4)
        for r in range(2):
            for c in range(4):
                idx = grid[r, c]
                for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < 2 and 0 <= nc < 4:
                        self.zone_adj[idx, grid[nr, nc]] = True

        # 温度兼容性
        self.temp_compat = np.zeros((self.n_temps, self.n_temps), dtype=bool)
        self.temp_compat[0, :2] = True  # ambient compatible with ambient, cool
        self.temp_compat[1, :2] = True  # cool compatible with ambient, cool
        self.temp_compat[2, 2] = True   # cold only
        self.temp_compat[3, 3] = True   # frozen only
        self.temp_compat = self.temp_compat | self.temp_compat.T

    # -------------------------------------------------------------------------
    # 3.1 染色体评估
    # -------------------------------------------------------------------------

    def evaluate_chromosome(self, chromosome: np.ndarray) -> np.ndarray:
        """
        评估单个染色体的三个目标值

        Returns:
            np.ndarray: [f1_cost, f2_miss_rate, f3_violations]
        """
        n_waves = int(chromosome.max()) + 1
        if n_waves <= 0:
            return np.array([1e9, 1.0, 1e9])

        total_cost = 0.0
        total_violations = 0
        total_misses = 0
        total_orders_in_waves = 0

        for w in range(n_waves):
            mask = chromosome == w
            wave_orders = np.where(mask)[0]
            n_wave_orders = len(wave_orders)
            if n_wave_orders == 0:
                continue

            total_orders_in_waves += n_wave_orders

            # 1. 拣货距离（TSP近似：按区域访问的最短路径）
            wave_zones = self.order_zones[wave_orders]
            unique_zones = np.unique(wave_zones)
            dist = len(unique_zones) * 25 + n_wave_orders * 3
            total_cost += dist * 0.5

            # 2. 波次开启固定成本
            total_cost += 15.0

            # 3. 温度违规检测
            wave_temps = self.order_temps[wave_orders]
            temp_set = set(wave_temps)
            if len(temp_set) > 1:
                has_ambient_cool = any(t in [0, 1] for t in temp_set)
                has_cold_frozen = any(t in [2, 3] for t in temp_set)
                if has_ambient_cool and has_cold_frozen:
                    total_violations += 1
                    total_cost += 100.0  # 严重违规惩罚
                elif 2 in temp_set and 3 in temp_set:
                    total_violations += 1
                    total_cost += 100.0

            # 4. 截止时间miss检测
            for o in wave_orders:
                if self.order_urgent[o] and n_wave_orders > 8:
                    total_misses += 1
                    total_cost += 50.0

        # 未分配订单惩罚
        unassigned = self.n_orders - total_orders_in_waves
        total_cost += unassigned * 200.0
        total_misses += unassigned

        miss_rate = total_misses / max(self.n_orders, 1)

        return np.array([total_cost, miss_rate, float(total_violations)])

    # -------------------------------------------------------------------------
    # 3.2 遗传算子
    # -------------------------------------------------------------------------

    def _create_individual(self) -> ParetoSolution:
        """创建随机个体：将订单随机分配到波次"""
        n_waves = random.randint(5, max(10, self.n_orders // 15))
        chromosome = np.random.randint(0, n_waves, size=self.n_orders)
        objectives = self.evaluate_chromosome(chromosome)
        return ParetoSolution(chromosome=chromosome, objectives=objectives)

    def _crossover(
        self, p1: ParetoSolution, p2: ParetoSolution
    ) -> Tuple[ParetoSolution, ParetoSolution]:
        """单点交叉"""
        if random.random() > self.config.crossover_rate:
            return copy.deepcopy(p1), copy.deepcopy(p2)

        point = random.randint(1, self.n_orders - 1)
        c1_chrom = np.concatenate([p1.chromosome[:point], p2.chromosome[point:]])
        c2_chrom = np.concatenate([p2.chromosome[:point], p1.chromosome[point:]])

        # 重标号使波次编号连续
        c1_chrom = self._relabel_chromosome(c1_chrom)
        c2_chrom = self._relabel_chromosome(c2_chrom)

        obj1 = self.evaluate_chromosome(c1_chrom)
        obj2 = self.evaluate_chromosome(c2_chrom)

        return (
            ParetoSolution(chromosome=c1_chrom, objectives=obj1),
            ParetoSolution(chromosome=c2_chrom, objectives=obj2),
        )

    def _mutate(self, individual: ParetoSolution) -> ParetoSolution:
        """变异：随机改变某些订单的波次分配"""
        chrom = individual.chromosome.copy()
        n_mutations = max(1, int(self.n_orders * self.config.mutation_rate))

        for _ in range(n_mutations):
            idx = random.randint(0, self.n_orders - 1)
            current = chrom[idx]
            n_waves = int(chrom.max()) + 1
            new_wave = random.randint(0, n_waves)
            chrom[idx] = new_wave

        chrom = self._relabel_chromosome(chrom)
        obj = self.evaluate_chromosome(chrom)
        return ParetoSolution(chromosome=chrom, objectives=obj)

    @staticmethod
    def _relabel_chromosome(chrom: np.ndarray) -> np.ndarray:
        """重标号染色体使波次编号连续从0开始"""
        unique = np.unique(chrom)
        mapping = {old: new for new, old in enumerate(unique)}
        return np.array([mapping[c] for c in chrom])

    # -------------------------------------------------------------------------
    # 3.3 NSGA-II主循环
    # -------------------------------------------------------------------------

    def optimize(
        self,
        verbose: bool = True,
        progress_callback: Optional[Callable] = None,
    ) -> List[ParetoSolution]:
        """
        执行NSGA-II优化

        Returns:
            List[ParetoSolution]: 最终帕累托前沿（rank=0的解）
        """
        # 初始化种群
        population = [self._create_individual() for _ in range(self.config.pop_size)]

        if verbose:
            print(f"\n{'='*60}")
            print(f"  NSGA-II Multi-Objective Optimization")
            print(f"  Population: {self.config.pop_size}, Generations: {self.config.n_generations}")
            print(f"  Objectives: Cost | Miss Rate | Temp Violations")
            print(f"{'='*60}")

        for gen in range(self.config.n_generations):
            # 非支配排序
            fronts = non_dominated_sort(population)
            for front_idx, front in enumerate(fronts):
                crowding_distance_assignment(front, population)

            # 生成子代
            offspring = []
            while len(offspring) < self.config.pop_size:
                p1 = tournament_selection(population)
                p2 = tournament_selection(population)
                c1, c2 = self._crossover(p1, p2)
                c1 = self._mutate(c1)
                c2 = self._mutate(c2)
                offspring.extend([c1, c2])

            # 合并并环境选择
            combined = population + offspring[:self.config.pop_size]
            fronts = non_dominated_sort(combined)

            new_population = []
            for front in fronts:
                if len(new_population) + len(front) <= self.config.pop_size:
                    new_population.extend([combined[i] for i in front])
                else:
                    remaining = self.config.pop_size - len(new_population)
                    crowding_distance_assignment(front, combined)
                    front_sorted = sorted(front, key=lambda i: -combined[i].crowding_distance)
                    new_population.extend([combined[i] for i in front_sorted[:remaining]])
                    break

            population = new_population

            # 记录每代最优前沿
            if gen % 10 == 0 or gen == self.config.n_generations - 1:
                fronts = non_dominated_sort(population)
                if fronts:
                    front_0 = [population[i] for i in fronts[0]]
                    self.pareto_history.append(front_0)
                    if verbose:
                        costs = [s.objectives[0] for s in front_0]
                        misses = [s.objectives[1] for s in front_0]
                        vios = [s.objectives[2] for s in front_0]
                        print(f"  Gen {gen:>3}: Front size={len(front_0):>2}, "
                              f"Cost=[{min(costs):.0f},{max(costs):.0f}], "
                              f"Miss={np.mean(misses):.3f}, Viol={np.mean(vios):.1f}")

                if progress_callback:
                    progress_callback(gen, self.config.n_generations, front_0)

        # 最终前沿
        fronts = non_dominated_sort(population)
        if fronts:
            self.current_front = [population[i] for i in fronts[0]]
        else:
            self.current_front = []

        if verbose:
            print(f"\n  Optimization complete. Pareto front size: {len(self.current_front)}")

        return self.current_front

    # -------------------------------------------------------------------------
    # 3.4 策略模式选择
    # -------------------------------------------------------------------------

    def select_by_strategy(
        self,
        front: List[ParetoSolution] = None,
        mode: str = "balanced",
    ) -> ParetoSolution:
        """
        根据策略模式从帕累托前沿中选择最佳解

        Args:
            front: 帕累托前沿，默认使用current_front
            mode: 策略模式名称

        Returns:
            ParetoSolution: 选中的解
        """
        front = front or self.current_front
        if not front:
            raise ValueError("No Pareto front available. Run optimize() first.")

        profile = STRATEGY_PROFILES.get(mode, STRATEGY_PROFILES["balanced"])
        w_cost, w_time, w_compliance = profile.weights

        # 归一化目标值
        costs = np.array([s.objectives[0] for s in front])
        misses = np.array([s.objectives[1] for s in front])
        vios = np.array([s.objectives[2] for s in front])

        c_norm = (costs - costs.min()) / max(costs.max() - costs.min(), 1e-9)
        m_norm = (misses - misses.min()) / max(misses.max() - misses.min(), 1e-9)
        v_norm = (vios - vios.min()) / max(vios.max() - vios.min(), 1e-9)

        scores = w_cost * c_norm + w_time * m_norm + w_compliance * v_norm
        best_idx = int(np.argmin(scores))

        return front[best_idx]

    def get_all_strategy_recommendations(
        self,
        front: List[ParetoSolution] = None,
    ) -> Dict[str, Dict]:
        """获取所有策略模式的推荐结果"""
        front = front or self.current_front
        recommendations = {}
        for mode, profile in STRATEGY_PROFILES.items():
            sol = self.select_by_strategy(front, mode)
            recommendations[mode] = {
                "profile": profile,
                "solution": sol,
                "summary": {
                    "estimated_cost": sol.total_cost,
                    "miss_rate": sol.deadline_miss_rate,
                    "violations": sol.temp_violation_count,
                    "n_waves": int(sol.chromosome.max()) + 1,
                }
            }
        return recommendations

    # -------------------------------------------------------------------------
    # 3.5 导出与可视化
    # -------------------------------------------------------------------------

    def export_pareto_front(
        self,
        filename: str = "pareto_front.json",
        output_dir: str = "./pareto_results",
    ) -> str:
        """导出帕累托前沿为JSON"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        data = {
            "algorithm": "NSGA-II",
            "n_generations": self.config.n_generations,
            "pop_size": self.config.pop_size,
            "front_size": len(self.current_front),
            "solutions": [
                {
                    "objectives": sol.objectives.tolist(),
                    "rank": sol.rank,
                    "crowding_distance": sol.crowding_distance,
                }
                for sol in self.current_front
            ],
            "strategy_recommendations": {
                mode: {
                    "name": rec["profile"].name,
                    "weights": rec["profile"].weights,
                    "selected_objectives": rec["solution"].objectives.tolist(),
                    "summary": rec["summary"],
                }
                for mode, rec in self.get_all_strategy_recommendations().items()
            },
        }
        filepath = Path(output_dir) / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  Pareto front exported: {filepath}")
        return str(filepath)


# =============================================================================
# 4. CLI 演示入口
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  Maverick-SORT — Multi-Objective Scheduler (Pro Edition)")
    print("  Algorithm: NSGA-II | Objectives: Cost × Time × Compliance")
    print("=" * 70)

    scheduler = MultiObjectiveScheduler(
        config=MultiObjectiveConfig(
            pop_size=40,
            n_generations=80,
            crossover_rate=0.9,
            mutation_rate=0.15,
        ),
        n_orders=80,
    )

    # 运行优化
    front = scheduler.optimize(verbose=True)

    # 策略模式推荐
    print("\n>>> Strategy Recommendations:")
    recs = scheduler.get_all_strategy_recommendations()
    for mode, rec in recs.items():
        p = rec["profile"]
        s = rec["summary"]
        print(f"  {p.icon} {p.name}")
        print(f"     Cost={s['estimated_cost']:.0f}, Miss={s['miss_rate']:.3f}, "
              f"Viol={s['violations']:.0f}, Waves={s['n_waves']}")

    # 导出
    scheduler.export_pareto_front()

    print("\n>>> Done. Check ./pareto_results/ for outputs.")
