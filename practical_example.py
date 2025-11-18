"""
实用示例：如何改进你的代码来准确确定长轴

这个脚本展示了如何将你原有的代码改进为更可靠的长轴确定方法
"""

import numpy as np
import matplotlib.pyplot as plt
from math import pi, cos, sin
from scipy.spatial import ConvexHull
from matplotlib.patches import Ellipse

# 假设这些是你自己的模块
# from mmg_anbi import compute_next_moment_anbi
# from mmg_anbi_qianshui11 import MMG_Model_new1
# from ship_data import list_ship_data

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# --- 配置参数 ---
SHIP_LENGTH = 225.0
SHIP_WIDTH = SHIP_LENGTH / 8
SAFE_LATERAL_DISTANCE = 150.0
REQUIRED_DOMAIN_WIDTH = 3 * SHIP_WIDTH

# ============================================================================
# 方法对比：展示原方法 vs 改进方法的区别
# ============================================================================

def original_method():
    """
    你原来的方法（存在问题）
    """
    print("\n" + "="*80)
    print("【原方法】单一工况法")
    print("="*80)
    
    # 只测试一组舵角和航速
    rudder_angle = 15.0
    speed = 6.0
    
    print(f"测试工况: 舵角={rudder_angle}°, 航速={speed}m/s")
    
    # 仿真（这里用简化模型演示）
    footprint_right = simulate_simple(rudder_angle, speed, SAFE_LATERAL_DISTANCE)
    footprint_left = simulate_simple(-rudder_angle, speed, SAFE_LATERAL_DISTANCE)
    
    # 计算凸包
    all_points = np.array(footprint_right + footprint_left)
    hull = ConvexHull(all_points)
    hull_vertices = all_points[hull.vertices]
    
    # 直接取最大最小值
    L_footprint = np.max(hull_vertices[:, 1]) - np.min(hull_vertices[:, 1])
    B_footprint = np.max(hull_vertices[:, 0]) - np.min(hull_vertices[:, 0])
    
    print(f"\n结果:")
    print(f"  长轴 L = {L_footprint:.2f}m ({L_footprint/SHIP_LENGTH:.2f} 倍船长)")
    print(f"  短轴 B = {B_footprint:.2f}m ({B_footprint/SHIP_WIDTH:.2f} 倍船宽)")
    
    print(f"\n问题分析:")
    print(f"  ❌ 只测试了一组舵角（15°），如果遇到25°舵角怎么办？")
    print(f"  ❌ 只测试了一个航速（6m/s），如果高速或低速怎么办？")
    print(f"  ❌ 没有安全裕度，如果模型有误差怎么办？")
    print(f"  ❌ 无法确定这个长轴是否足够安全")
    
    return L_footprint, B_footprint, hull_vertices


def improved_method_1():
    """
    改进方法1：多工况包络法（推荐）
    """
    print("\n" + "="*80)
    print("【改进方法1】多工况包络法")
    print("="*80)
    
    # 设计多组测试工况
    test_matrix = [
        (10, 5.0),   # 小舵角，低速
        (15, 6.0),   # 中舵角，中速
        (20, 6.5),   # 大舵角，中速
        (25, 7.0),   # 大舵角，高速
        (30, 7.5),   # 极大舵角，高速
    ]
    
    print(f"测试 {len(test_matrix)} 组工况:")
    for i, (rudder, speed) in enumerate(test_matrix, 1):
        print(f"  工况{i}: 舵角={rudder}°, 航速={speed}m/s")
    
    # 收集所有工况的足迹
    all_footprints = []
    
    for rudder, speed in test_matrix:
        fp_right = simulate_simple(rudder, speed, SAFE_LATERAL_DISTANCE)
        fp_left = simulate_simple(-rudder, speed, SAFE_LATERAL_DISTANCE)
        all_footprints.extend(fp_right)
        all_footprints.extend(fp_left)
    
    # 计算总包络
    all_points = np.array(all_footprints)
    hull = ConvexHull(all_points)
    hull_vertices = all_points[hull.vertices]
    
    L_natural = np.max(hull_vertices[:, 1]) - np.min(hull_vertices[:, 1])
    B_natural = np.max(hull_vertices[:, 0]) - np.min(hull_vertices[:, 0])
    
    # 应用安全系数
    SAFETY_FACTOR = 1.20  # 浅水条件建议20%
    L_final = L_natural * SAFETY_FACTOR
    B_final = max(B_natural, REQUIRED_DOMAIN_WIDTH) * SAFETY_FACTOR
    
    print(f"\n结果:")
    print(f"  自然长轴 L = {L_natural:.2f}m")
    print(f"  含安全系数 L = {L_final:.2f}m ({L_final/SHIP_LENGTH:.2f} 倍船长)")
    print(f"  自然短轴 B = {B_natural:.2f}m")
    print(f"  含安全系数 B = {B_final:.2f}m ({B_final/SHIP_WIDTH:.2f} 倍船宽)")
    
    print(f"\n优势:")
    print(f"  ✅ 测试了多种可能的操纵场景")
    print(f"  ✅ 包络了所有工况的极限情况")
    print(f"  ✅ 应用了20%的安全裕度")
    print(f"  ✅ 结果更可靠、更安全")
    
    return L_final, B_final, hull_vertices


def improved_method_2():
    """
    改进方法2：参数敏感性分析法
    """
    print("\n" + "="*80)
    print("【改进方法2】参数敏感性分析法")
    print("="*80)
    
    # 测试舵角的影响
    print("\n分析舵角对长轴的影响:")
    rudder_angles = [5, 10, 15, 20, 25, 30, 35]
    L_vs_rudder = []
    
    for rudder in rudder_angles:
        fp_r = simulate_simple(rudder, 6.0, SAFE_LATERAL_DISTANCE)
        fp_l = simulate_simple(-rudder, 6.0, SAFE_LATERAL_DISTANCE)
        points = np.array(fp_r + fp_l)
        hull = ConvexHull(points)
        L = np.max(points[hull.vertices][:, 1]) - np.min(points[hull.vertices][:, 1])
        L_vs_rudder.append((rudder, L))
        print(f"  舵角 {rudder:2d}° → L = {L:.2f}m")
    
    # 测试航速的影响
    print("\n分析航速对长轴的影响:")
    speeds = [4.0, 5.0, 6.0, 7.0, 8.0]
    L_vs_speed = []
    
    for speed in speeds:
        fp_r = simulate_simple(15, speed, SAFE_LATERAL_DISTANCE)
        fp_l = simulate_simple(-15, speed, SAFE_LATERAL_DISTANCE)
        points = np.array(fp_r + fp_l)
        hull = ConvexHull(points)
        L = np.max(points[hull.vertices][:, 1]) - np.min(points[hull.vertices][:, 1])
        L_vs_speed.append((speed, L))
        print(f"  航速 {speed:.1f}m/s → L = {L:.2f}m")
    
    # 找出最大值作为设计长轴
    max_L_rudder = max(L_vs_rudder, key=lambda x: x[1])
    max_L_speed = max(L_vs_speed, key=lambda x: x[1])
    
    L_design = max(max_L_rudder[1], max_L_speed[1]) * 1.15  # 15%安全系数
    
    print(f"\n结果:")
    print(f"  舵角影响: 最大L在舵角{max_L_rudder[0]}°时，L={max_L_rudder[1]:.2f}m")
    print(f"  航速影响: 最大L在航速{max_L_speed[0]}m/s时，L={max_L_speed[1]:.2f}m")
    print(f"  设计长轴: L = {L_design:.2f}m (含15%安全系数)")
    
    print(f"\n洞察:")
    L_range_rudder = max([x[1] for x in L_vs_rudder]) - min([x[1] for x in L_vs_rudder])
    L_range_speed = max([x[1] for x in L_vs_speed]) - min([x[1] for x in L_vs_speed])
    
    if L_range_rudder > L_range_speed:
        print(f"  💡 舵角对长轴的影响更大（变化范围{L_range_rudder:.2f}m vs {L_range_speed:.2f}m）")
        print(f"     建议重点考虑大舵角工况")
    else:
        print(f"  💡 航速对长轴的影响更大（变化范围{L_range_speed:.2f}m vs {L_range_rudder:.2f}m）")
        print(f"     建议重点考虑高速工况")
    
    return L_design, L_vs_rudder, L_vs_speed


def simulate_simple(rudder_angle, speed, target_lateral_dist):
    """
    简化的仿真模型（用于演示）
    实际使用时应该替换为你的MMG模型
    """
    # 简化参数
    if abs(rudder_angle) < 15:
        turning_radius = 600
    elif abs(rudder_angle) < 25:
        turning_radius = 400
    else:
        turning_radius = 300
    
    angular_velocity = speed / turning_radius * np.sign(rudder_angle)
    
    ship_vertices = np.array([
        [-12.5, -75.], [-9.375, -93.75], [9.375, -93.75], [12.5, -75.],
        [12.5, 0.], [9.375, 18.75], [0., 37.5], [-9.375, 18.75], [-12.5, 0.]
    ])
    
    x, y, heading = 0.0, 0.0, 0.0
    footprint_points = []
    
    for step in range(3000):
        heading += angular_velocity * 0.1
        x += speed * cos(heading) * 0.1
        y += speed * sin(heading) * 0.1
        
        rotation_matrix = np.array([
            [cos(heading), -sin(heading)],
            [sin(heading), cos(heading)]
        ])
        transformed_vertices = np.dot(ship_vertices, rotation_matrix) + np.array([x, y])
        footprint_points.extend(transformed_vertices)
        
        if np.sign(rudder_angle) * x >= target_lateral_dist:
            break
    
    return footprint_points


def visualize_comparison(original_result, improved_result1):
    """
    对比可视化：原方法 vs 改进方法
    """
    print("\n" + "="*80)
    print("生成对比图...")
    print("="*80)
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    # 左图：原方法
    ax1 = axes[0]
    L_orig, B_orig, hull_orig = original_result
    hull_closed = np.append(hull_orig, [hull_orig[0]], axis=0)
    ax1.plot(hull_closed[:, 0], hull_closed[:, 1], 'b--', linewidth=2, label='操纵足迹')
    ax1.fill(hull_closed[:, 0], hull_closed[:, 1], 'b', alpha=0.2)
    
    ellipse_orig = Ellipse(
        xy=(0, 0), width=max(B_orig, REQUIRED_DOMAIN_WIDTH), height=L_orig,
        edgecolor='r', fc='None', lw=2, label='原方法领域'
    )
    ax1.add_patch(ellipse_orig)
    
    ax1.set_xlabel('横向位移 X / m', fontsize=12)
    ax1.set_ylabel('纵向位移 Y / m', fontsize=12)
    ax1.set_title(f'原方法: L={L_orig:.0f}m, B={max(B_orig, REQUIRED_DOMAIN_WIDTH):.0f}m', 
                  fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.axis('equal')
    
    # 右图：改进方法
    ax2 = axes[1]
    L_imp, B_imp, hull_imp = improved_result1
    hull_closed = np.append(hull_imp, [hull_imp[0]], axis=0)
    ax2.plot(hull_closed[:, 0], hull_closed[:, 1], 'g--', linewidth=2, label='多工况足迹包络')
    ax2.fill(hull_closed[:, 0], hull_closed[:, 1], 'g', alpha=0.2)
    
    ellipse_imp = Ellipse(
        xy=(0, 0), width=B_imp, height=L_imp,
        edgecolor='r', fc='None', lw=2, label='改进方法领域'
    )
    ax2.add_patch(ellipse_imp)
    
    ax2.set_xlabel('横向位移 X / m', fontsize=12)
    ax2.set_ylabel('纵向位移 Y / m', fontsize=12)
    ax2.set_title(f'改进方法: L={L_imp:.0f}m, B={B_imp:.0f}m (含20%安全系数)', 
                  fontsize=14, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.axis('equal')
    
    plt.tight_layout()
    plt.savefig('method_comparison.png', dpi=150, bbox_inches='tight')
    print("对比图已保存至: method_comparison.png")
    
    # 打印差异分析
    print(f"\n差异分析:")
    print(f"  长轴增加: {L_imp - L_orig:.2f}m ({(L_imp/L_orig-1)*100:.1f}%)")
    print(f"  短轴增加: {B_imp - max(B_orig, REQUIRED_DOMAIN_WIDTH):.2f}m")
    
    if L_imp > L_orig * 1.1:
        print(f"  ⚠️  改进方法的长轴显著大于原方法（>10%）")
        print(f"      说明原方法确实低估了长轴，存在安全隐患！")
    
    plt.show()


def sensitivity_visualization(L_vs_rudder, L_vs_speed):
    """
    参数敏感性可视化
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 舵角敏感性
    ax1 = axes[0]
    rudders = [x[0] for x in L_vs_rudder]
    L_rudders = [x[1] for x in L_vs_rudder]
    ax1.plot(rudders, L_rudders, 'o-', linewidth=2, markersize=8, color='blue')
    ax1.set_xlabel('舵角 / °', fontsize=12)
    ax1.set_ylabel('长轴 L / m', fontsize=12)
    ax1.set_title('长轴 vs 舵角敏感性分析', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # 航速敏感性
    ax2 = axes[1]
    speeds = [x[0] for x in L_vs_speed]
    L_speeds = [x[1] for x in L_vs_speed]
    ax2.plot(speeds, L_speeds, 's-', linewidth=2, markersize=8, color='green')
    ax2.set_xlabel('航速 / m/s', fontsize=12)
    ax2.set_ylabel('长轴 L / m', fontsize=12)
    ax2.set_title('长轴 vs 航速敏感性分析', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('sensitivity_analysis.png', dpi=150, bbox_inches='tight')
    print("\n敏感性分析图已保存至: sensitivity_analysis.png")
    plt.show()


def main():
    """
    主函数：运行所有方法并对比
    """
    print("="*80)
    print("船舶领域长轴确定方法对比演示")
    print("="*80)
    print("\n这个脚本将展示:")
    print("1. 你原来的方法及其问题")
    print("2. 改进方法1：多工况包络法")
    print("3. 改进方法2：参数敏感性分析法")
    print("4. 可视化对比")
    
    # 运行原方法
    original_result = original_method()
    
    # 运行改进方法1
    improved_result1 = improved_method_1()
    
    # 运行改进方法2
    L_design, L_vs_rudder, L_vs_speed = improved_method_2()
    
    # 可视化对比
    visualize_comparison(original_result, improved_result1)
    sensitivity_visualization(L_vs_rudder, L_vs_speed)
    
    # 最终建议
    print("\n" + "="*80)
    print("最终建议")
    print("="*80)
    print(f"""
基于以上分析，建议采用以下长轴值：

1. 保守方案（推荐用于初步设计）：
   L = {improved_result1[0]:.2f}m ({improved_result1[0]/SHIP_LENGTH:.2f} 倍船长)
   基于多工况包络 + 20%安全系数

2. 平衡方案：
   L = {L_design:.2f}m ({L_design/SHIP_LENGTH:.2f} 倍船长)
   基于参数敏感性分析 + 15%安全系数

3. 激进方案（不推荐）：
   L = {original_result[0]:.2f}m ({original_result[0]/SHIP_LENGTH:.2f} 倍船长)
   仅基于单一工况，无安全裕度

💡 实际应用建议：
- 如果是安全关键应用（如避碰），使用保守方案
- 如果需要平衡安全和效率，使用平衡方案
- 建议用实船或高保真仿真验证最终选择

📊 下一步工作：
1. 将简化模型替换为你的实际MMG浅水模型
2. 增加更多测试工况（不同水深、装载状态等）
3. 用统计方法分析结果的置信区间
4. 与文献中的船舶领域模型对比验证
""")


if __name__ == "__main__":
    main()
