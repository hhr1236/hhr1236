"""
最优改向角选择模块

这个模块提供了多种策略来从一组安全的改向角中选择最优的角度。
主要考虑以下几个优化目标：

1. 最小改向角策略：选择改向幅度最小的角度，减少船舶操纵负担
2. 最大安全裕度策略：选择距离危险边界最远的角度
3. 最快复航策略：选择能够最快恢复到原航向的角度
4. 综合评分策略：综合考虑多个因素的加权评分

作者：根据问题需求设计
"""

import numpy as np
from numba import njit
from typing import List, Tuple, Optional
from math import pi, sin, cos, sqrt, exp


@njit
def calculate_proximity_risk(R_R, RR1, RR2):
    """计算静态邻近风险 U_p"""
    if R_R <= RR1:
        return 1.0
    elif R_R > RR2:
        return 0.0
    else:
        sin_arg = (pi / (RR2 - RR1)) * (R_R - (RR1 + RR2) / 2.0)
        return 0.5 - 0.5 * sin(sin_arg)


@njit
def calculate_dynamic_weight(v_n, c=1.0):
    """计算动态调制权重 W"""
    return exp(c * v_n)


@njit
def calculate_approach_velocity(ship_motion, bank_line_p1, bank_line_p2):
    """计算法向接近速度 v_n"""
    Dx = bank_line_p2[0] - bank_line_p1[0]
    Dy = bank_line_p2[1] - bank_line_p1[1]
    Nx, Ny = Dy, -Dx
    norm_N = sqrt(Nx ** 2 + Ny ** 2)
    if norm_N == 0:
        return 0.0
    nx, ny = Nx / norm_N, Ny / norm_N

    psi_nav = ship_motion[2]
    u_sway = ship_motion[3]
    v_surge = ship_motion[4]
    psi_math = (pi / 2) - psi_nav
    Vx = v_surge * cos(psi_math) - u_sway * sin(psi_math)
    Vy = v_surge * sin(psi_math) + u_sway * cos(psi_math)
    v_n_calc = Vx * nx + Vy * ny
    return v_n_calc


@njit
def point_to_line_distance_numba(point_x, point_y, line_m, line_b):
    """Numba兼容的点到直线距离计算"""
    A = line_m
    B = -1.0
    C = line_b
    d = abs(A * point_x + B * point_y + C) / sqrt(A ** 2 + B ** 2)
    return d


@njit
def line_equation_numba(point1, point2):
    """Numba兼容的直线方程计算"""
    x1, y1 = point1[0], point1[1]
    x2, y2 = point2[0], point2[1]
    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1
    return m, b


@njit
def CPA(own_ship, tar_ship):
    """
    计算TCPA和DCPA
    
    参数:
        own_ship: 本船状态 [x, y, course, u, v, r]
        tar_ship: 目标船状态 [x, y, course, u, v, r]
    
    返回:
        (TCPA, DCPA): 最近会遇时间和最近会遇距离
    """
    x_own = own_ship[0]       # 本船坐标
    y_own = own_ship[1]
    c_own = own_ship[2]
    u_own = own_ship[3]
    v_own = own_ship[4]
    r_own = own_ship[5]

    x_tar = tar_ship[0]       # 他船坐标
    y_tar = tar_ship[1]
    c_tar = tar_ship[2]
    u_tar = tar_ship[3]
    v_tar = tar_ship[4]
    r_tar = tar_ship[5]

    delta_x = x_tar - x_own
    delta_y = y_tar - y_own
    D = sqrt(delta_x**2 + delta_y**2)
    
    if D < 1e-6:  # 避免除零
        return 0.0, 0.0
    
    if delta_y >= 0:
        TB = sin(delta_x / D) if abs(delta_x / D) <= 1.0 else pi / 2
    else:
        TB = pi - (sin(delta_x / D) if abs(delta_x / D) <= 1.0 else pi / 2)
    if TB < 0:
        TB += 2 * pi

    delta_u = v_tar * sin(c_tar) - v_own * sin(c_own)
    delta_v = v_tar * cos(c_tar) - v_own * cos(c_own)
    RV = sqrt(delta_u**2 + delta_v**2)
    
    if RV < 1e-6:  # 相对速度接近零
        return float('inf'), D
    
    if delta_v >= 0:
        RC = sin(delta_u / RV) if abs(delta_u / RV) <= 1.0 else pi / 2
    else:
        RC = pi - (sin(delta_u / RV) if abs(delta_u / RV) <= 1.0 else pi / 2)
    if RC < 0:
        RC += 2 * pi

    TCPA = -(delta_x * delta_u + delta_y * delta_v) / (delta_u**2 + delta_v**2)
    
    if TCPA < 0:  # 如果TCPA为负，表示目标船正在远离
        DCPA = D
    else:
        DCPA = sqrt((delta_x + delta_u * TCPA)**2 + (delta_y + delta_v * TCPA)**2)

    return TCPA, round(DCPA, 1)


# ============================================================================
# 策略1: 最小改向角策略
# ============================================================================

def strategy_minimal_deviation(safe_angles: List[int]) -> Tuple[int, str]:
    """
    策略1: 最小改向角策略
    
    选择改向幅度最小的安全角度。这个策略的优点是：
    - 减少船舶操纵负担
    - 降低能耗
    - 便于船员操作
    - 减少对正常航行的干扰
    
    参数:
        safe_angles: 所有安全的改向角度列表
    
    返回:
        (最优角度, 策略说明)
    """
    if not safe_angles:
        return None, "无可用的安全角度"
    
    # 假设0度是正常航向，选择偏离最小的角度
    optimal_angle = min(safe_angles)
    
    explanation = f"""
    【最小改向角策略】
    - 选择的最优角度: {optimal_angle}度
    - 原理: 选择改向幅度最小的角度，减少操纵负担
    - 优点: 操作简单，能耗最低，对正常航行干扰最小
    - 适用场景: 当所有安全角度的安全裕度都足够时
    """
    
    return optimal_angle, explanation


# ============================================================================
# 策略2: 中间值策略（最大安全裕度）
# ============================================================================

def strategy_maximum_margin(safe_angles: List[int]) -> Tuple[int, str]:
    """
    策略2: 最大安全裕度策略
    
    如果安全角度形成一个连续区间，选择区间的中间值。
    这个策略的优点是：
    - 对不确定性有最大的容错空间
    - 即使实际改向略有偏差，仍然安全
    - 在避让过程中有更多调整余地
    
    参数:
        safe_angles: 所有安全的改向角度列表
    
    返回:
        (最优角度, 策略说明)
    """
    if not safe_angles:
        return None, "无可用的安全角度"
    
    # 检查是否形成连续区间
    safe_angles_sorted = sorted(safe_angles)
    is_continuous = all(
        safe_angles_sorted[i+1] - safe_angles_sorted[i] == 1 
        for i in range(len(safe_angles_sorted)-1)
    )
    
    if is_continuous:
        # 连续区间，选择中间值
        optimal_angle = safe_angles_sorted[len(safe_angles_sorted) // 2]
        explanation = f"""
        【最大安全裕度策略 - 连续区间】
        - 选择的最优角度: {optimal_angle}度
        - 安全区间: [{safe_angles_sorted[0]}°, {safe_angles_sorted[-1]}°]
        - 原理: 选择区间中点，获得最大的安全裕度
        - 优点: 对操作误差和环境扰动有最大容错能力
        - 左右安全裕度: ±{optimal_angle - safe_angles_sorted[0]}度
        """
    else:
        # 非连续区间，选择最长连续段的中间值
        max_segment = []
        current_segment = [safe_angles_sorted[0]]
        
        for i in range(1, len(safe_angles_sorted)):
            if safe_angles_sorted[i] - safe_angles_sorted[i-1] == 1:
                current_segment.append(safe_angles_sorted[i])
            else:
                if len(current_segment) > len(max_segment):
                    max_segment = current_segment.copy()
                current_segment = [safe_angles_sorted[i]]
        
        if len(current_segment) > len(max_segment):
            max_segment = current_segment
        
        optimal_angle = max_segment[len(max_segment) // 2]
        explanation = f"""
        【最大安全裕度策略 - 非连续区间】
        - 选择的最优角度: {optimal_angle}度
        - 最长连续安全段: [{max_segment[0]}°, {max_segment[-1]}°]
        - 原理: 在最长的连续安全段中选择中点
        - 优点: 在该段内有最大的操作灵活性
        - 安全裕度: ±{len(max_segment)//2}度
        """
    
    return optimal_angle, explanation


# ============================================================================
# 策略3: 最快复航策略
# ============================================================================

def strategy_fastest_return(safe_angles: List[int], original_course: float) -> Tuple[int, str]:
    """
    策略3: 最快复航策略
    
    选择避让后能够最快恢复到原定航向的角度。
    这个策略考虑：
    - 改向角度对后续复航的影响
    - 较大的改向角可能提供更快的危险解除
    - 综合考虑避让时间和复航时间
    
    参数:
        safe_angles: 所有安全的改向角度列表
        original_course: 原定航向（弧度）
    
    返回:
        (最优角度, 策略说明)
    """
    if not safe_angles:
        return None, "无可用的安全角度"
    
    # 对于超越和交叉情况，较大的改向角通常能更快解除危险
    # 但也要避免过度改向
    safe_angles_sorted = sorted(safe_angles)
    
    # 选择区间的75%分位点（偏向较大改向，但不是最大）
    index_75 = int(len(safe_angles_sorted) * 0.75)
    if index_75 >= len(safe_angles_sorted):
        index_75 = len(safe_angles_sorted) - 1
    
    optimal_angle = safe_angles_sorted[index_75]
    
    explanation = f"""
    【最快复航策略】
    - 选择的最优角度: {optimal_angle}度
    - 原理: 选择较大的改向角以更快解除危险
    - 位置: 安全区间的75%分位点
    - 优点: 能更快拉开与目标船的距离，尽早恢复原航向
    - 考虑: 在保持安全的前提下，倾向于较大改向
    - 适用场景: 需要尽快完成避让动作时
    """
    
    return optimal_angle, explanation


# ============================================================================
# 策略4: 综合评分策略（推荐）
# ============================================================================

def strategy_comprehensive_score(
    safe_angles: List[int],
    ship_state: List[float],
    target_state: List[float],
    bank_p1: np.ndarray,
    bank_p2: np.ndarray,
    RR1: float,
    RR2: float,
    original_course: float,
    weights: Optional[dict] = None
) -> Tuple[int, str, dict]:
    """
    策略4: 综合评分策略（推荐使用）
    
    综合考虑多个因素，为每个安全角度计算评分：
    1. 改向成本（越小越好）- 改向角度越小，操纵成本越低
    2. 岸壁安全裕度（离岸距离越大越好）- 考虑改向角度大会更靠近边界的影响
    3. 避让效果（基于TCPA和DCPA）- 使用TCPA和DCPA评估避让效果
    
    参数:
        safe_angles: 所有安全的改向角度列表
        ship_state: 当前船舶状态 [x, y, course, u, v, r]
        target_state: 目标船状态 [x, y, course, u, v, r]
        bank_p1, bank_p2: 岸线两点
        RR1, RR2: 岸壁风险参数
        original_course: 原定航向
        weights: 各因素权重字典，默认为 {
            'deviation': 0.35,  # 改向成本
            'bank_safety': 0.35,  # 岸壁安全
            'collision_safety': 0.30  # 碰撞安全（基于TCPA/DCPA）
        }
    
    返回:
        (最优角度, 策略说明, 详细评分字典)
    """
    if not safe_angles:
        return None, "无可用的安全角度", {}
    
    # 默认权重（去掉连续性，重新分配权重）
    if weights is None:
        weights = {
            'deviation': 0.35,
            'bank_safety': 0.35,
            'collision_safety': 0.30
        }
    
    scores = {}
    line_m, line_b = line_equation_numba(bank_p1, bank_p2)
    
    # 预先计算一些参数
    max_angle = max(safe_angles)
    min_angle = min(safe_angles)
    
    for angle in safe_angles:
        score_details = {}
        
        # 1. 改向成本评分（越小越好）
        # 归一化到[0,1]，最小改向得1分，最大改向得0分
        if max_angle > min_angle:
            deviation_score = 1.0 - (angle - min_angle) / (max_angle - min_angle)
        else:
            deviation_score = 1.0
        score_details['deviation'] = deviation_score
        
        # 2. 岸壁安全裕度评分（考虑改向角度大会更靠近边界）
        # 计算当前位置到岸线的距离
        dist_to_bank = point_to_line_distance_numba(
            ship_state[0], ship_state[1], line_m, line_b
        )
        
        # 考虑改向角度对离岸距离的影响：
        # 改向角度越大，理论上会更靠近边界，需要在评分中体现这种权衡
        # 使用一个调节因子：较大的改向角会降低岸壁安全评分
        angle_penalty = (angle - min_angle) / (max_angle - min_angle) if max_angle > min_angle else 0.0
        adjusted_dist = dist_to_bank * (1.0 - 0.3 * angle_penalty)  # 最多降低30%
        
        # 归一化：RR1为0分，RR2为1分，超过RR2更好
        bank_safety_score = min(1.0, max(0.0, (adjusted_dist - RR1) / (RR2 - RR1)))
        score_details['bank_safety'] = bank_safety_score
        
        # 3. 避让效果评分（基于TCPA和DCPA）
        # 使用CPA函数计算TCPA和DCPA
        tcpa, dcpa = CPA(ship_state, target_state)
        
        # DCPA评分：DCPA越大越好
        # 假设安全DCPA阈值为RR1的2倍
        safe_dcpa_threshold = RR1 * 2.0
        if dcpa >= safe_dcpa_threshold:
            dcpa_score = 1.0
        else:
            dcpa_score = dcpa / safe_dcpa_threshold
        
        # TCPA评分：TCPA越大越好（有更多时间避让）
        # 假设期望TCPA至少为300秒
        desired_tcpa = 300.0
        if tcpa < 0:  # 目标船正在远离
            tcpa_score = 1.0
        elif tcpa >= desired_tcpa:
            tcpa_score = 1.0
        else:
            tcpa_score = tcpa / desired_tcpa
        
        # 综合TCPA和DCPA评分（DCPA权重更高）
        collision_safety_score = 0.6 * dcpa_score + 0.4 * tcpa_score
        score_details['collision_safety'] = collision_safety_score
        score_details['tcpa'] = tcpa
        score_details['dcpa'] = dcpa
        
        # 计算加权总分
        total_score = (
            weights['deviation'] * deviation_score +
            weights['bank_safety'] * bank_safety_score +
            weights['collision_safety'] * collision_safety_score
        )
        
        scores[angle] = {
            'total': total_score,
            'details': score_details
        }
    
    # 选择总分最高的角度
    optimal_angle = max(scores.keys(), key=lambda a: scores[a]['total'])
    optimal_score = scores[optimal_angle]
    
    explanation = f"""
    【综合评分策略】（推荐）
    - 选择的最优角度: {optimal_angle}度
    - 总评分: {optimal_score['total']:.3f}
    
    评分组成:
    - 改向成本评分: {optimal_score['details']['deviation']:.3f} (权重{weights['deviation']})
      → 越小的改向角得分越高
    - 岸壁安全评分: {optimal_score['details']['bank_safety']:.3f} (权重{weights['bank_safety']})
      → 离岸距离越大得分越高，同时考虑大改向角更靠近边界的影响
    - 避让效果评分: {optimal_score['details']['collision_safety']:.3f} (权重{weights['collision_safety']})
      → 基于TCPA={optimal_score['details']['tcpa']:.1f}秒 和 DCPA={optimal_score['details']['dcpa']:.1f}米
      → DCPA越大、TCPA越大，避让效果越好
    
    原理: 综合平衡多个优化目标，找到最佳折中方案
    特点: 
    - 使用TCPA/DCPA精确评估避让效果
    - 考虑改向角度与岸壁距离的权衡关系
    - 可通过调整权重适应不同场景
    """
    
    return optimal_angle, explanation, scores


# ============================================================================
# 统一接口函数
# ============================================================================

def select_optimal_angle(
    safe_angles: List[int],
    strategy: str = 'comprehensive',
    **kwargs
) -> Tuple[Optional[int], str, Optional[dict]]:
    """
    统一的最优角度选择接口
    
    参数:
        safe_angles: 所有安全的改向角度列表
        strategy: 选择策略，可选值:
            - 'minimal': 最小改向角策略
            - 'margin': 最大安全裕度策略
            - 'fastest': 最快复航策略
            - 'comprehensive': 综合评分策略（推荐，默认）
        **kwargs: 传递给具体策略的额外参数
    
    返回:
        (最优角度, 策略说明, 额外信息字典)
    """
    if not safe_angles:
        return None, "错误: 没有可用的安全角度", None
    
    if strategy == 'minimal':
        optimal, explanation = strategy_minimal_deviation(safe_angles)
        return optimal, explanation, None
    
    elif strategy == 'margin':
        optimal, explanation = strategy_maximum_margin(safe_angles)
        return optimal, explanation, None
    
    elif strategy == 'fastest':
        original_course = kwargs.get('original_course', 101 * pi / 180)
        optimal, explanation = strategy_fastest_return(safe_angles, original_course)
        return optimal, explanation, None
    
    elif strategy == 'comprehensive':
        required_keys = ['ship_state', 'target_state', 'bank_p1', 'bank_p2', 'RR1', 'RR2']
        for key in required_keys:
            if key not in kwargs:
                return None, f"错误: 综合评分策略需要参数 {key}", None
        
        optimal, explanation, scores = strategy_comprehensive_score(
            safe_angles,
            kwargs['ship_state'],
            kwargs['target_state'],
            kwargs['bank_p1'],
            kwargs['bank_p2'],
            kwargs['RR1'],
            kwargs['RR2'],
            kwargs.get('original_course', 101 * pi / 180),
            kwargs.get('weights', None)
        )
        return optimal, explanation, scores
    
    else:
        return None, f"错误: 未知的策略 '{strategy}'", None


# ============================================================================
# 策略比较工具
# ============================================================================

def compare_all_strategies(
    safe_angles: List[int],
    ship_state: List[float],
    target_state: List[float],
    bank_p1: np.ndarray,
    bank_p2: np.ndarray,
    RR1: float,
    RR2: float,
    original_course: float = 101 * pi / 180
) -> dict:
    """
    比较所有策略的结果，帮助决策
    
    返回:
        包含所有策略结果的字典
    """
    results = {}
    
    # 策略1: 最小改向角
    angle1, exp1 = strategy_minimal_deviation(safe_angles)
    results['minimal'] = {'angle': angle1, 'explanation': exp1}
    
    # 策略2: 最大安全裕度
    angle2, exp2 = strategy_maximum_margin(safe_angles)
    results['margin'] = {'angle': angle2, 'explanation': exp2}
    
    # 策略3: 最快复航
    angle3, exp3 = strategy_fastest_return(safe_angles, original_course)
    results['fastest'] = {'angle': angle3, 'explanation': exp3}
    
    # 策略4: 综合评分
    angle4, exp4, scores4 = strategy_comprehensive_score(
        safe_angles, ship_state, target_state,
        bank_p1, bank_p2, RR1, RR2, original_course
    )
    results['comprehensive'] = {
        'angle': angle4,
        'explanation': exp4,
        'scores': scores4
    }
    
    return results
