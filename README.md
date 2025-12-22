# Ship Scheduler Optimization Project

## 🚢 Overview

This repository contains an advanced ship scheduling system that optimizes task assignments for a fleet of vessels. The system has been enhanced with **Mixed Integer Linear Programming (MILP)** to find globally optimal solutions, significantly improving upon the original greedy algorithm.

## 🎯 Problem

Given:
- 6 ships at different starting positions
- 22 tasks (personnel transport + cargo delivery)
- Maximum 3 docking stops per ship
- Various urgency levels for tasks

Find: The optimal assignment of tasks to ships that minimizes total distance and number of ships used.

## ✨ Key Features

- **Original Greedy Algorithm**: Fast local optimization (existing code)
- **NEW: MILP Global Optimization**: Mathematically optimal solutions
- **Flexible Strategy Selection**: Choose between speed and optimality
- **Constraint Handling**: Docking limits, urgency priorities, ship activation costs
- **Comparison Tools**: Side-by-side analysis of different approaches

## 📊 Results

| Algorithm | Ships Used | Solution Quality | Speed |
|-----------|------------|------------------|-------|
| Greedy    | 6          | Local optimum    | ⚡ Fast |
| **MILP**  | **4-6**    | **Global optimum** | 🐌 Moderate |

**Improvement**: Up to 33% reduction in ships used! 🎉

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install numpy pandas pulp
```

### Basic Usage

```python
from ship_scheduler_optimized import ShipSchedulerOptimized

# Use MILP optimization
scheduler = ShipSchedulerOptimized(
    ships=ship_initial_positions,
    personnel_loc=personnel_locations,
    needs=platform_needs,
    coords=platform_coordinates,
    max_dockings=3,
    strategy='optimal_ships'  # 'optimal_distance', 'optimal_ships', or 'greedy'
)

results = scheduler.run()
```

### Optimization Strategies

- **`'optimal_distance'`**: MILP minimizing distance + platform visits
  - Penalizes platform visits (50,000 per platform) to encourage "顺路" (on-the-way) tasks
  - Tasks cluster at fewer platforms → fewer dockings, better route efficiency
  
- **`'optimal_ships'`**: MILP minimizing number of ships
  - Large ship activation penalty (100,000 per ship) to force task consolidation
  - Uses fewer ships even if individual ships travel longer distances
  
- **`'greedy'`**: Fast greedy algorithm (local optimum)

### Run Comparison

```bash
python compare_algorithms.py
```

## 📁 Files

- **`ship_scheduler.py`**: Original implementation with greedy algorithm
- **`ship_scheduler_optimized.py`**: NEW enhanced version with MILP optimization
- **`compare_algorithms.py`**: Script to compare different strategies
- **`SHIP_SCHEDULER_GUIDE.md`**: Comprehensive documentation and guide

## 🔍 How It Works

### Greedy Algorithm (Original)
```
for each task:
    find ship with minimum cost for this task
    assign task to that ship
    update ship position and costs
```
**Problem**: Makes locally optimal decisions, can't see the global picture.

### MILP Optimization (NEW)
```
Decision Variables:
  x[task,ship] = 1 if task assigned to ship, 0 otherwise
  
Objective:
  Minimize: Σ(distance * urgency * x[task,ship]) + Σ(activation_cost * ship_used)
  
Constraints:
  - Each task assigned to exactly one ship
  - Docking limits respected
  - Ship activation logic
```
**Advantage**: Considers ALL tasks and ships simultaneously for globally optimal solution.

## 📖 Documentation

For detailed explanation of the algorithms, mathematical formulation, and usage examples, see:
- [**SHIP_SCHEDULER_GUIDE.md**](SHIP_SCHEDULER_GUIDE.md) - Complete guide with examples

## �� Example Output

```
🚢 【铭洋12】 (停靠次数: 3/3)
   - 航行足迹: ['A', 'E', 'LD52', 'R']
   - 任务清单 (3 个):
     - 运送修井监督 (ID: P04): LD52 → E 🔥
     - 运送制冷剂 (ID: C20): A → R 🔥
     - 运送修井小件 (ID: C16): A → E ⚠️

✅ MILP 策略节省了 2 艘船!
```

## 🛠️ Technical Stack

- **Python 3.8+**
- **NumPy**: Numerical computations
- **Pandas**: Data manipulation
- **PuLP**: Linear programming modeling
- **CBC Solver**: MILP optimization engine

## 🤝 Contributing

Improvements welcome! Potential enhancements:
- Route sequencing optimization
- Time window constraints
- Fuel consumption modeling
- Visual route maps
- Benchmark test suites

## 📚 References

- Vehicle Routing Problem (VRP)
- Mixed Integer Linear Programming
- Branch and Bound optimization
- PuLP documentation

## 📝 License

Educational and research purposes.

---

**Note**: This repository demonstrates the power of mathematical optimization over heuristic approaches for complex scheduling problems.
