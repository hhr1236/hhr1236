"""
测试船舶调度器的返港功能
Test the ship scheduler's return-to-port functionality
"""
import sys
from ship_scheduler import (
    ShipScheduler, ship_initial_positions, personnel_locations,
    platform_needs, platform_coordinates, evening_tasks, MAX_DOCKINGS
)


def test_return_to_port_strategy():
    """测试返港策略"""
    print("\n" + "=" * 60)
    print("测试返港策略 (return_to_port)")
    print("=" * 60)
    
    scheduler = ShipScheduler(
        ships=ship_initial_positions,
        personnel_loc=personnel_locations,
        needs=platform_needs,
        coords=platform_coordinates,
        max_dockings=MAX_DOCKINGS,
        strategy='return_to_port'
    )
    
    scheduler.run()
    scheduler.add_return_tasks()
    scheduler.assign_evening_tasks(evening_tasks)
    scheduler.add_port_return_tasks()
    
    # 验证所有活跃船只都有返港任务
    active_ships_with_tasks = [name for name, agent in scheduler.ship_agents.items() 
                                if agent['assigned_tasks']]
    
    for ship_name in active_ships_with_tasks:
        agent = scheduler.ship_agents[ship_name]
        has_port_return = any(task.get('is_port_return') for task in agent['assigned_tasks'])
        
        if has_port_return:
            print(f"✓ 船只 '{ship_name}' 有返港任务")
            # 验证载重不超过容量
            if agent['current_load'] <= agent['capacity']:
                print(f"  ✓ 载重正常: {agent['current_load']:.1f}吨 / {agent['capacity']}吨")
            else:
                print(f"  ⚠️  警告: 载重超标: {agent['current_load']:.1f}吨 / {agent['capacity']}吨")
        else:
            print(f"  注意: 船只 '{ship_name}' 没有返港任务")
    
    return scheduler.ship_agents


def test_capacity_tracking():
    """测试载重跟踪"""
    print("\n" + "=" * 60)
    print("测试载重跟踪功能")
    print("=" * 60)
    
    scheduler = ShipScheduler(
        ships=ship_initial_positions,
        personnel_loc=personnel_locations,
        needs=platform_needs,
        coords=platform_coordinates,
        max_dockings=MAX_DOCKINGS,
        strategy='return_to_port'
    )
    
    scheduler.run()
    
    # 检查所有船只的载重情况
    all_within_capacity = True
    for ship_name, agent in scheduler.ship_agents.items():
        if agent['assigned_tasks']:
            current_load = agent.get('current_load', 0.0)
            capacity = agent.get('capacity', 100)
            
            print(f"船只 '{ship_name}': {current_load:.1f}吨 / {capacity}吨", end="")
            
            if current_load <= capacity:
                print(" ✓")
            else:
                print(f" ⚠️  超载 {current_load - capacity:.1f}吨")
                all_within_capacity = False
    
    if all_within_capacity:
        print("\n✓ 所有船只载重在容量范围内")
    else:
        print("\n⚠️  部分船只超载")
    
    return all_within_capacity


def test_port_coordinates():
    """测试港口坐标是否正确配置"""
    print("\n" + "=" * 60)
    print("测试港口坐标配置")
    print("=" * 60)
    
    if 'PORT' in platform_coordinates:
        port_coord = platform_coordinates['PORT']
        expected_coord = (13112939.86447716, 4717608.198280469)
        
        if port_coord == expected_coord:
            print(f"✓ 港口坐标正确配置: {port_coord}")
            return True
        else:
            print(f"⚠️  港口坐标不匹配:")
            print(f"  期望: {expected_coord}")
            print(f"  实际: {port_coord}")
            return False
    else:
        print("✗ 港口坐标未配置")
        return False


def test_all_strategies():
    """测试所有策略"""
    print("\n" + "=" * 60)
    print("测试所有策略")
    print("=" * 60)
    
    strategies = ['default', 'minimize_ships', 'return_to_port']
    results = {}
    
    for strategy in strategies:
        print(f"\n--- 测试策略: {strategy} ---")
        
        scheduler = ShipScheduler(
            ships=ship_initial_positions,
            personnel_loc=personnel_locations,
            needs=platform_needs,
            coords=platform_coordinates,
            max_dockings=MAX_DOCKINGS,
            strategy=strategy
        )
        
        scheduler.run()
        scheduler.add_return_tasks()
        scheduler.assign_evening_tasks(evening_tasks)
        scheduler.add_port_return_tasks()
        
        # 统计使用的船只数量
        active_ships = sum(1 for agent in scheduler.ship_agents.values() 
                          if agent['assigned_tasks'])
        
        # 检查是否有返港任务
        ships_with_port_return = sum(
            1 for agent in scheduler.ship_agents.values()
            if any(task.get('is_port_return') for task in agent['assigned_tasks'])
        )
        
        results[strategy] = {
            'active_ships': active_ships,
            'ships_with_port_return': ships_with_port_return
        }
        
        print(f"  活跃船只: {active_ships}")
        print(f"  有返港任务的船只: {ships_with_port_return}")
    
    print("\n--- 策略比较 ---")
    for strategy, result in results.items():
        print(f"{strategy}: {result['active_ships']} 艘船, {result['ships_with_port_return']} 艘返港")
    
    return results


if __name__ == '__main__':
    print("=" * 60)
    print("船舶调度器测试套件")
    print("=" * 60)
    
    # 运行所有测试
    test_port_coordinates()
    test_capacity_tracking()
    test_return_to_port_strategy()
    test_all_strategies()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
