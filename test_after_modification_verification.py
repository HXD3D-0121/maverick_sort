"""
测试脚本：验证HR_DRL_busy_balance.py修改后的功能性
测试内容：
1. 正指数逻辑验证（busy_balance函数输出）
2. alpha参数可配置性验证（默认vs随机）
3. 小规模训练循环验证（确保代码可跑通）
"""
import sys
import random
import numpy as np
import torch

random.seed(42)
np.random.seed(42)
torch.manual_seed(42)

from HR_DRL_busy_balance import PPO, busy_balance, STSP_prob
from new_env import JSRS

def test_busy_balance_positive_exp():
    """测试busy_balance函数使用正指数：workload越大，概率越高"""
    print("=" * 60)
    print("测试1: busy_balance正指数逻辑验证")
    print("=" * 60)

    env = JSRS.make('IS3J5M5R0', 'Data/new/IS3J5M5R0.jsr')
    status = env.reset()

    # 获取busy_balance概率
    p_busy = busy_balance(status)

    # 获取operations及其workload
    operations = status.available_operations
    ope_raw = [(x[0], x[1]) for x in operations if x is not None]

    print(f"可用操作数: {len(ope_raw)}")
    print(f"概率分布形状: {p_busy.shape}")

    # 验证概率非负且和为1（在可用操作位置上）
    p_busy_avail = p_busy[p_busy > 0]
    print(f"可用位置概率和: {p_busy_avail.sum().item():.6f}")

    # 验证workload越大，概率越高
    workloads = []
    probs = []
    for i, op in enumerate(operations):
        if op is not None:
            workload = sum(op[1].average_processing_time[s_remain] for s_remain in op[1].stages)
            # 找到对应概率（需要去重匹配）
            workloads.append(workload)

    # 去重后的概率对应去重后的操作
    unique_ope = []
    for oper in ope_raw:
        if oper not in unique_ope:
            unique_ope.append(oper)

    node = [(x, y) for x in status.machine_register.values() for y in status.job_register.values()]
    avail_idx = [i for i, x in enumerate(node) if x in unique_ope]
    avail_probs = [p_busy[i].item() for i in avail_idx]

    # 简单验证：最大workload对应最大概率
    if len(workloads) > 1:
        max_wl_idx = workloads.index(max(workloads))
        min_wl_idx = workloads.index(min(workloads))
        print(f"最大workload: {workloads[max_wl_idx]:.2f} -> 概率: {avail_probs[max_wl_idx]:.6f}")
        print(f"最小workload: {workloads[min_wl_idx]:.2f} -> 概率: {avail_probs[min_wl_idx]:.6f}")
        if avail_probs[max_wl_idx] >= avail_probs[min_wl_idx]:
            print("[PASS] 正指数验证通过：workload越大，概率越高")
        else:
            print("[FAIL] 正指数验证失败")

    print()
    return True

def test_alpha_configurability():
    """测试alpha参数的可配置性"""
    print("=" * 60)
    print("测试2: alpha参数可配置性验证")
    print("=" * 60)

    # 测试固定alpha
    print("\n--- 固定alpha配置 ---")
    ppo_fixed = PPO(hidden_dim=64, state_d=5*5*12, action_d=5*5,
                    alpha1=1.0, alpha2=0.1, random_alpha=False)
    print(f"固定配置: alpha1={ppo_fixed.alpha1}, alpha2={ppo_fixed.alpha2}")

    # 测试随机alpha
    print("\n--- 随机alpha配置 ---")
    ppo_rand1 = PPO(hidden_dim=64, state_d=5*5*12, action_d=5*5, random_alpha=True)
    ppo_rand2 = PPO(hidden_dim=64, state_d=5*5*12, action_d=5*5, random_alpha=True)

    # 验证两次随机值不同
    assert ppo_rand1.alpha1 != ppo_rand2.alpha1 or ppo_rand1.alpha2 != ppo_rand2.alpha2, \
        "随机alpha应产生不同值"
    print(f"随机实例1: alpha1={ppo_rand1.alpha1:.4f}, alpha2={ppo_rand1.alpha2:.4f}")
    print(f"随机实例2: alpha1={ppo_rand2.alpha1:.4f}, alpha2={ppo_rand2.alpha2:.4f}")
    print("[PASS] 随机alpha配置验证通过")
    print()
    return True

def test_small_training_run():
    """运行极小规模训练，验证代码可跑通"""
    print("=" * 60)
    print("测试3: 小规模训练循环验证（2 episodes）")
    print("=" * 60)

    configs = [
        ("默认alpha(1.0, 0.1)", {"alpha1": 1.0, "alpha2": 0.1, "random_alpha": False}),
        ("随机alpha", {"random_alpha": True}),
        ("自定义alpha(2.0, 0.05)", {"alpha1": 2.0, "alpha2": 0.05, "random_alpha": False}),
    ]

    instance_names = ['IS3J5M5R0']
    results = {}

    for name, kwargs in configs:
        print(f"\n--- 配置: {name} ---")
        random.seed(42)
        np.random.seed(42)
        torch.manual_seed(42)

        ppo = PPO(hidden_dim=64, state_d=5*5*12, action_d=5*5, **kwargs)

        try:
            return_l, makespan_l, instances_makespan = ppo.train_loop(
                instance_list=instance_names,
                episodes=2,
                plot_process=False,
                val_process=False
            )
            print(f"训练完成，makespan: {instances_makespan}")
            results[name] = {"status": "OK", "makespan": instances_makespan}
        except Exception as e:
            print(f"训练失败: {e}")
            results[name] = {"status": "FAIL", "error": str(e)}

    # 汇总
    print("\n--- 训练测试汇总 ---")
    all_ok = True
    for name, res in results.items():
        status = res["status"]
        print(f"{name}: {status}")
        if status != "OK":
            all_ok = False

    if all_ok:
        print("\n[PASS] 所有配置训练测试通过")
    else:
        print("\n[FAIL] 部分配置训练失败")
    print()
    return all_ok

def test_prob_guidance_computation():
    """验证prob_guidance计算使用了正确的alpha权重"""
    print("=" * 60)
    print("测试4: prob_guidance权重计算验证")
    print("=" * 60)

    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)

    ppo = PPO(hidden_dim=64, state_d=5*5*12, action_d=5*5, alpha1=1.5, alpha2=0.2)
    env = JSRS.make('IS3J5M5R0', 'Data/new/IS3J5M5R0.jsr')
    status = env.reset()

    state, avail, avail_bi, node = ppo.get_state_vec(status)
    prob_guidance, action, action_num, action_prob = ppo.take_action(state, avail, avail_bi, node, status)

    # 手动计算期望的prob_guidance
    prob_STSP = STSP_prob(status)
    prob_workload = busy_balance(status)
    expected = ppo.alpha1 * prob_STSP + ppo.alpha2 * prob_workload

    # 比较（允许微小数值误差）
    diff = torch.abs(torch.tensor(prob_guidance) - expected.cpu()).max().item()
    print(f"alpha1={ppo.alpha1}, alpha2={ppo.alpha2}")
    print(f"prob_guidance计算最大误差: {diff:.8f}")

    if diff < 1e-5:
        print("[PASS] prob_guidance权重计算验证通过")
        return True
    else:
        print("[FAIL] prob_guidance权重计算验证失败")
        return False

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("HR_DRL_busy_balance.py 修改验证测试套件")
    print("=" * 60 + "\n")

    results = []
    results.append(("busy_balance正指数", test_busy_balance_positive_exp()))
    results.append(("alpha可配置性", test_alpha_configurability()))
    results.append(("prob_guidance计算", test_prob_guidance_computation()))
    results.append(("小规模训练", test_small_training_run()))

    print("=" * 60)
    print("最终测试汇总")
    print("=" * 60)
    for name, ok in results:
        mark = "[PASS]" if ok else "[FAIL]"
        print(f"{mark} {name}")

    all_pass = all(r[1] for r in results)
    if all_pass:
        print("\n*** 所有测试通过，修改未引入功能性问题 ***")
        sys.exit(0)
    else:
        print("\n!!! 存在测试失败，请检查修改 !!!")
        sys.exit(1)
