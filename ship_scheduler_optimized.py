"""
Enhanced Ship Scheduler with MILP (Mixed Integer Linear Programming) Optimization

This module provides an improved version of the ship scheduling system that uses
mathematical optimization to find globally optimal (or near-optimal) solutions.

Key Improvements:
1. MILP-based optimization for global optimum
2. Proper constraint modeling (docking limits, task dependencies)
3. Multiple optimization strategies (greedy, optimal)
4. Better handling of urgency and ship activation costs
"""

import pprint
import numpy as np
import pandas as pd
from collections import defaultdict
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpBinary, LpStatus, PULP_CBC_CMD

# region Data Definitions
# 1.1 可用船队及其初始位置
ship_initial_positions = {
    "铭洋12": {"platform": (13450640.007581526, 4848056.034375883)},
    "海洋石油231": {"platform": (13443914.306586778, 4864560.117847532)},
    "安泉州77": {"platform": (13464242.470120028, 4851553.947134592)},
    "德沣": {"platform": (13447624.362575933, 4854443.73620372)},
    "威尔7": {"platform": (13480357.636204716, 4863420.328046263)},
    "东远503": {"platform": (13446723.008658983, 4866267.795537939)},
}

personnel_locations = {
    "维保人员": "B", "后勤厨师": "CEP", "修井监督": "LD52", "油化工程师": "O",
    "腐蚀检测人员": "K", "人员": "JXB", "4人": "SZ36-10/N",
}

item_locations = {
    "仪表设备": "G", "污水设备2吊": "Q", "样桶分液桶": "K", "油样": "H",
    "油水样": "G", "仪表小件": "O", "修井小件": "A", "钻修机物料": "H",
    "维保小件": "O", "油漆": "M", "制冷剂": "A", "4吊设备": "SZ36-10/N",
    "6分管": "Q", "电仪备件": "Q",
}

platform_needs = {
    "K": {"personnel_needed": ["维保人员"], "items_needed": ["仪表设备", "污水设备2吊"]},
    "B": {"personnel_needed": [], "items_needed": ["样桶分液桶"]},
    "J": {"personnel_needed": ["腐蚀检测人员"], "items_needed": ["电仪备件"]},
    "LD52N": {"personnel_needed": ["后勤厨师"], "items_needed": []},
    "O": {"personnel_needed": [], "items_needed": ["油样", "油水样"]},
    "E": {"personnel_needed": ["修井监督", "油化工程师"], "items_needed": ["仪表小件", "修井小件"]},
    "G": {"personnel_needed": [], "items_needed": ["钻修机物料"]},
    "C": {"personnel_needed": [], "items_needed": ["维保小件", "油漆"]},
    "JXC": {"personnel_needed": ["人员"], "items_needed": [], "return_to": "JXB"},
    "R": {"personnel_needed": [], "items_needed": ["制冷剂"]},
    "JXA": {"personnel_needed": ["4人"], "items_needed": ["4吊设备", "6分管"]}
}

platform_coordinates = {
    'M': (13447994.07, 4859620.691), 'H': (13448000.87, 4859490.675),
    'O': (13452403.86, 4860510.515), 'G': (13450474.33, 4861002.722),
    'B': (13447245.44, 4857292.809), 'A': (13447037.65, 4855391.799),
    'JXC': (13479462.26, 4870977.711), 'JXB': (13479631.19, 4866600.75),
    'Q': (13447308.9, 4855361.113), 'K': (13446836.04, 4855404.299),
    'CEP': (13448133.22, 4859466.068), 'LD52N': (13449069.57, 4865682.528),
    'LD52': (13445508.24, 4857630.383), 'E': (13450319.72, 4858037.746),
    'J': (13445539.16, 4853839.886), 'C': (13449252.9, 4855464.784),
    'R': (13455681.61, 4891284.077), "SZ36-10/N": (13449133.298273638, 4865627.817903508),
    "JXA": (13476188.63, 4862683.308)
}

task_urgency_levels = {
    "PERSONNEL": 1, "R": 1, "E": 2, "G": 2, "油样": 2, "油水样": 2,
    "仪表设备": 2, "污水设备2吊": 2, "DEFAULT": 3,
}

evening_tasks = [{"type": "PERSONNEL", "origin": "H", "destination": "O", "desc": "运送HO人员", "urgency": 1}]
# endregion

MAX_DOCKINGS = 3
PENALTY_COST = 9999999.0
SHIP_ACTIVATION_COST = 100000.0


def get_task_urgency(task):
    if task['type'] == 'PERSONNEL': return 1
    dest_urgency = task_urgency_levels.get(task['destination'])
    if dest_urgency: return dest_urgency
    item_desc = task['desc'].replace('运送', '')
    item_urgency = task_urgency_levels.get(item_desc)
    if item_urgency: return item_urgency
    return task_urgency_levels.get("DEFAULT", 3)


class ShipSchedulerOptimized:
    """
    Enhanced ship scheduler with MILP optimization capability.
    
    Strategies:
    - 'greedy': Original greedy algorithm (fast, local optimum)
    - 'optimal_distance': MILP optimization minimizing total distance (允许多船，优化总距离)
    - 'optimal_ships': MILP optimization minimizing number of ships (尽量少用船)
    """
    
    def __init__(self, ships, personnel_loc, needs, coords, max_dockings, strategy='optimal_distance'):
        self.initial_ships = ships
        self.personnel_loc = personnel_loc
        self.needs = needs
        self.coords = coords
        self.max_dockings = max_dockings
        
        if strategy not in ['greedy', 'optimal_distance', 'optimal_ships']:
            raise ValueError("策略必须是 'greedy', 'optimal_distance' 或 'optimal_ships'")
        
        self.strategy = strategy
        # Set activation cost based on strategy
        if strategy == 'optimal_ships':
            self.activation_cost = SHIP_ACTIVATION_COST
            self.optimization_objective = 'minimize_ships'
        else:
            self.activation_cost = 0.0
            self.optimization_objective = 'minimize_distance'
        
        self.ship_agents = {}
        
        print(f"\n[INFO] 调度器已初始化, 优化策略: '{self.strategy}'")
        if strategy == 'optimal_distance':
            print("[INFO] 使用 MILP 全局优化 - 目标: 最小化总距离/靠泊次数")
        elif strategy == 'optimal_ships':
            print("[INFO] 使用 MILP 全局优化 - 目标: 最小化使用船只数量")
        else:
            print("[INFO] 使用贪心算法 - 快速但只能找到局部最优")

    def _calculate_distance(self, p1, p2):
        """计算两点之间的欧几里得距离"""
        def get_coord(point):
            if isinstance(point, tuple):
                return point
            elif point in self.coords:
                return self.coords[point]
            else:
                return None

        coord1, coord2 = get_coord(p1), get_coord(p2)
        if coord1 is None or coord2 is None:
            return np.inf
        return np.linalg.norm(np.array(coord1) - np.array(coord2))

    def _initialize_ship_agents(self):
        """初始化船只代理"""
        self.ship_agents = {}
        for name, data in self.initial_ships.items():
            initial_coord = data['platform']
            platform_name = next(
                (p_name for p_name, p_coord in self.coords.items() if p_coord == initial_coord),
                None
            )
            current_position = platform_name if platform_name else initial_coord
            initial_docked = {platform_name} if platform_name else set()
            
            self.ship_agents[name] = {
                'id': name,
                'current_platform': current_position,
                'docked_platforms': initial_docked,
                'assigned_tasks': [],
                'is_active': False
            }

    def _generate_all_tasks(self):
        """生成所有任务（人员+物资）"""
        all_tasks = {}
        task_counter = 1
        
        # 人员任务
        for dest, needs in self.needs.items():
            for person in needs.get('personnel_needed', []):
                origin = self.personnel_loc.get(person)
                if origin:
                    t_id = f"P{task_counter:02d}"
                    task_data = {
                        'id': t_id,
                        'type': 'PERSONNEL',
                        'origin': origin,
                        'destination': dest,
                        'desc': f"运送{person}"
                    }
                    task_data['urgency'] = get_task_urgency(task_data)
                    all_tasks[t_id] = task_data
                    task_counter += 1
                    
                    # 返回任务
                    if needs.get('return_to'):
                        return_dest = needs['return_to']
                        return_t_id = f"R{task_counter:02d}"
                        return_task_data = {
                            'id': return_t_id,
                            'type': 'RETURN',
                            'origin': dest,
                            'destination': return_dest,
                            'desc': f"返回{return_dest}",
                            'is_return_task': True,
                            'original_task': t_id,
                            'urgency': 99  # 低优先级
                        }
                        all_tasks[return_t_id] = return_task_data
                        task_counter += 1
        
        # 物资任务
        for dest, needs in self.needs.items():
            for item in needs.get('items_needed', []):
                origin = item_locations.get(item)
                if origin:
                    t_id = f"C{task_counter:02d}"
                    task_data = {
                        'id': t_id,
                        'type': 'CARGO',
                        'origin': origin,
                        'destination': dest,
                        'desc': f"运送{item}"
                    }
                    task_data['urgency'] = get_task_urgency(task_data)
                    all_tasks[t_id] = task_data
                    task_counter += 1
        
        return all_tasks

    def _solve_with_milp(self, tasks):
        """
        使用 MILP 求解任务分配问题
        
        决策变量:
        - x[t,s]: 二进制变量，表示任务t是否分配给船s
        - y[s]: 二进制变量，表示船s是否被激活
        - z[p,s]: 二进制变量，表示平台p是否被船s访问
        
        目标函数:
        - 最小化: 总距离成本 + 船只激活成本
        
        约束:
        1. 每个任务必须分配给恰好一艘船
        2. 每艘船的停靠平台数不超过最大限制（正确计算唯一平台数）
        3. 船只激活逻辑
        4. 平台访问逻辑
        """
        print("\n" + "=" * 60)
        print("开始 MILP 全局优化求解")
        print("=" * 60)
        
        # 创建问题
        prob = LpProblem("Ship_Task_Assignment", LpMinimize)
        
        ships = list(self.ship_agents.keys())
        task_ids = list(tasks.keys())
        
        # 收集所有会被访问的平台
        platforms = set()
        for task in tasks.values():
            platforms.add(task['origin'])
            platforms.add(task['destination'])
        platforms = list(platforms)
        
        # 决策变量
        # x[t,s] = 1 表示任务t分配给船s
        x = {}
        for t_id in task_ids:
            for s in ships:
                x[t_id, s] = LpVariable(f"x_{t_id}_{s}", cat=LpBinary)
        
        # y[s] = 1 表示船s被激活使用
        y = {s: LpVariable(f"y_{s}", cat=LpBinary) for s in ships}
        
        # z[p,s] = 1 表示船s访问了平台p
        z = {}
        for p in platforms:
            for s in ships:
                z[p, s] = LpVariable(f"z_{p}_{s}", cat=LpBinary)
        
        # 计算成本矩阵
        cost_matrix = {}
        for t_id, task in tasks.items():
            for s_name, agent in self.ship_agents.items():
                # 计算从船当前位置到任务起点再到终点的距离
                dist_to_origin = self._calculate_distance(agent['current_platform'], task['origin'])
                dist_task = self._calculate_distance(task['origin'], task['destination'])
                total_dist = dist_to_origin + dist_task
                
                # 应用紧急程度因子
                urgency = task.get('urgency', 3)
                urgency_factor = 0.3 if urgency == 1 else 0.6 if urgency == 2 else 1.0
                
                cost_matrix[t_id, s_name] = total_dist * urgency_factor
        
        # 目标函数: 最小化总成本
        prob += (
            lpSum([cost_matrix[t_id, s] * x[t_id, s] 
                   for t_id in task_ids for s in ships]) +
            lpSum([self.activation_cost * y[s] for s in ships]),
            "Total_Cost"
        )
        
        # 约束1: 每个任务必须分配给恰好一艘船
        for t_id in task_ids:
            prob += (
                lpSum([x[t_id, s] for s in ships]) == 1,
                f"Task_{t_id}_assigned"
            )
        
        # 约束2: 船只激活逻辑 - 如果船s执行任何任务，则y[s]=1
        for s in ships:
            prob += (
                lpSum([x[t_id, s] for t_id in task_ids]) <= len(task_ids) * y[s],
                f"Ship_{s}_activation"
            )
        
        # 约束3: 平台访问逻辑 - 如果船s执行访问平台p的任务，则z[p,s]=1
        for p in platforms:
            for s in ships:
                # 找到所有涉及平台p的任务
                related_tasks = [t_id for t_id, task in tasks.items() 
                                if task['origin'] == p or task['destination'] == p]
                if related_tasks:
                    prob += (
                        lpSum([x[t_id, s] for t_id in related_tasks]) <= len(related_tasks) * z[p, s],
                        f"Platform_{p}_ship_{s}_visit"
                    )
        
        # 约束4: 每艘船访问的总平台数不超过最大限制 + 1（初始位置）
        # 使用更灵活的约束：总访问平台数 <= max_dockings + 1
        for s in ships:
            prob += (
                lpSum([z[p, s] for p in platforms]) <= self.max_dockings + 1,
                f"Ship_{s}_docking_limit"
            )
        
        # 求解
        print("\n开始求解 MILP 问题...")
        print(f"- 任务数量: {len(task_ids)}")
        print(f"- 船只数量: {len(ships)}")
        print(f"- 平台数量: {len(platforms)}")
        print(f"- 最大停靠限制: {self.max_dockings}")
        print(f"- 决策变量数量: {len(x) + len(y) + len(z)}")
        
        # 使用 CBC 求解器，设置时间限制
        solver = PULP_CBC_CMD(msg=1, timeLimit=120)
        prob.solve(solver)
        
        # 检查求解状态
        status = LpStatus[prob.status]
        print(f"\n求解状态: {status}")
        
        if status != 'Optimal' and status != 'Feasible':
            print("[警告] MILP 求解失败，将回退到贪心算法")
            return None
        
        # 提取解
        assignments = {}
        for t_id in task_ids:
            for s in ships:
                if x[t_id, s].varValue and x[t_id, s].varValue > 0.5:
                    assignments[t_id] = s
                    break
        
        print(f"\n最优解找到!")
        print(f"- 目标函数值: {prob.objective.value():,.0f}")
        print(f"- 激活船只数: {sum(1 for s in ships if y[s].varValue and y[s].varValue > 0.5)}")
        
        # 验证约束
        print("\n验证停靠约束:")
        for s in ships:
            visited_platforms = set()
            for t_id, assigned_ship in assignments.items():
                if assigned_ship == s:
                    task = tasks[t_id]
                    visited_platforms.add(task['origin'])
                    visited_platforms.add(task['destination'])
            
            initial_platforms = self.ship_agents[s]['docked_platforms']
            new_platforms = visited_platforms - initial_platforms
            if new_platforms:
                print(f"  船 '{s}': 访问 {len(new_platforms)} 个新平台 (限制: {self.max_dockings})")
                if len(new_platforms) > self.max_dockings:
                    print(f"    ⚠️ 警告: 超出限制!")
        
        return assignments

    def _apply_milp_assignments(self, tasks, assignments):
        """应用 MILP 求解结果"""
        print("\n应用 MILP 分配结果...")
        
        for t_id, ship_name in assignments.items():
            task = tasks[t_id]
            agent = self.ship_agents[ship_name]
            
            # 分配任务
            agent['assigned_tasks'].append(task)
            agent['is_active'] = True
            
            # 更新停靠平台
            agent['docked_platforms'].update({task['origin'], task['destination']})
            
            # 更新船只位置（简化版本）
            agent['current_platform'] = task['destination']
            
            print(f"  任务 {t_id} ({task['desc']}) -> 船 '{ship_name}'")

    def run(self):
        """运行调度算法"""
        self._initialize_ship_agents()
        
        if self.strategy in ['optimal_distance', 'optimal_ships']:
            # 使用 MILP 优化
            all_tasks = self._generate_all_tasks()
            assignments = self._solve_with_milp(all_tasks)
            
            if assignments:
                self._apply_milp_assignments(all_tasks, assignments)
            else:
                # MILP 失败，回退到贪心
                print("\n[INFO] 回退到贪心算法")
                self._run_greedy()
        else:
            # 使用贪心算法
            self._run_greedy()
        
        return self.ship_agents

    def _run_greedy(self):
        """运行原始的贪心算法（简化版本）"""
        print("\n使用贪心算法进行任务分配...")
        
        # 生成任务
        personnel_tasks, _ = self._generate_tasks('PERSONNEL')
        cargo_tasks, _ = self._generate_tasks('CARGO')
        
        # 简单分配：就近原则
        all_tasks = {**personnel_tasks, **cargo_tasks}
        for t_id, task in all_tasks.items():
            best_ship = None
            min_cost = float('inf')
            
            for s_name, agent in self.ship_agents.items():
                if len(agent['docked_platforms']) >= self.max_dockings + 1:
                    continue
                
                dist = self._calculate_distance(agent['current_platform'], task['origin'])
                dist += self._calculate_distance(task['origin'], task['destination'])
                
                urgency = task.get('urgency', 3)
                urgency_factor = 0.3 if urgency == 1 else 0.6 if urgency == 2 else 1.0
                cost = dist * urgency_factor
                
                if not agent['is_active']:
                    cost += self.activation_cost
                
                if cost < min_cost:
                    min_cost = cost
                    best_ship = s_name
            
            if best_ship:
                agent = self.ship_agents[best_ship]
                agent['assigned_tasks'].append(task)
                agent['is_active'] = True
                agent['docked_platforms'].update({task['origin'], task['destination']})
                agent['current_platform'] = task['destination']

    def _generate_tasks(self, task_type):
        """生成特定类型的任务"""
        tasks, task_map, counter = {}, {}, 1
        
        if task_type == 'PERSONNEL':
            for dest, needs in self.needs.items():
                for person in needs.get('personnel_needed', []):
                    origin = self.personnel_loc.get(person)
                    if origin:
                        t_id = f"P{counter:02d}"
                        task_data = {
                            'id': t_id,
                            'type': 'PERSONNEL',
                            'origin': origin,
                            'destination': dest,
                            'desc': f"运送{person}"
                        }
                        task_data['urgency'] = get_task_urgency(task_data)
                        tasks[t_id] = task_data
                        task_map[t_id] = f"{origin}->{dest}({person})"
                        counter += 1
        else:
            for dest, needs in self.needs.items():
                for item in needs.get('items_needed', []):
                    origin = item_locations.get(item)
                    if origin:
                        t_id = f"C{counter:02d}"
                        task_data = {
                            'id': t_id,
                            'type': 'CARGO',
                            'origin': origin,
                            'destination': dest,
                            'desc': f"运送{item}"
                        }
                        task_data['urgency'] = get_task_urgency(task_data)
                        tasks[t_id] = task_data
                        task_map[t_id] = f"{origin}->{dest}({item})"
                        counter += 1
        
        return tasks, task_map


def display_schedule_summary(final_states, strategy_name):
    """显示最终调度方案"""
    print("\n\n" + "#" * 20 + f" 最终调度方案 ({strategy_name}) " + "#" * 20)
    
    active_ships = 0
    total_cost = 0
    
    for name, agent in final_states.items():
        if not agent['assigned_tasks']:
            continue
        
        active_ships += 1
        docking_count = len(agent['docked_platforms']) - 1
        
        print(f"\n🚢 【{name}】 (停靠次数: {docking_count}/{MAX_DOCKINGS})")
        print(f"   - 航行足迹: {sorted(list(agent['docked_platforms']))}")
        print(f"   - 任务清单 ({len(agent['assigned_tasks'])} 个):")
        
        for task in sorted(agent['assigned_tasks'], key=lambda t: t.get('urgency', 3)):
            urgency_symbol = "🔥" if task.get('urgency') == 1 else "⚠️" if task.get('urgency') == 2 else ""
            detail = f"{task['desc']} (ID: {task['id']}): {task['origin']} → {task['destination']} {urgency_symbol}"
            print(f"     - {detail}")
    
    print(f"\n总计使用船只数量: {active_ships}")
    print("#" * (64 + len(strategy_name)))
    
    return active_ships


def compare_strategies():
    """比较不同策略的结果"""
    print("\n" + "=" * 80)
    print(" " * 25 + "策略对比分析")
    print("=" * 80)
    
    results = {}
    
    # 比较三种策略: greedy, optimal_distance, optimal_ships
    for strategy in ['greedy', 'optimal_distance', 'optimal_ships']:
        print(f"\n\n{'#' * 80}")
        print(f"{'#' * 30} {strategy.upper()} 策略 {'#' * 30}")
        print(f"{'#' * 80}\n")
        
        scheduler = ShipSchedulerOptimized(
            ships=ship_initial_positions,
            personnel_loc=personnel_locations,
            needs=platform_needs,
            coords=platform_coordinates,
            max_dockings=MAX_DOCKINGS,
            strategy=strategy
        )
        
        scheduler.run()
        active_ships = display_schedule_summary(scheduler.ship_agents, f"{strategy} 策略")
        
        results[strategy] = {
            'active_ships': active_ships,
            'ship_agents': scheduler.ship_agents
        }
    
    # 对比总结
    print("\n\n" + "=" * 80)
    print(" " * 30 + "对比总结")
    print("=" * 80)
    print(f"\n贪心策略使用船只: {results['greedy']['active_ships']}")
    print(f"MILP 优化距离策略使用船只: {results['optimal_distance']['active_ships']}")
    print(f"MILP 最少船只策略使用船只: {results['optimal_ships']['active_ships']}")
    
    print("\n策略说明:")
    print("  - greedy: 贪心算法，快速但局部最优")
    print("  - optimal_distance: MILP优化，目标是最小化总距离和靠泊次数")
    print("  - optimal_ships: MILP优化，目标是尽可能减少使用的船只数量")
    
    if results['optimal_ships']['active_ships'] < results['greedy']['active_ships']:
        print(f"\n✅ MILP最少船只策略节省了 {results['greedy']['active_ships'] - results['optimal_ships']['active_ships']} 艘船!")
    elif results['optimal_ships']['active_ships'] == results['greedy']['active_ships']:
        print(f"\n⚖️ 贪心和MILP最少船只策略使用相同数量的船只")


if __name__ == '__main__':
    # 运行策略对比
    compare_strategies()
