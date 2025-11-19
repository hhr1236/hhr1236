"""
最优改向角选择 - 使用示例

这个文件展示了如何使用 optimal_angle_selection 模块来选择最优的改向角度。
包含完整的示例代码和不同策略的对比。

使用步骤:
1. 先使用原有代码计算所有安全的改向角度集合
2. 调用本模块的函数选择最优角度
3. 根据实际情况选择合适的策略
"""

import numpy as np
from math import pi
from numba import typed
from optimal_angle_selection import (
    select_optimal_angle,
    compare_all_strategies,
    strategy_minimal_deviation,
    strategy_maximum_margin,
    strategy_fastest_return,
    strategy_comprehensive_score
)


# ============================================================================
# 示例1: 基本使用 - 使用不同策略选择最优角度
# ============================================================================

def example_basic_usage():
    """示例1: 基本使用方法"""
    print("="*80)
    print("示例1: 基本使用 - 单个策略选择")
    print("="*80)
    
    # 假设从原有代码得到的安全角度集合
    safe_angles = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
    
    print(f"\n从安全计算得到的可用角度: {safe_angles}")
    print(f"共有 {len(safe_angles)} 个安全的改向角度可选\n")
    
    # -------------------------
    # 策略1: 最小改向角
    # -------------------------
    print("\n" + "-"*80)
    print("使用策略1: 最小改向角")
    print("-"*80)
    optimal_angle, explanation = strategy_minimal_deviation(safe_angles)
    print(explanation)
    
    # -------------------------
    # 策略2: 最大安全裕度
    # -------------------------
    print("\n" + "-"*80)
    print("使用策略2: 最大安全裕度")
    print("-"*80)
    optimal_angle, explanation = strategy_maximum_margin(safe_angles)
    print(explanation)
    
    # -------------------------
    # 策略3: 最快复航
    # -------------------------
    print("\n" + "-"*80)
    print("使用策略3: 最快复航")
    print("-"*80)
    optimal_angle, explanation = strategy_fastest_return(safe_angles, 101*pi/180)
    print(explanation)


# ============================================================================
# 示例2: 综合评分策略（推荐）
# ============================================================================

def example_comprehensive_strategy():
    """示例2: 使用综合评分策略（推荐）"""
    print("\n\n")
    print("="*80)
    print("示例2: 综合评分策略（推荐使用）")
    print("="*80)
    
    # 模拟数据
    safe_angles = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
    
    # 船舶状态 [x, y, course, u_sway, v_surge, r]
    ship_state = [13129232.354082255, 4714024.311997643, 1.74, 0.012, 5.08, 0.0]
    target_state = [13130154.550863445, 4713911.276295917, 1.754, 0.0, 2.51, 0.0]
    
    # 岸线参数
    bank_p1 = np.array([13126214.0, 4714473.0])
    bank_p2 = np.array([13127587.0, 4714219.0])
    
    # 风险参数
    SHIP_BREADTH = 32.5
    RR1 = 1.0 * SHIP_BREADTH
    RR2 = 2.0 * SHIP_BREADTH
    
    print(f"\n安全角度集合: {safe_angles}")
    
    # 使用综合评分策略
    optimal_angle, explanation, scores = strategy_comprehensive_score(
        safe_angles=safe_angles,
        ship_state=ship_state,
        target_state=target_state,
        bank_p1=bank_p1,
        bank_p2=bank_p2,
        RR1=RR1,
        RR2=RR2,
        original_course=101*pi/180
    )
    
    print(explanation)
    
    # 显示前5个得分最高的角度
    print("\n前5个得分最高的角度详情:")
    print("-"*80)
    sorted_scores = sorted(scores.items(), key=lambda x: x[1]['total'], reverse=True)
    for i, (angle, score_info) in enumerate(sorted_scores[:5], 1):
        print(f"\n第{i}名: {angle}度")
        print(f"  总分: {score_info['total']:.4f}")
        print(f"  - 改向成本: {score_info['details']['deviation']:.3f}")
        print(f"  - 岸壁安全: {score_info['details']['bank_safety']:.3f}")
        print(f"  - 避让效果: {score_info['details']['collision_safety']:.3f}")
        print(f"  - 连续性: {score_info['details']['continuity']:.3f}")


# ============================================================================
# 示例3: 自定义权重的综合评分
# ============================================================================

def example_custom_weights():
    """示例3: 使用自定义权重"""
    print("\n\n")
    print("="*80)
    print("示例3: 自定义权重的综合评分")
    print("="*80)
    
    safe_angles = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    ship_state = [13129232.354082255, 4714024.311997643, 1.74, 0.012, 5.08, 0.0]
    target_state = [13130154.550863445, 4713911.276295917, 1.754, 0.0, 2.51, 0.0]
    bank_p1 = np.array([13126214.0, 4714473.0])
    bank_p2 = np.array([13127587.0, 4714219.0])
    RR1, RR2 = 32.5, 65.0
    
    print(f"\n安全角度集合: {safe_angles}\n")
    
    # 场景1: 优先考虑岸壁安全
    print("\n场景1: 优先考虑岸壁安全（比如在狭窄水道）")
    print("-"*80)
    weights_bank_priority = {
        'deviation': 0.15,      # 降低改向成本权重
        'bank_safety': 0.50,    # 大幅提高岸壁安全权重
        'collision_safety': 0.25,
        'continuity': 0.10
    }
    
    optimal1, exp1, _ = strategy_comprehensive_score(
        safe_angles, ship_state, target_state,
        bank_p1, bank_p2, RR1, RR2, 101*pi/180,
        weights=weights_bank_priority
    )
    print(f"最优角度: {optimal1}度")
    print(f"权重设置: {weights_bank_priority}")
    
    # 场景2: 优先考虑最小改向（减少操纵）
    print("\n\n场景2: 优先考虑最小改向（比如在开阔水域）")
    print("-"*80)
    weights_minimal_priority = {
        'deviation': 0.50,      # 大幅提高改向成本权重
        'bank_safety': 0.20,
        'collision_safety': 0.20,
        'continuity': 0.10
    }
    
    optimal2, exp2, _ = strategy_comprehensive_score(
        safe_angles, ship_state, target_state,
        bank_p1, bank_p2, RR1, RR2, 101*pi/180,
        weights=weights_minimal_priority
    )
    print(f"最优角度: {optimal2}度")
    print(f"权重设置: {weights_minimal_priority}")
    
    # 场景3: 优先快速避让（比如紧急情况）
    print("\n\n场景3: 优先快速避让（比如紧急情况）")
    print("-"*80)
    weights_fast_priority = {
        'deviation': 0.10,
        'bank_safety': 0.20,
        'collision_safety': 0.60,  # 大幅提高避让效果权重
        'continuity': 0.10
    }
    
    optimal3, exp3, _ = strategy_comprehensive_score(
        safe_angles, ship_state, target_state,
        bank_p1, bank_p2, RR1, RR2, 101*pi/180,
        weights=weights_fast_priority
    )
    print(f"最优角度: {optimal3}度")
    print(f"权重设置: {weights_fast_priority}")


# ============================================================================
# 示例4: 比较所有策略
# ============================================================================

def example_compare_all():
    """示例4: 比较所有策略的结果"""
    print("\n\n")
    print("="*80)
    print("示例4: 比较所有策略")
    print("="*80)
    
    safe_angles = [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
    ship_state = [13129232.354082255, 4714024.311997643, 1.74, 0.012, 5.08, 0.0]
    target_state = [13130154.550863445, 4713911.276295917, 1.754, 0.0, 2.51, 0.0]
    bank_p1 = np.array([13126214.0, 4714473.0])
    bank_p2 = np.array([13127587.0, 4714219.0])
    RR1, RR2 = 32.5, 65.0
    
    print(f"\n安全角度集合: {safe_angles}\n")
    
    # 使用比较函数
    results = compare_all_strategies(
        safe_angles, ship_state, target_state,
        bank_p1, bank_p2, RR1, RR2, 101*pi/180
    )
    
    print("\n所有策略的推荐结果:")
    print("="*80)
    print(f"策略1 - 最小改向角:   {results['minimal']['angle']}度")
    print(f"策略2 - 最大安全裕度: {results['margin']['angle']}度")
    print(f"策略3 - 最快复航:     {results['fastest']['angle']}度")
    print(f"策略4 - 综合评分:     {results['comprehensive']['angle']}度 （推荐）")
    print("="*80)
    
    print("\n详细说明:")
    print("-"*80)
    for strategy_name, result in results.items():
        print(f"\n{strategy_name.upper()}:")
        print(result['explanation'])


# ============================================================================
# 示例5: 集成到原有代码中
# ============================================================================

def example_integration():
    """示例5: 如何集成到您的原有代码中"""
    print("\n\n")
    print("="*80)
    print("示例5: 集成到原有代码")
    print("="*80)
    
    print("""
    集成步骤：
    
    1. 在您的主程序文件开头添加导入:
       ```python
       from optimal_angle_selection import select_optimal_angle, compare_all_strategies
       ```
    
    2. 在计算出安全角度集合后，添加选择逻辑:
       ```python
       # 您的原有代码
       all_safe_angles = get_safe_angle_range(
           model='overtake',
           # ... 其他参数 ...
       )
       
       # 新增: 选择最优角度
       if all_safe_angles:
           # 方法1: 使用统一接口（推荐综合策略）
           optimal_angle, explanation, scores = select_optimal_angle(
               safe_angles=all_safe_angles,
               strategy='comprehensive',  # 或 'minimal', 'margin', 'fastest'
               ship_state=list_own_initial,
               target_state=list_tar_initial,
               bank_p1=p1,
               bank_p2=p2,
               RR1=RR1,
               RR2=RR2,
               original_course=101*pi/180
           )
           
           print(f"\\n推荐的最优改向角: {optimal_angle}度")
           print(explanation)
           
           # 方法2: 比较所有策略再决策
           all_results = compare_all_strategies(
               all_safe_angles,
               list_own_initial,
               list_tar_initial,
               p1, p2, RR1, RR2
           )
           
           # 可以根据实际情况选择合适的策略结果
           # 比如在狭窄水道选择综合评分，在开阔水域选择最小改向
       ```
    
    3. 根据场景选择策略:
       - 开阔水域，交通密度低 → 使用 'minimal' (最小改向)
       - 狭窄水道，需要精确控制 → 使用 'comprehensive' (综合评分)
       - 紧急避让 → 使用 'fastest' (最快复航)
       - 不确定时 → 使用 'margin' (最大安全裕度)
    
    4. 可选: 自定义权重以适应特定场景
       在调用 select_optimal_angle 时传入 weights 参数
    """)


# ============================================================================
# 示例6: 处理边界情况
# ============================================================================

def example_edge_cases():
    """示例6: 处理各种边界情况"""
    print("\n\n")
    print("="*80)
    print("示例6: 边界情况处理")
    print("="*80)
    
    # 准备测试数据
    ship_state = [13129232.354082255, 4714024.311997643, 1.74, 0.012, 5.08, 0.0]
    target_state = [13130154.550863445, 4713911.276295917, 1.754, 0.0, 2.51, 0.0]
    bank_p1 = np.array([13126214.0, 4714473.0])
    bank_p2 = np.array([13127587.0, 4714219.0])
    RR1, RR2 = 32.5, 65.0
    
    # 情况1: 空的安全角度集合
    print("\n情况1: 没有安全角度")
    print("-"*80)
    empty_angles = []
    result, msg, _ = select_optimal_angle(empty_angles, 'minimal')
    print(f"结果: {result}")
    print(f"说明: {msg}")
    
    # 情况2: 只有一个安全角度
    print("\n\n情况2: 只有一个安全角度")
    print("-"*80)
    single_angle = [15]
    result, msg = strategy_minimal_deviation(single_angle)
    print(f"最优角度: {result}度")
    print(msg)
    
    # 情况3: 非连续的安全角度
    print("\n\n情况3: 非连续的安全角度区间")
    print("-"*80)
    discontinuous_angles = [5, 6, 7, 12, 13, 14, 15, 16, 20, 21]
    result, msg = strategy_maximum_margin(discontinuous_angles)
    print(f"最优角度: {result}度")
    print(msg)
    
    # 情况4: 很大的角度范围
    print("\n\n情况4: 很宽的安全区间")
    print("-"*80)
    wide_range = list(range(5, 31))  # 5到30度
    result, msg = strategy_maximum_margin(wide_range)
    print(f"最优角度: {result}度")
    print(f"区间宽度: {len(wide_range)}度")
    print(msg)


# ============================================================================
# 主函数
# ============================================================================

def main():
    """运行所有示例"""
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*20 + "最优改向角选择 - 完整示例" + " "*28 + "║")
    print("╚" + "="*78 + "╝")
    
    # 运行各个示例
    example_basic_usage()
    example_comprehensive_strategy()
    example_custom_weights()
    example_compare_all()
    example_integration()
    example_edge_cases()
    
    print("\n\n" + "="*80)
    print("所有示例运行完成!")
    print("="*80)
    print("""
    总结与建议:
    
    1. 推荐使用「综合评分策略」作为默认选择
       - 它平衡了多个优化目标
       - 可以通过调整权重适应不同场景
    
    2. 在特定场景下可以选择专用策略:
       - 开阔水域 → 最小改向角策略
       - 狭窄水道 → 最大安全裕度策略  
       - 紧急情况 → 最快复航策略
    
    3. 建议先使用 compare_all_strategies 比较各策略结果
       然后根据实际情况做出最终决策
    
    4. 权重可以根据：
       - 水域特征（开阔/狭窄）
       - 交通密度（高/低）
       - 天气条件（好/差）
       - 船舶状态（正常/受限）
       进行动态调整
    """)


if __name__ == "__main__":
    main()
