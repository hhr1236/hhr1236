"""
车舵协同避让决策优化Demo
====================================
扩展原有的纯转向角优化，增加变速能力，实现车舵协同的多维度决策优化。

主要改进：
1. 搜索空间：从一维（角度）扩展到二维（角度×速度）
2. 速度档位：前进三(85/60)、前进二(70/60)、前进一(48/60)
3. 决策变量：(angle, speed_gear) 组合
4. 优化目标：DCPA、风险度、避让时间
"""

import numpy as np
import math
from numba import jit, njit, typed
import matplotlib.pyplot as plt
from math import *

# 假设这些依赖已准备好（用户代码中的模块）
# from tar_position import get_tar_position
# from ship_data import list_ship_data
# from CRI import danger_evaluate
# from mmg_anbi_qianshui import compute_next_moment
# from PID_1 import pid_duojiao

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ================================================================
# 速度档位定义
# ================================================================
SPEED_GEARS = {
    '前进三': 85.0 / 60.0,  # 约 1.417 m/s
    '前进二': 70.0 / 60.0,  # 约 1.167 m/s
    '前进一': 48.0 / 60.0,  # 约 0.800 m/s
}

# 索引编号便于程序使用
GEAR_INDEX = {
    0: ('前进三', 85.0 / 60.0),
    1: ('前进二', 70.0 / 60.0),
    2: ('前进一', 48.0 / 60.0),
}


# ================================================================
# 核心改进：车舵协同评估函数
# ================================================================
def evaluate_rudder_speed_combination(
    angle,           # 转向角度（度）
    speed_gear_idx,  # 速度档位索引 (0/1/2)
    model,           # 避让模型 ('meet', 'cross', 'overtake')
    list_own,        # 本船状态
    list_tar,        # 目标船状态
    list_own_ship_initial,  # 本船参数
    deep,            # 水深
    bank_p1, bank_p2,  # 航道边界
    RR1, RR2,        # 风险距离阈值
    U_threshold,     # 风险度阈值
    original_course  # 原始航向
):
    """
    评估单个(角度,速度)组合的性能
    
    返回：
    - status: 1=成功, -1=碰撞, -2=超出风险阈值, 0=超时
    - dcpa: 最近会遇距离（只在成功时有意义）
    - max_risk: 过程中的最大风险度
    - steps: 避让所需步数（时间）
    """
    
    # 获取速度档位信息
    gear_name, gear_value = GEAR_INDEX[speed_gear_idx]
    
    # *** 关键修改点 ***
    # 这里需要调用你的仿真引擎，修改 list_own_ship_initial[11] = gear_value
    # 然后进行避让仿真，类似原代码的 evaluate_all_maneuvers_with_risk
    
    # 为了demo演示，这里使用简化的模拟逻辑
    # 实际使用时需替换为你的完整仿真代码
    
    # 示例：避让时间（速度越快，避让时间越短，但风险可能增加）
    base_steps = 400
    steps = int(base_steps / gear_value) if gear_value > 0 else 800
    
    # 示例：DCPA和风险度的计算（需要实际仿真）
    # 这里用简化公式模拟：角度越大，DCPA越大；速度越快，风险越高
    dcpa = 50.0 + angle * 3.0 - speed_gear_idx * 10.0
    max_risk = 0.3 + (speed_gear_idx * 0.15) + (35 - angle) * 0.01
    
    # 判断是否成功（简化版）
    if dcpa < 20.0:
        status = -1  # 碰撞
    elif max_risk > U_threshold:
        status = -2  # 超出风险阈值
    elif steps > 800:
        status = 0   # 超时
    else:
        status = 1   # 成功
    
    return {
        'angle': angle,
        'speed_gear': gear_name,
        'speed_value': gear_value,
        'status': status,
        'dcpa': dcpa if status == 1 else -1,
        'max_risk': max_risk,
        'steps': steps
    }


# ================================================================
# 车舵协同的多目标优化
# ================================================================
def optimize_rudder_speed_coordination(
    angle_range=(5, 36),      # 转向角度范围
    speed_gears=(0, 1, 2),    # 速度档位范围
    model='meet',
    list_own=None,
    list_tar=None,
    list_own_ship_initial=None,
    deep=23.0,
    bank_p1=None,
    bank_p2=None,
    RR1=32.5,
    RR2=130.0,
    U_threshold=0.75,
    original_course=101*math.pi/180
):
    """
    遍历所有(角度, 速度)组合，找出帕累托最优解
    """
    
    all_results = []
    successful_results = []
    
    print("=" * 80)
    print("开始车舵协同优化评估...")
    print(f"角度范围: {angle_range[0]}° - {angle_range[1]-1}°")
    print(f"速度档位: {[GEAR_INDEX[g][0] for g in speed_gears]}")
    print("=" * 80)
    
    # 遍历所有组合
    total_combinations = (angle_range[1] - angle_range[0]) * len(speed_gears)
    count = 0
    
    for angle in range(angle_range[0], angle_range[1]):
        for gear_idx in speed_gears:
            count += 1
            
            result = evaluate_rudder_speed_combination(
                angle, gear_idx, model,
                list_own, list_tar, list_own_ship_initial,
                deep, bank_p1, bank_p2, RR1, RR2,
                U_threshold, original_course
            )
            
            all_results.append(result)
            
            if result['status'] == 1:
                successful_results.append(result)
            
            # 进度显示
            if count % 10 == 0 or count == total_combinations:
                print(f"进度: {count}/{total_combinations} "
                      f"({100*count/total_combinations:.1f}%) - "
                      f"成功方案数: {len(successful_results)}")
    
    print("\n" + "=" * 80)
    print(f"评估完成！总方案数: {len(all_results)}, 成功方案数: {len(successful_results)}")
    print("=" * 80)
    
    return all_results, successful_results


# ================================================================
# 帕累托前沿筛选（多目标版本）
# ================================================================
def find_pareto_front_multi_objective(successful_results):
    """
    针对车舵协同优化的帕累托筛选
    
    目标函数：
    1. max_risk （风险度，越小越好）
    2. dcpa （DCPA，越大越好）
    3. steps （避让时间，越小越好）
    """
    
    if not successful_results:
        return []
    
    pareto_front = []
    
    for i, sol_A in enumerate(successful_results):
        is_dominated = False
        
        for j, sol_B in enumerate(successful_results):
            if i == j:
                continue
            
            # 检查sol_B是否支配sol_A
            # sol_B支配sol_A的条件：
            # 1. sol_B在所有目标上都不差于sol_A
            # 2. sol_B至少在一个目标上严格优于sol_A
            
            # 目标1：最小化max_risk
            risk_better = sol_B['max_risk'] <= sol_A['max_risk']
            risk_strictly = sol_B['max_risk'] < sol_A['max_risk']
            
            # 目标2：最大化dcpa
            dcpa_better = sol_B['dcpa'] >= sol_A['dcpa']
            dcpa_strictly = sol_B['dcpa'] > sol_A['dcpa']
            
            # 目标3：最小化steps
            steps_better = sol_B['steps'] <= sol_A['steps']
            steps_strictly = sol_B['steps'] < sol_A['steps']
            
            # 检查支配关系
            all_better_or_equal = (risk_better and dcpa_better and steps_better)
            at_least_one_strictly = (risk_strictly or dcpa_strictly or steps_strictly)
            
            if all_better_or_equal and at_least_one_strictly:
                is_dominated = True
                break
        
        if not is_dominated:
            pareto_front.append(sol_A)
    
    print(f"\n帕累托前沿包含 {len(pareto_front)} 个非支配解")
    return pareto_front


# ================================================================
# 决策权重与最优解选择
# ================================================================
def select_best_solution(pareto_front, weights=None):
    """
    从帕累托前沿中根据权重选择最优解
    
    默认权重：
    - dcpa: 0.40 （安全距离）
    - risk: 0.35 （风险度）
    - steps: 0.25 （避让时间）
    """
    
    if not pareto_front:
        return None, None
    
    if weights is None:
        weights = {
            'dcpa': 0.40,
            'risk': 0.35,
            'steps': 0.25
        }
    
    # 归一化
    def normalize(values):
        min_v, max_v = min(values), max(values)
        if max_v == min_v:
            return np.ones(len(values)) * 0.5
        return np.array([(v - min_v) / (max_v - min_v) for v in values])
    
    dcpas = np.array([s['dcpa'] for s in pareto_front])
    risks = np.array([s['max_risk'] for s in pareto_front])
    steps = np.array([s['steps'] for s in pareto_front])
    
    norm_dcpas = normalize(dcpas)
    norm_risks = normalize(risks)
    norm_steps = normalize(steps)
    
    # 计算加权评分（dcpa是收益项，其余是成本项）
    scores = (
        weights['dcpa'] * norm_dcpas -
        weights['risk'] * norm_risks -
        weights['steps'] * norm_steps
    )
    
    best_idx = np.argmax(scores)
    return pareto_front[best_idx], scores[best_idx]


# ================================================================
# 可视化：车舵协同决策空间
# ================================================================
def visualize_rudder_speed_space(all_results, pareto_front, best_solution):
    """
    3D可视化：展示角度、速度、性能指标的关系
    """
    
    fig = plt.figure(figsize=(15, 5))
    
    # 子图1：角度 vs DCPA，颜色表示速度档位
    ax1 = fig.add_subplot(131)
    
    gear_colors = {0: 'red', 1: 'orange', 2: 'green'}
    gear_labels = {0: '前进三', 1: '前进二', 2: '前进一'}
    
    for gear_idx in [0, 1, 2]:
        subset = [r for r in all_results if 
                  GEAR_INDEX.get(list(SPEED_GEARS.keys()).index(r['speed_gear'])) == GEAR_INDEX[gear_idx] 
                  if r['status'] == 1]
        if subset:
            angles = [r['angle'] for r in subset]
            dcpas = [r['dcpa'] for r in subset]
            ax1.scatter(angles, dcpas, c=gear_colors[gear_idx], 
                       label=gear_labels[gear_idx], alpha=0.6, s=50)
    
    # 标记帕累托前沿
    if pareto_front:
        p_angles = [p['angle'] for p in pareto_front]
        p_dcpas = [p['dcpa'] for p in pareto_front]
        ax1.scatter(p_angles, p_dcpas, c='blue', marker='s', 
                   s=100, label='帕累托前沿', edgecolors='black', linewidth=1.5)
    
    # 标记最优解
    if best_solution:
        ax1.scatter([best_solution['angle']], [best_solution['dcpa']], 
                   c='purple', marker='*', s=300, label='最优解', 
                   edgecolors='black', linewidth=2)
    
    ax1.set_xlabel('转向角度 (°)', fontsize=12)
    ax1.set_ylabel('DCPA (m)', fontsize=12)
    ax1.set_title('角度-DCPA关系图', fontsize=14)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 子图2：风险度 vs 避让时间
    ax2 = fig.add_subplot(132)
    
    for gear_idx in [0, 1, 2]:
        subset = [r for r in all_results if 
                  GEAR_INDEX.get(list(SPEED_GEARS.keys()).index(r['speed_gear'])) == GEAR_INDEX[gear_idx]
                  if r['status'] == 1]
        if subset:
            risks = [r['max_risk'] for r in subset]
            steps = [r['steps'] for r in subset]
            ax2.scatter(risks, steps, c=gear_colors[gear_idx], 
                       label=gear_labels[gear_idx], alpha=0.6, s=50)
    
    if pareto_front:
        p_risks = [p['max_risk'] for p in pareto_front]
        p_steps = [p['steps'] for p in pareto_front]
        ax2.scatter(p_risks, p_steps, c='blue', marker='s', 
                   s=100, label='帕累托前沿', edgecolors='black', linewidth=1.5)
    
    if best_solution:
        ax2.scatter([best_solution['max_risk']], [best_solution['steps']], 
                   c='purple', marker='*', s=300, label='最优解', 
                   edgecolors='black', linewidth=2)
    
    ax2.set_xlabel('最大风险度', fontsize=12)
    ax2.set_ylabel('避让步数', fontsize=12)
    ax2.set_title('风险-时间关系图', fontsize=14)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 子图3：帕累托前沿详细标注
    ax3 = fig.add_subplot(133)
    
    if pareto_front:
        for i, sol in enumerate(pareto_front):
            # 映射速度档位到索引
            gear_idx = list(SPEED_GEARS.keys()).index(sol['speed_gear'])
            ax3.scatter([sol['angle']], [sol['dcpa']], 
                       c=gear_colors[gear_idx], s=150, 
                       edgecolors='black', linewidth=1)
            ax3.text(sol['angle'] + 0.5, sol['dcpa'], 
                    f"{sol['angle']}°\n{sol['speed_gear']}", 
                    fontsize=9, ha='left')
    
    if best_solution:
        ax3.scatter([best_solution['angle']], [best_solution['dcpa']], 
                   c='purple', marker='*', s=400, 
                   edgecolors='black', linewidth=2, zorder=10)
    
    ax3.set_xlabel('转向角度 (°)', fontsize=12)
    ax3.set_ylabel('DCPA (m)', fontsize=12)
    ax3.set_title('帕累托前沿标注图', fontsize=14)
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('rudder_speed_coordination_result.png', dpi=150, bbox_inches='tight')
    print("\n可视化结果已保存至: rudder_speed_coordination_result.png")
    plt.show()


# ================================================================
# 轨迹预测与可视化
# ================================================================
def generate_trajectory(angle, speed_gear_idx, list_own, list_tar, steps):
    """
    生成单个方案的预测轨迹
    
    参数:
        angle: 转向角度
        speed_gear_idx: 速度档位索引
        list_own: 本船初始状态 [x, y, heading, ...]
        list_tar: 目标船初始状态 [x, y, heading, ...]
        steps: 仿真步数
    
    返回:
        own_trajectory: 本船轨迹 [(x, y), ...]
        tar_trajectory: 目标船轨迹 [(x, y), ...]
    """
    gear_name, gear_value = GEAR_INDEX[speed_gear_idx]
    
    # 本船轨迹初始化
    own_x, own_y = list_own[0], list_own[1]
    own_heading = list_own[2]
    own_u = list_own[4]  # 前进速度
    
    # 目标船轨迹初始化
    tar_x, tar_y = list_tar[0], list_tar[1]
    tar_heading = list_tar[2]
    tar_u = list_tar[4]
    
    own_trajectory = [(own_x, own_y)]
    tar_trajectory = [(tar_x, tar_y)]
    
    # 简化的轨迹预测（实际应使用MMG模型）
    dt = 1.0  # 时间步长（秒）
    
    # 本船转向：逐渐改变航向到目标角度
    target_heading = own_heading + angle * math.pi / 180
    
    for step in range(steps):
        # 本船运动（简化版）
        # 航向逐渐变化
        heading_diff = target_heading - own_heading
        if abs(heading_diff) > 0.01:
            own_heading += np.sign(heading_diff) * min(abs(heading_diff), 0.02)
        
        # 根据速度档位和航向更新位置
        own_speed = own_u * gear_value / (85.0/60.0)  # 调整速度
        own_x += own_speed * math.sin(own_heading) * dt
        own_y += own_speed * math.cos(own_heading) * dt
        own_trajectory.append((own_x, own_y))
        
        # 目标船运动（保持直线）
        tar_x += tar_u * math.sin(tar_heading) * dt
        tar_y += tar_u * math.cos(tar_heading) * dt
        tar_trajectory.append((tar_x, tar_y))
    
    return own_trajectory, tar_trajectory


def visualize_trajectories(list_own_initial, list_tar_initial, pareto_front, 
                           best_solution, bank_p1, bank_p2):
    """
    可视化船舶位置和各个方案的预测轨迹
    """
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # 颜色映射
    gear_colors = {0: 'red', 1: 'orange', 2: 'green'}
    gear_labels = {0: '前进三', 1: '前进二', 2: '前进一'}
    
    # 绘制航道边界
    ax.plot([bank_p1[0], bank_p2[0]], [bank_p1[1], bank_p2[1]], 
            'k--', linewidth=2, label='航道边界', alpha=0.5)
    
    # 绘制初始船舶位置
    own_x, own_y = list_own_initial[0], list_own_initial[1]
    tar_x, tar_y = list_tar_initial[0], list_tar_initial[1]
    
    # 本船（蓝色三角形）
    own_heading = list_own_initial[2]
    ship_size = 80
    ax.scatter([own_x], [own_y], c='blue', s=ship_size*3, marker='^', 
              edgecolors='black', linewidth=2, label='本船初始位置', zorder=10)
    
    # 绘制本船航向指示
    arrow_length = 200
    ax.arrow(own_x, own_y, 
            arrow_length * math.sin(own_heading), 
            arrow_length * math.cos(own_heading),
            head_width=50, head_length=80, fc='blue', ec='blue', alpha=0.5)
    
    # 目标船（红色三角形）
    tar_heading = list_tar_initial[2]
    ax.scatter([tar_x], [tar_y], c='red', s=ship_size*3, marker='^', 
              edgecolors='black', linewidth=2, label='目标船初始位置', zorder=10)
    
    # 绘制目标船航向指示
    ax.arrow(tar_x, tar_y, 
            arrow_length * math.sin(tar_heading), 
            arrow_length * math.cos(tar_heading),
            head_width=50, head_length=80, fc='red', ec='red', alpha=0.5)
    
    # 绘制帕累托前沿方案的预测轨迹
    if pareto_front:
        plotted_gears = set()
        
        for i, sol in enumerate(pareto_front):
            gear_idx = list(SPEED_GEARS.keys()).index(sol['speed_gear'])
            
            # 生成轨迹
            own_traj, tar_traj = generate_trajectory(
                sol['angle'], gear_idx, 
                list_own_initial, list_tar_initial, 
                min(sol['steps'], 300)  # 限制显示长度
            )
            
            # 提取坐标
            own_xs = [p[0] for p in own_traj]
            own_ys = [p[1] for p in own_traj]
            
            # 绘制本船轨迹
            label = f"{gear_labels[gear_idx]} ({sol['angle']}°)" if gear_idx not in plotted_gears else None
            ax.plot(own_xs, own_ys, color=gear_colors[gear_idx], 
                   linewidth=1.5, alpha=0.6, label=label)
            
            plotted_gears.add(gear_idx)
            
            # 标注轨迹终点
            ax.scatter([own_xs[-1]], [own_ys[-1]], 
                      c=gear_colors[gear_idx], s=40, marker='o', 
                      edgecolors='black', linewidth=0.5, alpha=0.8)
        
        # 绘制目标船轨迹（只绘制一次）
        if pareto_front:
            sol = pareto_front[0]
            gear_idx = list(SPEED_GEARS.keys()).index(sol['speed_gear'])
            _, tar_traj = generate_trajectory(
                sol['angle'], gear_idx, 
                list_own_initial, list_tar_initial, 
                min(sol['steps'], 300)
            )
            tar_xs = [p[0] for p in tar_traj]
            tar_ys = [p[1] for p in tar_traj]
            ax.plot(tar_xs, tar_ys, 'r--', linewidth=2, alpha=0.5, label='目标船轨迹')
            ax.scatter([tar_xs[-1]], [tar_ys[-1]], c='red', s=60, marker='s', 
                      edgecolors='black', linewidth=1)
    
    # 高亮显示最优方案轨迹
    if best_solution:
        gear_idx = list(SPEED_GEARS.keys()).index(best_solution['speed_gear'])
        own_traj, _ = generate_trajectory(
            best_solution['angle'], gear_idx,
            list_own_initial, list_tar_initial,
            min(best_solution['steps'], 300)
        )
        own_xs = [p[0] for p in own_traj]
        own_ys = [p[1] for p in own_traj]
        
        # 用粗线突出显示最优轨迹
        ax.plot(own_xs, own_ys, color='purple', linewidth=3, alpha=0.9,
               label=f'最优方案: {best_solution["angle"]}°, {best_solution["speed_gear"]}',
               linestyle='-', zorder=5)
        
        # 标注最优方案终点
        ax.scatter([own_xs[-1]], [own_ys[-1]], c='purple', s=200, marker='*',
                  edgecolors='black', linewidth=2, zorder=10)
    
    ax.set_xlabel('X坐标 (m)', fontsize=12)
    ax.set_ylabel('Y坐标 (m)', fontsize=12)
    ax.set_title('车舵协同避让轨迹预测图', fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.axis('equal')
    
    plt.tight_layout()
    plt.savefig('trajectory_prediction.png', dpi=150, bbox_inches='tight')
    print("\n轨迹预测图已保存至: trajectory_prediction.png")
    plt.show()


# ================================================================
# 主程序示例
# ================================================================
if __name__ == '__main__':
    
    print("\n" + "=" * 80)
    print("车舵协同避让决策优化系统 Demo".center(80))
    print("=" * 80)
    
    # 模拟参数（实际使用时替换为你的真实数据）
    SHIP_BREADTH = 32.5
    RR1, RR2 = 1.0 * SHIP_BREADTH, 4 * SHIP_BREADTH
    RISK_THRESHOLD = 0.75
    ORIGINAL_COURSE = 101 * math.pi / 180
    
    # 航道边界（示例）
    p1 = np.array([13126214.0, 4714473.0])
    p2 = np.array([13127587.0, 4714219.0])
    
    # 本船和目标船初始状态（示例）
    list_own_initial = [13123293.2, 4715126.8, 1.754, 0.017, 5.352, -9.3e-06]
    list_tar_initial = [13126113.5, 4714630.6, 4.904, 0.0, 5.771, 0.0]
    list_own_ship_params = [0] * 12  # 船舶参数示例
    
    # 步骤1：评估所有车舵组合
    all_results, successful_results = optimize_rudder_speed_coordination(
        angle_range=(5, 31),       # 角度范围
        speed_gears=(0, 1, 2),     # 全部三个速度档位
        model='meet',
        list_own=list_own_initial,
        list_tar=list_tar_initial,
        list_own_ship_initial=list_own_ship_params,
        deep=23.0,
        bank_p1=p1,
        bank_p2=p2,
        RR1=RR1,
        RR2=RR2,
        U_threshold=RISK_THRESHOLD,
        original_course=ORIGINAL_COURSE
    )
    
    # 步骤2：帕累托前沿筛选
    print("\n正在进行帕累托前沿筛选...")
    pareto_front = find_pareto_front_multi_objective(successful_results)
    
    # 打印帕累托前沿
    if pareto_front:
        print("\n" + "=" * 80)
        print("帕累托前沿解集（非支配解）")
        print("=" * 80)
        print(f"{'序号':<6}{'角度(°)':<10}{'速度档位':<12}{'DCPA(m)':<12}"
              f"{'风险度':<12}{'步数':<10}")
        print("-" * 80)
        for i, sol in enumerate(pareto_front, 1):
            print(f"{i:<6}{sol['angle']:<10}{sol['speed_gear']:<12}"
                  f"{sol['dcpa']:<12.1f}{sol['max_risk']:<12.4f}"
                  f"{sol['steps']:<10}")
    
    # 步骤3：加权决策
    print("\n正在进行加权决策...")
    decision_weights = {
        'dcpa': 0.40,
        'risk': 0.35,
        'steps': 0.25
    }
    
    best_solution, best_score = select_best_solution(pareto_front, decision_weights)
    
    if best_solution:
        print("\n" + "=" * 80)
        print("最优车舵协同方案".center(80))
        print("=" * 80)
        print(f"  推荐转向角度: {best_solution['angle']}°")
        print(f"  推荐速度档位: {best_solution['speed_gear']} "
              f"({best_solution['speed_value']:.3f} m/s)")
        print(f"  预期DCPA: {best_solution['dcpa']:.1f} m")
        print(f"  最大风险度: {best_solution['max_risk']:.4f}")
        print(f"  避让步数: {best_solution['steps']}")
        print(f"  综合评分: {best_score:.4f}")
        print("=" * 80)
    
    # 步骤4：可视化
    print("\n正在生成可视化结果...")
    visualize_rudder_speed_space(all_results, pareto_front, best_solution)
    
    # 步骤5：生成轨迹预测图
    print("\n正在生成轨迹预测图...")
    visualize_trajectories(list_own_initial, list_tar_initial, pareto_front, 
                          best_solution, p1, p2)
    
    print("\n" + "=" * 80)
    print("Demo运行完成！".center(80))
    print("=" * 80)
    print("\n说明：")
    print("1. 本Demo使用简化的仿真模型进行演示")
    print("2. 实际使用时，需要将评估函数替换为您的完整仿真代码")
    print("3. 特别注意修改 list_own_ship_initial[11] 来控制速度档位")
    print("4. 可以调整权重来适应不同的决策偏好")
    print("5. 生成了两张图：决策空间分析图和轨迹预测图")
