import pprint
import numpy as np
import pandas as pd
from collections import defaultdict

# region Data Definitions
# 1.1 可用船队及其初始位置
ship_initial_positions = {
    "铭洋12": {"platform": (13450640.007581526, 4848056.034375883)},  #
    "海洋石油231": {"platform": (13443914.306586778, 4864560.117847532)},  #
    "安泉州77": {"platform": (13464242.470120028, 4851553.947134592)},  #
    "德沣": {"platform": (13447624.362575933, 4854443.73620372)},  #
    "威尔7": {"platform": (13480357.636204716, 4863420.328046263)},  #
    "东远503": {"platform": (13446723.008658983, 4866267.795537939)},  #
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


class ShipScheduler:
    def __init__(self, ships, personnel_loc, needs, coords, max_dockings, strategy='default'):
        self.initial_ships, self.personnel_loc, self.needs, self.coords, self.max_dockings = ships, personnel_loc, needs, coords, max_dockings
        if strategy not in ['default', 'minimize_ships']: raise ValueError("策略必须是 'default' 或 'minimize_ships'")
        self.strategy = strategy
        self.activation_cost = SHIP_ACTIVATION_COST if self.strategy == 'minimize_ships' else 0.0
        self.ship_agents = {}
        print(f"\n[INFO] 调度器已初始化, 优化策略: '{self.strategy}'")

    def _calculate_distance(self, p1, p2):
        def get_coord(point):
            if isinstance(point, tuple):
                return point
            elif point in self.coords:
                return self.coords[point]
            else:
                return None

        coord1, coord2 = get_coord(p1), get_coord(p2)
        if coord1 is None or coord2 is None: return np.inf
        return np.linalg.norm(np.array(coord1) - np.array(coord2))

    def assign_evening_tasks(self, evening_tasks_list):
        print("\n" + "=" * 60 + "\n           开始分配晚间任务 (纯粹就近原则)\n" + "=" * 60)
        if not evening_tasks_list:
            print("没有晚间任务需要分配。")
            return
        for i, task in enumerate(evening_tasks_list, 1):
            task_id, best_ship, min_dist = f"E{i:02d}", None, np.inf
            for ship_name, agent in self.ship_agents.items():
                if 'current_platform' in agent:
                    dist = self._calculate_distance(agent['current_platform'], task['origin'])
                    print(
                        f"  - 检查船只 '{ship_name}': 位置 '{agent.get('current_platform', '未知')}', 到达 '{task['origin']}' 的距离: {dist:,.0f}")
                    if dist < min_dist: min_dist, best_ship = dist, ship_name
            if best_ship:
                agent = self.ship_agents[best_ship]
                task_data = {**task, 'id': task_id, 'is_evening_task': True}
                print(
                    f"\n   >>> 决定将任务 '{task_id}' ({task['desc']}) 分配给最近的船 '{best_ship}' (距离: {min_dist:,.0f})")
                original_platform = agent['current_platform']
                agent['assigned_tasks'].append(task_data)
                agent['docked_platforms'].update({task['origin'], task['destination']})
                agent['current_platform'] = task['destination']
                print(f"   [路径] '{best_ship}' 从 '{original_platform}' 前往 '{task['origin']}' 接人/取货。")
                print(f"   [状态更新] '{best_ship}' 的位置从 '{task['origin']}' 送达至 '{agent['current_platform']}'。")
            else:
                print(f"警告：未能为晚间任务 '{task_id}' 找到合适的船只。")
        print(f"\n晚间任务分配完成。")

    def add_return_tasks(self):
        """
        在所有日间任务分配完成后，添加返回任务。
        """
        print("\n--- 检查并添加返回任务 ---")
        return_requirements = {'JXC': 'JXB'}
        for ship_name, agent in self.ship_agents.items():
            if not agent['assigned_tasks']: continue

            # 找到最后一个非返回、非晚间的任务
            last_real_task = None
            for task in reversed(agent['assigned_tasks']):
                if not task.get('is_return_task') and not task.get('is_evening_task'):
                    last_real_task = task
                    break

            if last_real_task:
                last_destination = last_real_task['destination']
                if last_destination in return_requirements:
                    return_dest = return_requirements[last_destination]
                    # 检查是否已经存在返回到该目的地的任务
                    has_return_task = any(
                        t.get('is_return_task') and t['destination'] == return_dest for t in agent['assigned_tasks'])
                    if not has_return_task and len(agent.get('docked_platforms', set())) < self.max_dockings + 1:
                        # FIX: 给予返回任务一个非常大的urgency值，确保它排在最后
                        return_task = {'id': f"RET_{ship_name}", 'type': 'RETURN', 'origin': last_destination,
                                       'destination': return_dest, 'desc': f"返回{return_dest}", 'is_return_task': True,
                                       'urgency': 99}  # <--- 核心修改在这里

                        agent['assigned_tasks'].append(return_task)

                        # 更新船只状态
                        if 'docked_platforms' not in agent: agent['docked_platforms'] = set()
                        agent['docked_platforms'].add(return_dest)
                        agent['current_platform'] = return_dest  # 逻辑上，船只最终停在返回点

                        print(f"  为船只 '{ship_name}' 添加了低优先级返回任务: {last_destination} -> {return_dest}")

    def _post_assignment_correction(self):
        """
        通用化的后处理修正函数，带有详细的打印输出。
        """
        print("\n" + "=" * 20 + " 分配后修正检查 (详细模式) " + "=" * 20)

        # 1. 按路线搜集所有已分配的任务和船只信息
        print("\n[步骤1] 搜集所有航线及其执行船只...")
        tasks_by_route = defaultdict(lambda: {'ships': set(), 'tasks': []})
        for ship_name, agent in self.ship_agents.items():
            for task in agent['assigned_tasks']:
                if task.get('origin') and task.get('destination'):
                    route = (task['origin'], task['destination'])
                    tasks_by_route[route]['ships'].add(ship_name)
                    tasks_by_route[route]['tasks'].append({'task_obj': task, 'original_ship': ship_name})

        print("  - 搜集完成，航线数据如下:")
        pprint.pprint({k: v['ships'] for k, v in tasks_by_route.items()}, indent=2)

        print("\n[步骤2] 查找被拆分到多个船只的问题航线...")
        found_problem = False
        for route, data in tasks_by_route.items():
            if len(data['ships']) > 1:
                found_problem = True
                print(
                    f"\n  -----------> [发现问题] 路线 {route[0]} -> {route[1]} 被 {len(data['ships'])} 艘船执行: {data['ships']}")

                # 3. 确定唯一的"主船" (Master Ship)
                print("\n  [步骤3] 确定主船 (Master Ship)...")
                master_ship = None

                # 优先级1: 零成本船
                print("    - 检查优先级1: 是否存在'零成本'船...")
                for ship_name in data['ships']:
                    is_zero_cost_ship = any(
                        t['task_obj'].get('is_zero_cost') for t in data['tasks'] if t['original_ship'] == ship_name)
                    if is_zero_cost_ship:
                        master_ship = ship_name
                        print(f"      >>> 发现'零成本'船: '{master_ship}'，将其选为主船。")
                        break

                # 优先级2: 顺路/返程船
                if not master_ship:
                    print("    - '零成本'船未找到。检查优先级2: 是否存在'顺路'船...")
                    for ship_name in data['ships']:
                        is_piggyback_ship = any(
                            t['task_obj'].get('is_piggyback') or t['task_obj'].get('is_round_trip') for t in
                            data['tasks'] if t['original_ship'] == ship_name)
                        if is_piggyback_ship:
                            master_ship = ship_name
                            print(f"      >>> 发现'顺路'船: '{master_ship}'，将其选为主船。")
                            break

                # 优先级3: 默认选择
                if not master_ship:
                    print("    - '顺路'船未找到。使用优先级3: 默认选择第一艘船。")
                    master_ship = list(data['ships'])[0]
                    print(f"      >>> 选择默认主船: '{master_ship}'")

                print(f"\n    【最终决定】将所有 {route[0]} -> {route[1]} 任务合并到船: '{master_ship}'")

                # 4. 执行任务迁移
                print("\n  [步骤4] 执行任务迁移...")
                tasks_to_move = []
                for ship_name in data['ships']:
                    if ship_name == master_ship:
                        continue

                    agent_to_remove_from = self.ship_agents[ship_name]
                    tasks_to_keep = []
                    for task in agent_to_remove_from['assigned_tasks']:
                        if task.get('origin') == route[0] and task.get('destination') == route[1]:
                            tasks_to_move.append(task)
                            print(f"      - 标记任务 '{task['id']}' 从船 '{ship_name}' 移出。")
                        else:
                            tasks_to_keep.append(task)
                    agent_to_remove_from['assigned_tasks'] = tasks_to_keep

                master_agent = self.ship_agents[master_ship]
                master_agent['assigned_tasks'].extend(tasks_to_move)
                print(f"    <<< 所有标记任务已成功合并到 '{master_ship}'")
                print("  <----------- 问题处理完毕。")

        if not found_problem:
            print("\n  [检查通过] 未发现任何同路线任务被拆分的情况。")

        print("\n" + "=" * 20 + " 分配后修正检查结束 " + "=" * 20)

    def run(self):
        self.ship_agents = {}
        for name, data in self.initial_ships.items():
            initial_coord = data['platform']
            # 直接使用坐标作为当前位置，而不是必须匹配平台名称
            # 如果坐标匹配某个平台，则使用平台名称；否则使用坐标本身
            platform_name = next((p_name for p_name, p_coord in self.coords.items() if p_coord == initial_coord), None)
            current_position = platform_name if platform_name else initial_coord

            # 初始化停靠平台集合（只有当位置是平台名称时才添加）
            initial_docked = {platform_name} if platform_name else set()

            self.ship_agents[name] = {'id': name, 'current_platform': current_position,
                                      'docked_platforms': initial_docked, 'assigned_tasks': [], 'is_active': False}

        personnel_tasks, p_task_map = self._generate_tasks('PERSONNEL')
        if personnel_tasks:
            self._run_iterative_assignment(personnel_tasks, self._build_cost_matrix(personnel_tasks), p_task_map)

        cargo_tasks, c_task_map = self._generate_tasks('CARGO')
        remaining_cargo = self._handle_zero_cost_tasks(cargo_tasks)
        remaining_cargo = self._handle_round_trip_piggybacking(remaining_cargo)
        remaining_cargo = self._handle_piggybacking(remaining_cargo)

        if remaining_cargo:
            self._run_iterative_assignment(remaining_cargo, self._build_cost_matrix(remaining_cargo), c_task_map)

        self._post_assignment_correction()

        return self.ship_agents

    def _generate_tasks(self, task_type):
        tasks, task_map, counter = {}, {}, 1
        if task_type == 'PERSONNEL':
            for dest, needs in self.needs.items():
                for person in needs.get('personnel_needed', []):
                    origin = self.personnel_loc.get(person)
                    if origin:
                        t_id, desc = f"P{counter:02d}", f"运送{person}"
                        task_data = {'id': t_id, 'type': 'PERSONNEL', 'origin': origin, 'destination': dest,
                                     'desc': desc}
                        task_data['urgency'] = get_task_urgency(task_data)
                        tasks[t_id], task_map[
                            t_id] = task_data, f"{origin}->{dest}({person})[紧急程度:{task_data['urgency']}]"
                        counter += 1
                        if needs.get('return_to'):
                            return_dest = needs['return_to']
                            return_t_id = f"R{counter:02d}"
                            return_desc = f"返回{return_dest}"
                            return_task_data = {'id': return_t_id, 'type': 'RETURN', 'origin': dest,
                                                'destination': return_dest, 'desc': return_desc, 'is_return_task': True,
                                                'original_task': t_id}
                            return_task_data['urgency'] = get_task_urgency(return_task_data)
                            tasks[return_t_id], task_map[
                                return_t_id] = return_task_data, f"{dest}->{return_dest}({return_desc})[返回任务]"
                            counter += 1
        else:
            print("\n--- 正在生成物资任务 (查找库存地点) ---")
            for dest, needs in self.needs.items():
                for item in needs.get('items_needed', []):
                    origin = item_locations.get(item)
                    if origin:
                        t_id, desc = f"C{counter:02d}", f"运送{item}"
                        task_data = {'id': t_id, 'type': 'CARGO', 'origin': origin, 'destination': dest, 'desc': desc}
                        task_data['urgency'] = get_task_urgency(task_data)
                        tasks[t_id], task_map[
                            t_id] = task_data, f"{origin}->{dest}({item})[紧急程度:{task_data['urgency']}]"
                        counter += 1
                    else:
                        print(f"  [警告] 物资 '{item}' 未定义库存地点。")
        return tasks, task_map

    def _handle_zero_cost_tasks(self, cargo_tasks):
        print("\n--- 子阶段 2a: (前置优化) 寻找零成本任务 (船只始于取货点) ---")
        remaining = cargo_tasks.copy()
        for t_id, task in list(remaining.items()):
            origin = task['origin']
            origin_coord = self.coords.get(origin)

            for agent in self.ship_agents.values():
                initial_coord = self.initial_ships[agent['id']]['platform']

                # 检查船舶初始位置是否在取货点
                # 方法1: 船舶位置是平台名称且匹配
                # 方法2: 船舶位置是坐标且与取货点坐标匹配
                is_at_origin = False
                current_pos = agent.get('initial_position', initial_coord)  # 使用初始坐标

                if isinstance(current_pos, str) and current_pos == origin:
                    is_at_origin = True
                elif isinstance(current_pos, tuple) and origin_coord and current_pos == origin_coord:
                    is_at_origin = True
                elif initial_coord == origin_coord:
                    is_at_origin = True

                if is_at_origin and task not in agent['assigned_tasks']:
                    agent['assigned_tasks'].append({**task, 'is_zero_cost': True})
                    agent['docked_platforms'].update({task['origin'], task['destination']})
                    print(
                        f"  [零成本] 任务 {task['id']} ({task.get('desc')}) -> 分配给始于'{origin}'的船 '{agent['id']}'")
                    del remaining[t_id]
                    break
        return remaining

    def _handle_round_trip_piggybacking(self, cargo_tasks):
        print("\n--- 子阶段 2b: (前置优化) 寻找返程顺路机会 ---")
        remaining = cargo_tasks.copy()
        for t_id, task in list(remaining.items()):
            task_origin, task_dest = task['origin'], task['destination']
            for agent in self.ship_agents.values():
                for main_task in agent['assigned_tasks']:
                    if main_task.get('is_zero_cost') or main_task.get('is_piggyback'): continue
                    if main_task['origin'] == task_dest and main_task['destination'] == task_origin:
                        agent['assigned_tasks'].append({**task, 'is_piggyback': True, 'is_round_trip': True})
                        agent['docked_platforms'].update({task_origin, task_dest})
                        print(
                            f"  [返程顺路] 任务 {task['id']} ({task.get('desc')}) -> 附加给 '{agent['id']}' (因其有 {task_dest}->{task_origin} 的主线任务)")
                        if t_id in remaining: del remaining[t_id]
                        break
                if t_id not in remaining: break
        return remaining

    def _handle_piggybacking(self, cargo_tasks):
        print("\n--- 子阶段 2c: (前置优化) 寻找通用顺路机会 ---")
        remaining = cargo_tasks.copy()
        for t_id, task in list(remaining.items()):
            task_origin, task_dest = task['origin'], task['destination']
            for agent in self.ship_agents.values():
                mainline_platforms = set()
                for main_task in agent['assigned_tasks']:
                    if main_task.get('is_zero_cost') or main_task.get('is_piggyback'): continue
                    mainline_platforms.add(main_task['origin'])
                    mainline_platforms.add(main_task['destination'])

                if task_origin in mainline_platforms or task_dest in mainline_platforms:
                    reason = f"因其计划前往起点'{task_origin}'" if task_origin in mainline_platforms else f"因其计划前往终点'{task_dest}'"
                    agent['assigned_tasks'].append({**task, 'is_piggyback': True})
                    agent['docked_platforms'].update({task_origin, task_dest})
                    print(f"  [通用顺路] 任务 {task['id']} ({task.get('desc')}) -> 附加给 '{agent['id']}' ({reason})")
                    if t_id in remaining: del remaining[t_id]
                    break
        return remaining

    def _build_cost_matrix(self, tasks):
        cost_matrix = pd.DataFrame(index=self.ship_agents.keys(), columns=tasks.keys(), dtype=float)
        for ship_name, agent in self.ship_agents.items():
            if (len(agent['docked_platforms']) - 1) >= self.max_dockings:
                cost_matrix.loc[ship_name, :] = PENALTY_COST
                continue
            for t_id, task in tasks.items():
                distance = self._calculate_distance(agent['current_platform'],
                                                    task['origin']) + self._calculate_distance(task['origin'],
                                                                                               task['destination'])
                urgency_factor = 0.3 if task.get('urgency') == 1 else 0.6 if task.get('urgency') == 2 else 1.0
                cost = distance * urgency_factor
                if self.strategy == 'minimize_ships' and not agent.get('is_active'): cost += self.activation_cost
                cost_matrix.loc[ship_name, t_id] = cost
        return cost_matrix

    def _run_iterative_assignment(self, task_dict, cost_matrix_df, task_details_map):
        dynamic_cost_matrix, unassigned_tasks, iteration = cost_matrix_df.copy(), task_dict.copy(), 1
        while not dynamic_cost_matrix.empty and dynamic_cost_matrix.min().min() < PENALTY_COST:
            task_type = "人员" if "P" in dynamic_cost_matrix.columns[0] else "物资"
            print(f"\n{'=' * 20} {task_type}任务分配：第 {iteration} 轮决策 {'=' * 20}")
            min_cost = dynamic_cost_matrix.min().min()
            ship_name, task_id = dynamic_cost_matrix.stack().idxmin()
            task_to_assign, agent = unassigned_tasks[task_id], self.ship_agents[ship_name]
            print(
                f"\n【决策】找到全局最小值: {min_cost:,.0f}\n   >>> 决定将任务 '{task_id}' ({task_details_map.get(task_id, '未知任务')}) 分配给 '{ship_name}'")
            original_platform = agent['current_platform']
            if self.strategy == 'minimize_ships' and not agent.get('is_active'):
                agent['is_active'] = True
                dynamic_cost_matrix.loc[ship_name] -= self.activation_cost
            agent['assigned_tasks'].append(task_to_assign)
            agent['docked_platforms'].update({task_to_assign['origin'], task_to_assign['destination']})
            agent['current_platform'] = task_to_assign['destination']
            print(f"   [状态更新] '{ship_name}' 的位置从 '{original_platform}' -> '{agent['current_platform']}'")
            del unassigned_tasks[task_id]
            dynamic_cost_matrix.drop(columns=[task_id], inplace=True)
            if (len(agent['docked_platforms']) - 1) >= self.max_dockings:
                dynamic_cost_matrix.loc[ship_name] = PENALTY_COST
                print(
                    f"   [约束] '{ship_name}' 已达到停靠上限({len(agent['docked_platforms']) - 1}/{self.max_dockings})。")
            else:
                for rem_task_id in dynamic_cost_matrix.columns:
                    rem_task = unassigned_tasks[rem_task_id]
                    new_dist = self._calculate_distance(agent['current_platform'],
                                                        rem_task['origin']) + self._calculate_distance(
                        rem_task['origin'], rem_task['destination'])
                    urgency_factor = 0.3 if rem_task.get('urgency') == 1 else 0.6 if rem_task.get(
                        'urgency') == 2 else 1.0
                    new_cost = new_dist * urgency_factor
                    if self.strategy == 'minimize_ships' and dynamic_cost_matrix.loc[
                        ship_name, rem_task_id] >= self.activation_cost:
                        dynamic_cost_matrix.loc[ship_name, rem_task_id] = new_cost + self.activation_cost
                    else:
                        dynamic_cost_matrix.loc[ship_name, rem_task_id] = new_cost
            iteration += 1


def display_schedule_summary(final_states, strategy_name):
    print("\n\n" + "#" * 20 + f" 最终调度方案 ({strategy_name}) " + "#" * 20)
    active_ships = 0
    for name, agent in final_states.items():
        if not agent['assigned_tasks']: continue
        active_ships += 1
        daily_docking_count = len({p for t in agent['assigned_tasks'] if not t.get('is_evening_task') for p in
                                   [t.get('origin'), t['destination']] if p}) - 1
        total_docking_count = len(agent['docked_platforms']) - 1
        print(f"\n🚢 【{name}】 (日常停靠: {daily_docking_count}/{MAX_DOCKINGS}, 总停靠: {total_docking_count})")
        print(f"   - 航行足迹: {sorted(list(agent['docked_platforms']))}")
        print("   - 任务清单:")
        sorted_tasks = sorted(agent['assigned_tasks'],
                              key=lambda t: (1 if t.get('is_evening_task') else 0, t.get('urgency', 3)))
        for task in sorted_tasks:
            prefix = "[晚间]" if task.get('is_evening_task') else "[返程顺路]" if task.get(
                'is_round_trip') else "[通用顺路]" if task.get('is_piggyback') else "[零成本]" if task.get(
                'is_zero_cost') else "[主线]"
            urgency_symbol = "🔥" if task.get('urgency') == 1 else "⚠️" if task.get('urgency') == 2 else ""
            detail = f"{task['desc']} (ID: {task['id']}): 从 {task['origin']} 到 {task['destination']} {urgency_symbol}"
            print(f"     - {prefix} {detail}")
    print(f"\n总计使用船只数量: {active_ships}\n" + "#" * (64 + len(strategy_name)))


if __name__ == '__main__':
    for strategy in ['default', 'minimize_ships']:
        scheduler = ShipScheduler(
            ships=ship_initial_positions, personnel_loc=personnel_locations, needs=platform_needs,
            coords=platform_coordinates, max_dockings=MAX_DOCKINGS, strategy=strategy
        )
        scheduler.run()
        scheduler.add_return_tasks()
        scheduler.assign_evening_tasks(evening_tasks)
        display_schedule_summary(scheduler.ship_agents, f"{strategy} 策略")
