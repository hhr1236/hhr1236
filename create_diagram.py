"""
可视化演示：原方法 vs 改进方法的对比
这个脚本创建一个简单的对比图来说明问题和解决方案
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def create_comparison_diagram():
    """创建方法对比图"""
    
    fig = plt.figure(figsize=(16, 10))
    
    # 标题
    fig.suptitle('船舶领域长轴确定方法对比', fontsize=20, fontweight='bold', y=0.98)
    
    # ============ 左侧：原方法 ============
    ax1 = plt.subplot(2, 3, 1)
    ax1.set_title('❌ 原方法（存在问题）', fontsize=14, fontweight='bold', color='red')
    ax1.axis('off')
    
    # 原方法流程
    y_pos = 0.9
    step_height = 0.15
    
    # 步骤1
    box1 = FancyBboxPatch((0.1, y_pos), 0.8, 0.1, boxstyle="round,pad=0.01", 
                          edgecolor='red', facecolor='#ffcccc', linewidth=2)
    ax1.add_patch(box1)
    ax1.text(0.5, y_pos+0.05, '单一工况测试\n舵角=15°, 速度=6m/s', 
            ha='center', va='center', fontsize=11, fontweight='bold')
    
    # 箭头
    arrow1 = FancyArrowPatch((0.5, y_pos-0.02), (0.5, y_pos-step_height+0.02),
                            arrowstyle='->', mutation_scale=20, linewidth=2, color='red')
    ax1.add_patch(arrow1)
    
    y_pos -= step_height
    
    # 步骤2
    box2 = FancyBboxPatch((0.1, y_pos), 0.8, 0.1, boxstyle="round,pad=0.01",
                          edgecolor='red', facecolor='#ffcccc', linewidth=2)
    ax1.add_patch(box2)
    ax1.text(0.5, y_pos+0.05, '生成操纵足迹', 
            ha='center', va='center', fontsize=11)
    
    arrow2 = FancyArrowPatch((0.5, y_pos-0.02), (0.5, y_pos-step_height+0.02),
                            arrowstyle='->', mutation_scale=20, linewidth=2, color='red')
    ax1.add_patch(arrow2)
    
    y_pos -= step_height
    
    # 步骤3
    box3 = FancyBboxPatch((0.1, y_pos), 0.8, 0.1, boxstyle="round,pad=0.01",
                          edgecolor='red', facecolor='#ffcccc', linewidth=2)
    ax1.add_patch(box3)
    ax1.text(0.5, y_pos+0.05, '直接计算长轴\nL = max(y) - min(y)', 
            ha='center', va='center', fontsize=11)
    
    arrow3 = FancyArrowPatch((0.5, y_pos-0.02), (0.5, y_pos-step_height+0.02),
                            arrowstyle='->', mutation_scale=20, linewidth=2, color='red')
    ax1.add_patch(arrow3)
    
    y_pos -= step_height
    
    # 结果
    box4 = FancyBboxPatch((0.1, y_pos), 0.8, 0.12, boxstyle="round,pad=0.01",
                          edgecolor='darkred', facecolor='#ff9999', linewidth=3)
    ax1.add_patch(box4)
    ax1.text(0.5, y_pos+0.06, '❌ 结果不可靠\n可能偏小30-40%', 
            ha='center', va='center', fontsize=11, fontweight='bold', color='darkred')
    
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    
    # ============ 右侧：改进方法 ============
    ax2 = plt.subplot(2, 3, 2)
    ax2.set_title('✅ 改进方法（多工况包络）', fontsize=14, fontweight='bold', color='green')
    ax2.axis('off')
    
    y_pos = 0.9
    
    # 步骤1
    box1 = FancyBboxPatch((0.1, y_pos), 0.8, 0.1, boxstyle="round,pad=0.01",
                          edgecolor='green', facecolor='#ccffcc', linewidth=2)
    ax2.add_patch(box1)
    ax2.text(0.5, y_pos+0.05, '多工况测试\n舵角=15°,20°,25°,30°\n速度=6.0,6.5,7.0m/s', 
            ha='center', va='center', fontsize=10, fontweight='bold')
    
    arrow1 = FancyArrowPatch((0.5, y_pos-0.02), (0.5, y_pos-step_height+0.02),
                            arrowstyle='->', mutation_scale=20, linewidth=2, color='green')
    ax2.add_patch(arrow1)
    
    y_pos -= step_height
    
    # 步骤2
    box2 = FancyBboxPatch((0.1, y_pos), 0.8, 0.1, boxstyle="round,pad=0.01",
                          edgecolor='green', facecolor='#ccffcc', linewidth=2)
    ax2.add_patch(box2)
    ax2.text(0.5, y_pos+0.05, '生成所有工况足迹\n取并集形成包络', 
            ha='center', va='center', fontsize=11)
    
    arrow2 = FancyArrowPatch((0.5, y_pos-0.02), (0.5, y_pos-step_height+0.02),
                            arrowstyle='->', mutation_scale=20, linewidth=2, color='green')
    ax2.add_patch(arrow2)
    
    y_pos -= step_height
    
    # 步骤3
    box3 = FancyBboxPatch((0.1, y_pos), 0.8, 0.1, boxstyle="round,pad=0.01",
                          edgecolor='green', facecolor='#ccffcc', linewidth=2)
    ax2.add_patch(box3)
    ax2.text(0.5, y_pos+0.05, '计算包络长轴\n应用安全系数 ×1.20', 
            ha='center', va='center', fontsize=11)
    
    arrow3 = FancyArrowPatch((0.5, y_pos-0.02), (0.5, y_pos-step_height+0.02),
                            arrowstyle='->', mutation_scale=20, linewidth=2, color='green')
    ax2.add_patch(arrow3)
    
    y_pos -= step_height
    
    # 结果
    box4 = FancyBboxPatch((0.1, y_pos), 0.8, 0.12, boxstyle="round,pad=0.01",
                          edgecolor='darkgreen', facecolor='#99ff99', linewidth=3)
    ax2.add_patch(box4)
    ax2.text(0.5, y_pos+0.06, '✅ 结果可靠\n覆盖所有场景+裕度', 
            ha='center', va='center', fontsize=11, fontweight='bold', color='darkgreen')
    
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    
    # ============ 对比表格 ============
    ax3 = plt.subplot(2, 3, 3)
    ax3.set_title('📊 方法对比', fontsize=14, fontweight='bold')
    ax3.axis('off')
    
    comparison_data = [
        ['项目', '原方法', '改进方法'],
        ['测试工况', '1组', '5-10组'],
        ['覆盖范围', '单一场景', '多场景包络'],
        ['安全系数', '无(0%)', '有(20%)'],
        ['长轴准确性', '可能偏小', '更可靠'],
        ['计算时间', '快', '中等'],
        ['推荐程度', '⭐', '⭐⭐⭐⭐⭐'],
    ]
    
    # 绘制表格
    table = ax3.table(cellText=comparison_data, loc='center', cellLoc='center',
                     colWidths=[0.3, 0.35, 0.35])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.5)
    
    # 设置表头样式
    for i in range(3):
        table[(0, i)].set_facecolor('#4472C4')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # 设置行颜色
    for i in range(1, len(comparison_data)):
        table[(i, 0)].set_facecolor('#E7E6E6')
        table[(i, 1)].set_facecolor('#FFE699')
        table[(i, 2)].set_facecolor('#C6EFCE')
    
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    
    # ============ 下方：问题说明 ============
    ax4 = plt.subplot(2, 3, (4, 6))
    ax4.axis('off')
    
    problem_text = """
原方法的问题分析：

1. 单一工况问题 ❌
   • 只测试了舵角15°，如果实际操纵需要25°舵角怎么办？
   • 只测试了速度6m/s，如果高速航行（7-8m/s）怎么办？
   • 结果：可能无法覆盖实际操纵的极限情况

2. 缺乏安全裕度 ❌
   • 直接使用操纵足迹的"自然尺寸"
   • 没有考虑模型误差、测量误差、操作误差
   • 结果：安全余量不足，存在风险

3. 无法验证 ❌
   • 没有对比不同工况的结果
   • 无法判断长轴是否足够
   • 结果：不知道结果是否可靠

改进方法的优势：

1. 多工况包络 ✅
   • 测试多种舵角（10°, 15°, 20°, 25°, 30°）
   • 测试多种速度（5.0, 6.0, 6.5, 7.0, 7.5 m/s）
   • 取所有工况的最大包络，确保覆盖所有可能场景

2. 安全系数 ✅
   • 在自然尺寸基础上乘以1.20（20%裕度）
   • 考虑浅水效应的复杂性
   • 符合海事安全工程惯例

3. 可验证性 ✅
   • 可以对比不同工况的结果
   • 可以进行参数敏感性分析
   • 可以与文献经验值对比（4-12倍船长）

预期改进效果：
• 长轴增加 30-40%（从约700m增至约1000m）
• 覆盖范围更全面（5-10个工况 vs 1个工况）
• 安全性显著提升（有20%裕度 vs 无裕度）
• 结果更可靠、更有科学依据
"""
    
    ax4.text(0.05, 0.98, problem_text, fontsize=11, verticalalignment='top',
            family='monospace', bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)
    
    plt.tight_layout()
    plt.savefig('solution_comparison_diagram.png', dpi=150, bbox_inches='tight')
    print("\n对比图已保存至: solution_comparison_diagram.png")
    print("\n这张图清晰展示了：")
    print("  • 原方法的流程和问题")
    print("  • 改进方法的流程和优势")
    print("  • 两种方法的详细对比")
    print("  • 问题分析和改进效果")
    
    plt.show()


if __name__ == "__main__":
    print("="*80)
    print("生成方法对比图...")
    print("="*80)
    create_comparison_diagram()
