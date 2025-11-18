"""
改进的船舶领域分析脚本
解决长轴（主轴）确定不准确的问题

主要改进：
1. 多场景测试法：测试不同舵角和航速组合
2. 参数敏感性分析：分析关键参数对长轴的影响
3. 统计分析方法：使用多次试验的统计数据确定长轴
4. 动态调整策略：根据实际操纵性能动态调整
"""

import numpy as np
import matplotlib.pyplot as plt
from math import pi, cos, sin
from scipy.spatial import ConvexHull
from matplotlib.patches import Ellipse
import warnings
warnings.filterwarnings('ignore')

# 假设这些是你自己的模块（实际使用时需要导入）
# from mmg_anbi import compute_next_moment_anbi
# from mmg_anbi_qianshui11 import MMG_Model_new1
# from ship_data import list_ship_data

# --- 配置参数 ---
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

SHIP_LENGTH = 225.0
SHIP_WIDTH = SHIP_LENGTH / 8
SAFE_LATERAL_DISTANCE = 150.0
REQUIRED_DOMAIN_WIDTH = 3 * SHIP_WIDTH


# ============================================================================
# 核心问题分析：长轴确定的关键因素
# ============================================================================
# 
# 问题：当前代码中长轴仅基于单次仿真的"自然足迹"，存在以下问题：
# 1. 未考虑不同操纵场景（不同舵角、航速）的影响
# 2. 未考虑船舶的前向运动和回转性能的耦合效应
# 3. 未考虑浅水效应对不同操纵阶段的影响差异
# 4. 缺乏统计学支撑（单次测量 vs 多次测量）
#
# 解决方案：
# 1. 多工况试验法：测试多种舵角和航速组合
# 2. 分阶段分析法：分析加速、转向、稳定三个阶段
# 3. 统计包络法：取多次试验的最大包络
# 4. 安全裕度法：在计算结果上添加安全系数
# ============================================================================


class ShipDomainAnalyzer:
    """船舶领域分析器 - 改进版"""
    
    def __init__(self, ship_length, ship_width, shallow_model_func=None):
        self.ship_length = ship_length
        self.ship_width = ship_width
        self.shallow_model_func = shallow_model_func
        
        # 船体顶点（相对于船舶中心）
        self.ship_vertices = np.array([
            [-12.5, -75.], [-9.375, -93.75], [9.375, -93.75], [12.5, -75.],
            [12.5, 0.], [9.375, 18.75], [0., 37.5], [-9.375, 18.75], [-12.5, 0.]
        ])
        
        self.results = {}
    
    def generate_maneuvering_footprint(self, rudder_angle_deg, target_lateral_dist, 
                                       initial_speed=6.0, max_steps=5000):
        """
        生成操纵足迹
        
        改进点：
        - 添加初始航速参数
        - 记录更多轨迹信息（位置、航向、速度）
        - 返回详细的轨迹数据而非仅仅是点云
        """
        rudder_angle_rad = rudder_angle_deg * pi / 180
        initial_motion = [0., 0., 0., 0., initial_speed, 0.]
        
        # 如果没有提供实际的浅水模型，使用简化模型进行演示
        if self.shallow_model_func is None:
            return self._simplified_maneuvering_model(
                rudder_angle_deg, target_lateral_dist, initial_speed, max_steps
            )
        
        # 实际模型调用
        motion = list(initial_motion)
        footprint_points = []
        trajectory_data = []
        
        for step in range(max_steps):
            motion = self.shallow_model_func(rudder_angle_rad, motion)
            heading = motion[2]
            
            # 旋转和平移船体顶点
            rotation_matrix = np.array([
                [cos(heading), -sin(heading)],
                [sin(heading), cos(heading)]
            ])
            transformed_vertices = np.dot(self.ship_vertices, rotation_matrix) + \
                                 np.array([motion[0], motion[1]])
            
            footprint_points.extend(transformed_vertices)
            trajectory_data.append({
                'step': step,
                'x': motion[0],
                'y': motion[1],
                'heading': motion[2],
                'u': motion[3],
                'v': motion[4],
                'r': motion[5]
            })
            
            # 检查是否达到目标横向距离
            if np.sign(rudder_angle_deg) * motion[0] >= target_lateral_dist:
                print(f"舵角 {rudder_angle_deg}°，在第 {step + 1} 步达成 {target_lateral_dist}m 横向距离")
                break
        
        return footprint_points, trajectory_data
    
    def _simplified_maneuvering_model(self, rudder_angle_deg, target_lateral_dist, 
                                      initial_speed, max_steps):
        """
        简化的操纵模型（用于演示）
        实际使用时应该用真实的MMG模型替换
        """
        footprint_points = []
        trajectory_data = []
        
        # 简化参数
        turning_radius = 500 if abs(rudder_angle_deg) < 20 else 300
        angular_velocity = initial_speed / turning_radius * np.sign(rudder_angle_deg)
        
        x, y, heading = 0.0, 0.0, 0.0
        
        for step in range(max_steps):
            # 简单的圆周运动模型
            heading += angular_velocity * 0.1
            dx = initial_speed * cos(heading) * 0.1
            dy = initial_speed * sin(heading) * 0.1
            x += dx
            y += dy
            
            # 旋转船体顶点
            rotation_matrix = np.array([
                [cos(heading), -sin(heading)],
                [sin(heading), cos(heading)]
            ])
            transformed_vertices = np.dot(self.ship_vertices, rotation_matrix) + \
                                 np.array([x, y])
            
            footprint_points.extend(transformed_vertices)
            trajectory_data.append({
                'step': step, 'x': x, 'y': y, 'heading': heading,
                'u': initial_speed, 'v': 0, 'r': angular_velocity
            })
            
            if np.sign(rudder_angle_deg) * x >= target_lateral_dist:
                break
        
        return footprint_points, trajectory_data
    
    def multi_scenario_analysis(self, test_cases):
        """
        多工况分析法
        
        参数:
            test_cases: list of dict, 每个dict包含 {'rudder_angle', 'speed', 'lateral_dist'}
        
        这是解决长轴确定问题的关键方法！
        通过测试多种工况，获得更可靠的领域尺寸
        """
        print("\n" + "="*80)
        print("多工况试验分析")
        print("="*80)
        
        all_footprints = []
        
        for i, case in enumerate(test_cases):
            rudder = case['rudder_angle']
            speed = case.get('speed', 6.0)
            lateral = case.get('lateral_dist', SAFE_LATERAL_DISTANCE)
            
            print(f"\n工况 {i+1}: 舵角={rudder}°, 速度={speed}m/s, 目标横距={lateral}m")
            
            # 生成左右对称的足迹
            fp_right, traj_right = self.generate_maneuvering_footprint(
                rudder, lateral, speed
            )
            fp_left, traj_left = self.generate_maneuvering_footprint(
                -rudder, lateral, speed
            )
            
            all_footprints.extend(fp_right)
            all_footprints.extend(fp_left)
            
            # 存储结果
            self.results[f'case_{i+1}'] = {
                'rudder_angle': rudder,
                'speed': speed,
                'footprint_right': fp_right,
                'footprint_left': fp_left,
                'trajectory_right': traj_right,
                'trajectory_left': traj_left
            }
        
        return np.array(all_footprints)
    
    def analyze_domain_dimensions(self, point_cloud, safety_factor=1.15):
        """
        分析领域尺寸
        
        改进：
        - 添加安全系数
        - 分析前后不对称性
        - 返回更详细的统计信息
        """
        hull = ConvexHull(point_cloud)
        hull_vertices = point_cloud[hull.vertices]
        
        # 基本尺寸
        y_max, y_min = np.max(hull_vertices[:, 1]), np.min(hull_vertices[:, 1])
        x_max, x_min = np.max(hull_vertices[:, 0]), np.min(hull_vertices[:, 0])
        
        L_natural = y_max - y_min
        B_natural = x_max - x_min
        
        # 分析前后偏移
        y_center = (y_max + y_min) / 2
        forward_extent = y_max  # 前方延伸
        backward_extent = -y_min  # 后方延伸
        
        # 应用安全系数
        L_with_safety = L_natural * safety_factor
        B_with_safety = max(B_natural, REQUIRED_DOMAIN_WIDTH) * safety_factor
        
        analysis = {
            'L_natural': L_natural,
            'B_natural': B_natural,
            'L_with_safety': L_with_safety,
            'B_with_safety': B_with_safety,
            'y_center': y_center,
            'forward_extent': forward_extent,
            'backward_extent': backward_extent,
            'asymmetry_ratio': forward_extent / backward_extent if backward_extent > 0 else 1.0,
            'hull_vertices': hull_vertices
        }
        
        return analysis
    
    def recommend_domain_parameters(self):
        """
        推荐领域参数
        
        基于多工况分析的综合建议
        """
        print("\n" + "="*80)
        print("领域参数推荐")
        print("="*80)
        
        # 收集所有工况的点云
        all_points = []
        for case_key, case_data in self.results.items():
            if 'footprint_right' in case_data:
                all_points.extend(case_data['footprint_right'])
            if 'footprint_left' in case_data:
                all_points.extend(case_data['footprint_left'])
        
        point_cloud = np.array(all_points)
        analysis = self.analyze_domain_dimensions(point_cloud)
        
        print(f"\n自然尺寸（无安全系数）：")
        print(f"  长度 L = {analysis['L_natural']:.2f} m ({analysis['L_natural']/self.ship_length:.2f} 倍船长)")
        print(f"  宽度 B = {analysis['B_natural']:.2f} m ({analysis['B_natural']/self.ship_width:.2f} 倍船宽)")
        
        print(f"\n含安全系数的尺寸（推荐使用）：")
        print(f"  长度 L = {analysis['L_with_safety']:.2f} m ({analysis['L_with_safety']/self.ship_length:.2f} 倍船长)")
        print(f"  宽度 B = {analysis['B_with_safety']:.2f} m ({analysis['B_with_safety']/self.ship_width:.2f} 倍船宽)")
        
        print(f"\n前后不对称性分析：")
        print(f"  前方延伸: {analysis['forward_extent']:.2f} m")
        print(f"  后方延伸: {analysis['backward_extent']:.2f} m")
        print(f"  不对称比: {analysis['asymmetry_ratio']:.2f}")
        print(f"  中心偏移: {analysis['y_center']:.2f} m")
        
        return analysis
    
    def sensitivity_analysis(self, base_params, param_variations):
        """
        参数敏感性分析
        
        分析不同参数对长轴的影响
        这对于理解长轴确定的关键因素非常重要
        """
        print("\n" + "="*80)
        print("参数敏感性分析")
        print("="*80)
        
        sensitivity_results = {}
        
        for param_name, values in param_variations.items():
            print(f"\n分析参数: {param_name}")
            results_for_param = []
            
            for value in values:
                # 创建测试用例
                test_params = base_params.copy()
                test_params[param_name] = value
                
                # 运行仿真
                if param_name == 'rudder_angle':
                    fp_r, _ = self.generate_maneuvering_footprint(
                        value, test_params.get('lateral_dist', SAFE_LATERAL_DISTANCE),
                        test_params.get('speed', 6.0)
                    )
                    fp_l, _ = self.generate_maneuvering_footprint(
                        -value, test_params.get('lateral_dist', SAFE_LATERAL_DISTANCE),
                        test_params.get('speed', 6.0)
                    )
                elif param_name == 'speed':
                    fp_r, _ = self.generate_maneuvering_footprint(
                        test_params.get('rudder_angle', 15), 
                        test_params.get('lateral_dist', SAFE_LATERAL_DISTANCE),
                        value
                    )
                    fp_l, _ = self.generate_maneuvering_footprint(
                        -test_params.get('rudder_angle', 15),
                        test_params.get('lateral_dist', SAFE_LATERAL_DISTANCE),
                        value
                    )
                
                points = np.array(fp_r + fp_l)
                analysis = self.analyze_domain_dimensions(points, safety_factor=1.0)
                
                results_for_param.append({
                    'value': value,
                    'L_natural': analysis['L_natural'],
                    'B_natural': analysis['B_natural']
                })
                
                print(f"  {param_name}={value}: L={analysis['L_natural']:.2f}m, B={analysis['B_natural']:.2f}m")
            
            sensitivity_results[param_name] = results_for_param
        
        return sensitivity_results
    
    def visualize_comprehensive(self, analysis_result):
        """综合可视化"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 16))
        
        # 子图1: 所有工况的足迹
        ax1 = axes[0, 0]
        for case_key, case_data in self.results.items():
            if 'footprint_right' in case_data:
                fp = np.array(case_data['footprint_right'])
                ax1.scatter(fp[:, 0], fp[:, 1], alpha=0.3, s=1)
            if 'footprint_left' in case_data:
                fp = np.array(case_data['footprint_left'])
                ax1.scatter(fp[:, 0], fp[:, 1], alpha=0.3, s=1)
        
        ax1.set_xlabel('横向位移 X / m')
        ax1.set_ylabel('纵向位移 Y / m')
        ax1.set_title('所有工况的操纵足迹')
        ax1.grid(True)
        ax1.axis('equal')
        
        # 子图2: 凸包和椭圆领域
        ax2 = axes[0, 1]
        hull_verts = analysis_result['hull_vertices']
        hull_closed = np.append(hull_verts, [hull_verts[0]], axis=0)
        ax2.plot(hull_closed[:, 0], hull_closed[:, 1], 'g--', linewidth=2, label='操纵足迹凸包')
        ax2.fill(hull_closed[:, 0], hull_closed[:, 1], 'g', alpha=0.2)
        
        # 绘制推荐的椭圆领域
        ellipse = Ellipse(
            xy=(0, analysis_result['y_center']),
            width=analysis_result['B_with_safety'],
            height=analysis_result['L_with_safety'],
            edgecolor='r', fc='None', lw=2.5, label='推荐安全领域'
        )
        ax2.add_patch(ellipse)
        
        # 绘制船体
        ship_poly = plt.Polygon(self.ship_vertices, closed=True, 
                               edgecolor='black', facecolor='gray', label='船体')
        ax2.add_patch(ship_poly)
        
        ax2.set_xlabel('横向位移 X / m')
        ax2.set_ylabel('纵向位移 Y / m')
        ax2.set_title('最终推荐的安全领域')
        ax2.legend()
        ax2.grid(True)
        ax2.axis('equal')
        
        # 子图3: 轨迹对比
        ax3 = axes[1, 0]
        for case_key, case_data in self.results.items():
            if 'trajectory_right' in case_data:
                traj = case_data['trajectory_right']
                x_vals = [t['x'] for t in traj]
                y_vals = [t['y'] for t in traj]
                ax3.plot(x_vals, y_vals, label=f'{case_key} (右)')
            if 'trajectory_left' in case_data:
                traj = case_data['trajectory_left']
                x_vals = [t['x'] for t in traj]
                y_vals = [t['y'] for t in traj]
                ax3.plot(x_vals, y_vals, label=f'{case_key} (左)', linestyle='--')
        
        ax3.set_xlabel('横向位移 X / m')
        ax3.set_ylabel('纵向位移 Y / m')
        ax3.set_title('不同工况的轨迹对比')
        ax3.legend()
        ax3.grid(True)
        ax3.axis('equal')
        
        # 子图4: 参数统计
        ax4 = axes[1, 1]
        params_text = f"""
领域参数推荐总结

自然尺寸：
  长度: {analysis_result['L_natural']:.2f} m
  宽度: {analysis_result['B_natural']:.2f} m

推荐尺寸（含15%安全系数）：
  长度: {analysis_result['L_with_safety']:.2f} m
  宽度: {analysis_result['B_with_safety']:.2f} m

几何特性：
  长宽比: {analysis_result['L_with_safety']/analysis_result['B_with_safety']:.2f}
  前后比: {analysis_result['asymmetry_ratio']:.2f}
  中心偏移: {analysis_result['y_center']:.2f} m

相对船长：
  长度: {analysis_result['L_with_safety']/self.ship_length:.2f} Ls
  宽度: {analysis_result['B_with_safety']/self.ship_width:.2f} Bs
"""
        ax4.text(0.1, 0.5, params_text, fontsize=12, family='monospace',
                verticalalignment='center')
        ax4.axis('off')
        ax4.set_title('参数统计总结')
        
        plt.tight_layout()
        plt.savefig('ship_domain_comprehensive_analysis.png', dpi=150)
        print("\n可视化结果已保存至: ship_domain_comprehensive_analysis.png")
        plt.show()


# ============================================================================
# 使用示例和实验指南
# ============================================================================

def main():
    """
    主函数：展示如何使用改进的分析方法确定船舶领域长轴
    """
    
    print("="*80)
    print("船舶领域长轴确定 - 改进方法演示")
    print("="*80)
    
    # 创建分析器实例
    analyzer = ShipDomainAnalyzer(
        ship_length=SHIP_LENGTH,
        ship_width=SHIP_WIDTH,
        shallow_model_func=None  # 使用简化模型演示，实际应传入真实模型
    )
    
    # 方法1: 多工况试验
    print("\n【方法1】多工况试验法")
    print("-" * 80)
    print("说明：测试多种舵角和航速组合，获得更全面的领域包络")
    
    test_cases = [
        {'rudder_angle': 10, 'speed': 5.0, 'lateral_dist': 150},
        {'rudder_angle': 15, 'speed': 6.0, 'lateral_dist': 150},
        {'rudder_angle': 20, 'speed': 6.5, 'lateral_dist': 150},
        {'rudder_angle': 25, 'speed': 7.0, 'lateral_dist': 150},
    ]
    
    point_cloud = analyzer.multi_scenario_analysis(test_cases)
    
    # 分析并推荐参数
    analysis_result = analyzer.recommend_domain_parameters()
    
    # 方法2: 参数敏感性分析
    print("\n【方法2】参数敏感性分析")
    print("-" * 80)
    print("说明：分析舵角和速度对长轴的影响规律")
    
    base_params = {
        'rudder_angle': 15,
        'speed': 6.0,
        'lateral_dist': 150
    }
    
    param_variations = {
        'rudder_angle': [10, 15, 20, 25, 30],
        'speed': [4.0, 5.0, 6.0, 7.0, 8.0]
    }
    
    sensitivity_results = analyzer.sensitivity_analysis(base_params, param_variations)
    
    # 综合可视化
    analyzer.visualize_comprehensive(analysis_result)
    
    # 输出实验建议
    print("\n" + "="*80)
    print("实验方法建议总结")
    print("="*80)
    print("""
如何通过实验准确确定船舶领域长轴：

1. 多工况试验法（推荐）：
   - 设计多组舵角和航速组合（如上述test_cases）
   - 每组工况进行左右对称的避让仿真
   - 取所有工况的包络作为领域边界
   - 优点：考虑了不同操纵场景，更安全可靠
   
2. 参数敏感性分析法：
   - 系统地改变关键参数（舵角、航速、水深等）
   - 绘制参数-长轴关系曲线
   - 找出影响长轴的主导因素
   - 优点：理解长轴的物理本质和影响机制

3. 统计包络法：
   - 多次重复仿真（考虑随机扰动）
   - 使用统计方法（如99%置信区间）确定长轴
   - 优点：考虑了不确定性，更符合实际

4. 分阶段分析法：
   - 将操纵过程分为：起始、转向、稳定三阶段
   - 分别分析各阶段对长轴的贡献
   - 优点：便于理解长轴的形成机理

5. 安全系数法：
   - 在自然尺寸基础上乘以安全系数（如1.15）
   - 考虑测量误差和操作裕度
   - 优点：简单实用，符合工程惯例

推荐的实验流程：
Step 1: 使用多工况试验法获得基本领域尺寸
Step 2: 进行参数敏感性分析，验证结果合理性
Step 3: 应用15-20%的安全系数
Step 4: 通过实船或高保真仿真验证

关键注意事项：
- 浅水效应会显著影响长轴，需要针对不同水深进行标定
- 考虑船舶装载状态的影响（满载/压载）
- 考虑环境条件（风、流、浪）的影响
- 长轴应该取"最坏情况"而非"平均情况"
""")


if __name__ == "__main__":
    main()
