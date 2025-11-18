#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示示例：船舶可以在任意坐标位置启动
Demonstration: Ships can start at arbitrary coordinates
"""

from ship_scheduler import (
    ShipScheduler, personnel_locations, item_locations, platform_needs, 
    platform_coordinates, MAX_DOCKINGS, display_schedule_summary
)

print("="*80)
print("演示：船舶在任意坐标位置启动的灵活性")
print("Demonstration: Flexibility of Ships Starting at Arbitrary Coordinates")
print("="*80)

# 场景1：所有船舶都在平台上（原始行为）
print("\n" + "="*80)
print("场景1: 所有船舶都在已知平台上")
print("Scenario 1: All ships at known platform locations")
print("="*80)

ships_at_platforms = {
    "平台船A": {"platform": (13448000.87, 4859490.675)},  # H平台
    "平台船B": {"platform": (13452403.86, 4860510.515)},  # O平台
}

for ship, data in ships_at_platforms.items():
    coord = data['platform']
    platform = next((p for p, c in platform_coordinates.items() if c == coord), None)
    print(f"  {ship}: {coord} → 平台 {platform}")

# 场景2：船舶在随机位置（新功能）
print("\n" + "="*80)
print("场景2: 船舶在海上任意位置（不在平台上）")
print("Scenario 2: Ships at arbitrary sea locations (not at platforms)")
print("="*80)

ships_at_sea = {
    "海上船A": {"platform": (13448500.0, 4859000.0)},  # 在H和CEP之间
    "海上船B": {"platform": (13451000.0, 4860700.0)},  # 在O和G之间
    "海上船C": {"platform": (13449000.0, 4858000.0)},  # 在M和B之间
}

for ship, data in ships_at_sea.items():
    coord = data['platform']
    # 找到最近的平台
    import numpy as np
    min_dist = float('inf')
    nearest_platform = None
    for p_name, p_coord in platform_coordinates.items():
        dist = np.linalg.norm(np.array(coord) - np.array(p_coord))
        if dist < min_dist:
            min_dist = dist
            nearest_platform = p_name
    print(f"  {ship}: {coord}")
    print(f"       → 最近平台: {nearest_platform} (距离: {min_dist:.0f}米)")

# 场景3：混合配置（部分在平台，部分在海上）
print("\n" + "="*80)
print("场景3: 混合配置 - 部分船在平台，部分船在海上")
print("Scenario 3: Mixed configuration - some at platforms, some at sea")
print("="*80)

mixed_ships = {
    "船舶1": {"platform": (13448000.87, 4859490.675)},  # H平台
    "船舶2": {"platform": (13449000.0, 4860000.0)},      # 随机位置
    "船舶3": {"platform": (13447245.44, 4857292.809)},  # B平台
    "船舶4": {"platform": (13450000.0, 4862000.0)},      # 随机位置
}

for ship, data in mixed_ships.items():
    coord = data['platform']
    platform = next((p for p, c in platform_coordinates.items() if c == coord), None)
    if platform:
        print(f"  {ship}: 在平台 {platform}")
    else:
        print(f"  {ship}: 在海上坐标 {coord}")

# 实际运行一个小型调度示例
print("\n" + "="*80)
print("运行实际调度示例（场景3）")
print("Running actual scheduling example (Scenario 3)")
print("="*80)

# 简化需求用于演示
demo_needs = {
    "K": {"personnel_needed": ["维保人员"], "items_needed": ["样桶分液桶"]},
    "O": {"personnel_needed": [], "items_needed": ["油样"]},
}

print("\n开始调度...\n")

scheduler = ShipScheduler(
    ships=mixed_ships,
    personnel_loc=personnel_locations,
    needs=demo_needs,
    coords=platform_coordinates,
    max_dockings=MAX_DOCKINGS,
    strategy='default'
)

scheduler.run()

print("\n" + "="*80)
print("调度结果")
print("Scheduling Results")
print("="*80)

for name, agent in scheduler.ship_agents.items():
    if agent['assigned_tasks']:
        print(f"\n🚢 {name}:")
        
        # 显示初始位置
        initial_pos = mixed_ships[name]['platform']
        platform = next((p for p, c in platform_coordinates.items() if c == initial_pos), None)
        if platform:
            print(f"   初始位置: 平台 {platform}")
        else:
            print(f"   初始位置: 坐标 {initial_pos}")
        
        # 显示任务
        print(f"   分配任务: {len(agent['assigned_tasks'])} 个")
        for task in agent['assigned_tasks']:
            task_type = "[零成本]" if task.get('is_zero_cost') else "[主线]"
            print(f"     {task_type} {task['desc']}: {task['origin']} → {task['destination']}")
        
        # 显示停靠记录
        print(f"   停靠平台: {sorted(list(agent['docked_platforms']))}")

print("\n" + "="*80)
print("✅ 功能演示完成！")
print("✅ 关键特性：")
print("   1. 船舶可以在任意坐标位置启动")
print("   2. 系统自动识别船舶是否在平台上")
print("   3. 距离计算支持坐标和平台名称混合使用")
print("   4. 零成本任务检测通过坐标比较正确工作")
print("="*80)
