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
    
    # Test 3: MILP Optimization
    print("\n\n" + "#" * 80)
    print("TEST 3: MILP Global Optimization (from ship_scheduler_optimized.py)")
    print("#" * 80 + "\n")
    
    scheduler_optimal = ShipSchedulerOptimized(
        ships=ship_initial_positions,
        personnel_loc=personnel_locations,
        needs=platform_needs,
        coords=platform_coordinates,
        max_dockings=MAX_DOCKINGS,
        strategy='optimal'
    )
    scheduler_optimal.run()
    ships_used_optimal = display_schedule_summary(scheduler_optimal.ship_agents, "MILP Optimal")
    
    # Summary
    print("\n\n" + "=" * 80)
    print(" " * 30 + "FINAL SUMMARY")
    print("=" * 80)
    print(f"\n{'Algorithm':<30} {'Ships Used':<15} {'Quality':<20}")
    print("-" * 80)
    if ships_used_orig:
        print(f"{'Original Greedy':<30} {ships_used_orig:<15} {'Local optimum':<20}")
    print(f"{'Simplified Greedy':<30} {ships_used_greedy:<15} {'Local optimum':<20}")
    print(f"{'MILP Optimization':<30} {ships_used_optimal:<15} {'Global optimum':<20}")
    print("=" * 80)
    
    # Improvement calculation
    if ships_used_greedy > ships_used_optimal:
        improvement = ((ships_used_greedy - ships_used_optimal) / ships_used_greedy) * 100
        print(f"\n🎉 IMPROVEMENT: {improvement:.1f}% reduction in ships used!")
        print(f"   ({ships_used_greedy} → {ships_used_optimal} ships)")
    elif ships_used_greedy == ships_used_optimal:
        print(f"\n✓ Both strategies use the same number of ships ({ships_used_optimal})")
        print("  MILP provides mathematical guarantee that this is optimal.")
    else:
        print(f"\n⚠️ Note: MILP used more ships due to strict constraints")
    
    print("\n" + "=" * 80)
    print("\nFor detailed explanation, see: SHIP_SCHEDULER_GUIDE.md")
    print("=" * 80 + "\n")

if __name__ == '__main__':
    main()
