#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试船舶在随机坐标位置的功能
Test ships starting at arbitrary coordinates (not at platform locations)
"""

import sys
from ship_scheduler import (
    ShipScheduler, personnel_locations, platform_needs, 
    platform_coordinates, MAX_DOCKINGS, display_schedule_summary
)

print("="*70)
print("测试场景：船舶在随机坐标位置启动")
print("Test Scenario: Ships starting at arbitrary coordinates")
print("="*70)

# 定义船舶在随机坐标位置（不在任何平台上）
test_ship_positions = {
    "测试船1": {"platform": (13448000.0, 4859500.0)},  # 接近H平台但不完全相同
    "测试船2": {"platform": (13450000.0, 4860000.0)},  # 在G和O之间的某个位置
    "测试船3": {"platform": (13447245.44, 4857292.809)},  # 恰好在B平台（用于对比）
}

print("\n船舶初始位置：")
for ship_name, data in test_ship_positions.items():
    coord = data['platform']
    # 检查是否在平台上
    platform_name = next((p_name for p_name, p_coord in platform_coordinates.items() if p_coord == coord), None)
    if platform_name:
        print(f"  {ship_name}: 坐标 {coord} (在平台 {platform_name} 上)")
    else:
        print(f"  {ship_name}: 坐标 {coord} (不在任何平台上)")

# 简化的需求配置（只使用几个任务）
test_platform_needs = {
    "K": {"personnel_needed": ["维保人员"], "items_needed": []},
    "O": {"personnel_needed": [], "items_needed": ["油样"]},
}

print("\n开始调度...")
print("-"*70)

try:
    scheduler = ShipScheduler(
        ships=test_ship_positions,
        personnel_loc=personnel_locations,
        needs=test_platform_needs,
        coords=platform_coordinates,
        max_dockings=MAX_DOCKINGS,
        strategy='default'
    )
    
    scheduler.run()
    scheduler.add_return_tasks()
    
    print("\n" + "="*70)
    print("测试结果总结")
    print("="*70)
    
    for name, agent in scheduler.ship_agents.items():
        print(f"\n🚢 {name}:")
        print(f"   当前位置: {agent['current_platform']}")
        print(f"   已停靠平台: {sorted(list(agent['docked_platforms']))}")
        print(f"   已分配任务数: {len(agent['assigned_tasks'])}")
        if agent['assigned_tasks']:
            print(f"   任务列表:")
            for task in agent['assigned_tasks']:
                print(f"     - {task['desc']} (ID: {task['id']}): {task['origin']} -> {task['destination']}")
    
    print("\n" + "="*70)
    print("✅ 测试成功！船舶可以在任意坐标位置启动。")
    print("✅ Test successful! Ships can start at arbitrary coordinates.")
    print("="*70)
    
except Exception as e:
    print("\n" + "="*70)
    print(f"❌ 测试失败: {e}")
    print(f"❌ Test failed: {e}")
    print("="*70)
    import traceback
    traceback.print_exc()
    sys.exit(1)
