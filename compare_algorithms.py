#!/usr/bin/env python3
"""
Simple script to demonstrate the improvement from greedy to MILP optimization
"""

import sys
from ship_scheduler import ShipScheduler
from ship_scheduler_optimized import ShipSchedulerOptimized, display_schedule_summary
from ship_scheduler import (
    ship_initial_positions, personnel_locations, platform_needs,
    platform_coordinates, MAX_DOCKINGS
)

def main():
    print("=" * 80)
    print(" " * 20 + "SHIP SCHEDULER COMPARISON")
    print("=" * 80)
    print("\nThis script compares the original greedy algorithm with MILP optimization.\n")
    
    # Test 1: Original Greedy Algorithm
    print("\n" + "#" * 80)
    print("TEST 1: Original Greedy Algorithm (from ship_scheduler.py)")
    print("#" * 80 + "\n")
    
    try:
        scheduler_orig = ShipScheduler(
            ships=ship_initial_positions,
            personnel_loc=personnel_locations,
            needs=platform_needs,
            coords=platform_coordinates,
            max_dockings=MAX_DOCKINGS,
            strategy='minimize_ships'
        )
        scheduler_orig.run()
        scheduler_orig.add_return_tasks()
        ships_used_orig = sum(1 for agent in scheduler_orig.ship_agents.values() 
                             if agent['assigned_tasks'])
        print(f"\n✓ Original algorithm completed")
        print(f"✓ Ships used: {ships_used_orig}")
    except Exception as e:
        print(f"✗ Error in original algorithm: {e}")
        ships_used_orig = None
    
    # Test 2: New Greedy (simplified)
    print("\n\n" + "#" * 80)
    print("TEST 2: Simplified Greedy Algorithm (from ship_scheduler_optimized.py)")
    print("#" * 80 + "\n")
    
    scheduler_greedy = ShipSchedulerOptimized(
        ships=ship_initial_positions,
        personnel_loc=personnel_locations,
        needs=platform_needs,
        coords=platform_coordinates,
        max_dockings=MAX_DOCKINGS,
        strategy='greedy'
    )
    scheduler_greedy.run()
    ships_used_greedy = display_schedule_summary(scheduler_greedy.ship_agents, "Greedy")
    
    # Test 3: MILP Optimization - Distance
    print("\n\n" + "#" * 80)
    print("TEST 3: MILP Optimization - Minimize Distance (from ship_scheduler_optimized.py)")
    print("#" * 80 + "\n")
    
    scheduler_optimal_dist = ShipSchedulerOptimized(
        ships=ship_initial_positions,
        personnel_loc=personnel_locations,
        needs=platform_needs,
        coords=platform_coordinates,
        max_dockings=MAX_DOCKINGS,
        strategy='optimal_distance'
    )
    scheduler_optimal_dist.run()
    ships_used_optimal_dist = display_schedule_summary(scheduler_optimal_dist.ship_agents, "MILP 优化距离")
    
    # Test 4: MILP Optimization - Ships
    print("\n\n" + "#" * 80)
    print("TEST 4: MILP Optimization - Minimize Ships (from ship_scheduler_optimized.py)")
    print("#" * 80 + "\n")
    
    scheduler_optimal_ships = ShipSchedulerOptimized(
        ships=ship_initial_positions,
        personnel_loc=personnel_locations,
        needs=platform_needs,
        coords=platform_coordinates,
        max_dockings=MAX_DOCKINGS,
        strategy='optimal_ships'
    )
    scheduler_optimal_ships.run()
    ships_used_optimal_ships = display_schedule_summary(scheduler_optimal_ships.ship_agents, "MILP 最少船只")
    
    # Summary
    print("\n\n" + "=" * 80)
    print(" " * 30 + "FINAL SUMMARY")
    print("=" * 80)
    print(f"\n{'Algorithm':<40} {'Ships Used':<15} {'Objective':<25}")
    print("-" * 80)
    if ships_used_orig:
        print(f"{'Original Greedy':<40} {ships_used_orig:<15} {'Local optimum':<25}")
    print(f"{'Simplified Greedy':<40} {ships_used_greedy:<15} {'Local optimum':<25}")
    print(f"{'MILP Optimize Distance':<40} {ships_used_optimal_dist:<15} {'Min distance/dockings':<25}")
    print(f"{'MILP Minimize Ships':<40} {ships_used_optimal_ships:<15} {'Min ship count':<25}")
    print("=" * 80)
    
    # Improvement calculation
    print("\n策略说明:")
    print("  - Original/Simplified Greedy: 贪心算法，快速但局部最优")
    print("  - MILP Optimize Distance: 优化总距离和靠泊次数（允许多船）")
    print("  - MILP Minimize Ships: 尽可能减少使用的船只数量")
    
    if ships_used_optimal_ships < ships_used_greedy:
        improvement = ((ships_used_greedy - ships_used_optimal_ships) / ships_used_greedy) * 100
        print(f"\n🎉 IMPROVEMENT: MILP最少船只策略减少了 {improvement:.1f}% 的船只使用!")
        print(f"   ({ships_used_greedy} → {ships_used_optimal_ships} ships)")
    elif ships_used_optimal_ships == ships_used_greedy:
        print(f"\n✓ 贪心和MILP最少船只策略使用相同数量的船只 ({ships_used_optimal_ships})")
        print("  MILP provides mathematical guarantee that this is optimal.")
    
    print("\n" + "=" * 80)
    print("\nFor detailed explanation, see: SHIP_SCHEDULER_GUIDE.md")
    print("=" * 80 + "\n")

if __name__ == '__main__':
    main()
