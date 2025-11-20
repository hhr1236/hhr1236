"""
测试脚本 - 验证最优角度选择功能

这个脚本验证各种策略在不同场景下的表现
"""

import numpy as np
from math import pi
from optimal_angle_selection import (
    select_optimal_angle,
    compare_all_strategies,
    strategy_minimal_deviation,
    strategy_maximum_margin,
    strategy_fastest_return,
    strategy_comprehensive_score
)


def test_minimal_deviation():
    """测试最小改向角策略"""
    print("\n" + "="*80)
    print("测试1: 最小改向角策略")
    print("="*80)
    
    # 测试用例1: 连续区间
    safe_angles = [10, 11, 12, 13, 14, 15]
    result, explanation = strategy_minimal_deviation(safe_angles)
    assert result == 10, f"期望10，实际{result}"
    print(f"✓ 测试通过: 连续区间 {safe_angles} -> {result}度")
    
    # 测试用例2: 非连续区间
    safe_angles = [5, 8, 10, 15, 20]
    result, explanation = strategy_minimal_deviation(safe_angles)
    assert result == 5, f"期望5，实际{result}"
    print(f"✓ 测试通过: 非连续区间 {safe_angles} -> {result}度")
    
    # 测试用例3: 单个角度
    safe_angles = [15]
    result, explanation = strategy_minimal_deviation(safe_angles)
    assert result == 15, f"期望15，实际{result}"
    print(f"✓ 测试通过: 单个角度 {safe_angles} -> {result}度")
    
    print("\n✅ 最小改向角策略测试全部通过")


def test_maximum_margin():
    """测试最大安全裕度策略"""
    print("\n" + "="*80)
    print("测试2: 最大安全裕度策略")
    print("="*80)
    
    # 测试用例1: 连续区间 - 奇数个
    safe_angles = [10, 11, 12, 13, 14]
    result, explanation = strategy_maximum_margin(safe_angles)
    assert result == 12, f"期望12，实际{result}"
    print(f"✓ 测试通过: 连续区间(奇数) {safe_angles} -> {result}度")
    
    # 测试用例2: 连续区间 - 偶数个
    safe_angles = [10, 11, 12, 13]
    result, explanation = strategy_maximum_margin(safe_angles)
    assert result in [11, 12], f"期望11或12，实际{result}"
    print(f"✓ 测试通过: 连续区间(偶数) {safe_angles} -> {result}度")
    
    # 测试用例3: 非连续区间
    safe_angles = [5, 6, 10, 11, 12, 13, 14, 20]
    result, explanation = strategy_maximum_margin(safe_angles)
    # 最长连续段是 [10,11,12,13,14]，中点是12
    assert result == 12, f"期望12，实际{result}"
    print(f"✓ 测试通过: 非连续区间 {safe_angles} -> {result}度")
    
    print("\n✅ 最大安全裕度策略测试全部通过")


def test_fastest_return():
    """测试最快复航策略"""
    print("\n" + "="*80)
    print("测试3: 最快复航策略")
    print("="*80)
    
    # 测试用例1: 连续区间
    safe_angles = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    result, explanation = strategy_fastest_return(safe_angles, 101*pi/180)
    # 75%分位应该在较大的角度
    assert result >= 17, f"期望>=17，实际{result}"
    print(f"✓ 测试通过: {safe_angles} -> {result}度 (应该>=17)")
    
    # 测试用例2: 较短区间
    safe_angles = [10, 11, 12, 13]
    result, explanation = strategy_fastest_return(safe_angles, 101*pi/180)
    assert result >= 12, f"期望>=12，实际{result}"
    print(f"✓ 测试通过: {safe_angles} -> {result}度 (应该>=12)")
    
    print("\n✅ 最快复航策略测试全部通过")


def test_comprehensive_score():
    """测试综合评分策略"""
    print("\n" + "="*80)
    print("测试4: 综合评分策略")
    print("="*80)
    
    safe_angles = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    ship_state = [13129232.354082255, 4714024.311997643, 1.74, 0.012, 5.08, 0.0]
    target_state = [13130154.550863445, 4713911.276295917, 1.754, 0.0, 2.51, 0.0]
    bank_p1 = np.array([13126214.0, 4714473.0])
    bank_p2 = np.array([13127587.0, 4714219.0])
    RR1, RR2 = 32.5, 65.0
    
    # 测试用例1: 默认权重
    result, explanation, scores = strategy_comprehensive_score(
        safe_angles, ship_state, target_state,
        bank_p1, bank_p2, RR1, RR2, 101*pi/180
    )
    assert result in safe_angles, f"结果{result}不在安全角度集合中"
    assert len(scores) == len(safe_angles), "评分数量应与角度数量相同"
    print(f"✓ 测试通过: 默认权重 -> {result}度")
    print(f"  总分: {scores[result]['total']:.4f}")
    
    # 测试用例2: 自定义权重（优先最小改向）
    weights_minimal = {
        'deviation': 0.70,
        'bank_safety': 0.15,
        'collision_safety': 0.15
    }
    result2, _, scores2 = strategy_comprehensive_score(
        safe_angles, ship_state, target_state,
        bank_p1, bank_p2, RR1, RR2, 101*pi/180,
        weights=weights_minimal
    )
    # 应该选择较小的角度
    assert result2 <= 13, f"优先最小改向时，期望<=13，实际{result2}"
    print(f"✓ 测试通过: 优先最小改向 -> {result2}度")
    
    # 测试用例3: 自定义权重（优先避让效果）
    weights_collision = {
        'deviation': 0.10,
        'bank_safety': 0.20,
        'collision_safety': 0.70
    }
    result3, _, scores3 = strategy_comprehensive_score(
        safe_angles, ship_state, target_state,
        bank_p1, bank_p2, RR1, RR2, 101*pi/180,
        weights=weights_collision
    )
    # 检查collision_safety得分被正确计算（包含tcpa和dcpa）
    assert 'tcpa' in scores3[result3]['details'], "应该包含TCPA信息"
    assert 'dcpa' in scores3[result3]['details'], "应该包含DCPA信息"
    print(f"✓ 测试通过: 优先避让效果 -> {result3}度")
    print(f"  TCPA={scores3[result3]['details']['tcpa']:.1f}秒, DCPA={scores3[result3]['details']['dcpa']:.1f}米")
    
    print("\n✅ 综合评分策略测试全部通过")


def test_unified_interface():
    """测试统一接口"""
    print("\n" + "="*80)
    print("测试5: 统一接口")
    print("="*80)
    
    safe_angles = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    ship_state = [13129232.354082255, 4714024.311997643, 1.74, 0.012, 5.08, 0.0]
    target_state = [13130154.550863445, 4713911.276295917, 1.754, 0.0, 2.51, 0.0]
    bank_p1 = np.array([13126214.0, 4714473.0])
    bank_p2 = np.array([13127587.0, 4714219.0])
    RR1, RR2 = 32.5, 65.0
    
    # 测试各种策略
    strategies = ['minimal', 'margin', 'fastest', 'comprehensive']
    for strategy in strategies:
        result, explanation, extra = select_optimal_angle(
            safe_angles=safe_angles,
            strategy=strategy,
            ship_state=ship_state,
            target_state=target_state,
            bank_p1=bank_p1,
            bank_p2=bank_p2,
            RR1=RR1,
            RR2=RR2,
            original_course=101*pi/180
        )
        assert result in safe_angles, f"策略{strategy}的结果{result}不在安全集合中"
        print(f"✓ 测试通过: 策略'{strategy}' -> {result}度")
    
    print("\n✅ 统一接口测试全部通过")


def test_edge_cases():
    """测试边界情况"""
    print("\n" + "="*80)
    print("测试6: 边界情况")
    print("="*80)
    
    # 测试用例1: 空集合
    safe_angles = []
    result, msg = strategy_minimal_deviation(safe_angles)
    assert result is None, "空集合应返回None"
    print(f"✓ 测试通过: 空集合 -> {result}")
    
    # 测试用例2: 单个角度
    safe_angles = [15]
    result, msg = strategy_minimal_deviation(safe_angles)
    assert result == 15, f"单个角度应返回该角度，实际{result}"
    print(f"✓ 测试通过: 单个角度 -> {result}度")
    
    # 测试用例3: 大范围
    safe_angles = list(range(5, 36))  # 5-35度
    result, msg = strategy_maximum_margin(safe_angles)
    assert 15 <= result <= 25, f"大范围应选择中间值，实际{result}"
    print(f"✓ 测试通过: 大范围[5-35] -> {result}度")
    
    print("\n✅ 边界情况测试全部通过")


def test_compare_all():
    """测试策略比较功能"""
    print("\n" + "="*80)
    print("测试7: 策略比较功能")
    print("="*80)
    
    safe_angles = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    ship_state = [13129232.354082255, 4714024.311997643, 1.74, 0.012, 5.08, 0.0]
    target_state = [13130154.550863445, 4713911.276295917, 1.754, 0.0, 2.51, 0.0]
    bank_p1 = np.array([13126214.0, 4714473.0])
    bank_p2 = np.array([13127587.0, 4714219.0])
    RR1, RR2 = 32.5, 65.0
    
    results = compare_all_strategies(
        safe_angles, ship_state, target_state,
        bank_p1, bank_p2, RR1, RR2, 101*pi/180
    )
    
    assert 'minimal' in results
    assert 'margin' in results
    assert 'fastest' in results
    assert 'comprehensive' in results
    
    print(f"✓ 策略1（最小改向）: {results['minimal']['angle']}度")
    print(f"✓ 策略2（最大裕度）: {results['margin']['angle']}度")
    print(f"✓ 策略3（最快复航）: {results['fastest']['angle']}度")
    print(f"✓ 策略4（综合评分）: {results['comprehensive']['angle']}度")
    
    print("\n✅ 策略比较功能测试通过")


def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*25 + "开始运行测试套件" + " "*30 + "║")
    print("╚" + "="*78 + "╝")
    
    try:
        test_minimal_deviation()
        test_maximum_margin()
        test_fastest_return()
        test_comprehensive_score()
        test_unified_interface()
        test_edge_cases()
        test_compare_all()
        
        print("\n" + "="*80)
        print("🎉 所有测试通过！")
        print("="*80)
        print("""
测试总结:
✅ 最小改向角策略 - 正常工作
✅ 最大安全裕度策略 - 正常工作
✅ 最快复航策略 - 正常工作
✅ 综合评分策略 - 正常工作
✅ 统一接口 - 正常工作
✅ 边界情况处理 - 正常工作
✅ 策略比较功能 - 正常工作

系统已准备就绪，可以集成到您的主程序中！
        """)
        return True
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
