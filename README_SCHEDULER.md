# 船舶调度系统 (Ship Scheduler)

一个用于优化海上平台船舶调度的Python系统，支持人员运送、物资运输和返港任务规划。

## 功能特性

### 1. 多目标调度
- **人员运送**：优先级最高，紧急运送人员到各平台
- **物资运输**：运送各类设备和物资到指定平台
- **返港任务**：任务完成后船只返回港口

### 2. 三种优化策略

#### `default` 策略
- 基于距离的贪心算法
- 优先分配距离最近的任务
- 不考虑船只使用数量最小化

#### `minimize_ships` 策略  
- 最小化使用船只数量
- 对未激活的船只添加激活成本
- 鼓励任务集中分配到少数船只

#### `return_to_port` 策略 (新增)
- 最小化船只使用数量
- **自动添加返港任务**
- **考虑载重约束**
- 路线规划时考虑港口距离
- 渐进式向港口方向靠近

### 3. 载重管理

每艘船都有容量限制（吨）：
```python
ship_initial_positions = {
    "铭洋12": {"platform": (...), "capacity": 50},
    "海洋石油231": {"platform": (...), "capacity": 100},
    # ...
}
```

人员和物资都有重量：
```python
personnel_weights = {
    "维保人员": 0.1,  # 每人0.1吨（含行李）
    "4人": 0.4,
    # ...
}

item_weights = {
    "仪表设备": 5,
    "污水设备2吊": 10,
    "4吊设备": 15,
    # ...
}
```

系统会：
- 实时跟踪每艘船的当前载重
- 在分配任务时更新载重
- 在返港前检查载重是否超标
- 显示载重百分比和警告

### 4. 返港功能

返港坐标：`(13112939.86447716, 4717608.198280469)`

启用返港功能后：
1. 所有完成任务的船只会自动添加返港任务
2. 系统检查船只载重，警告超载情况
3. 显示每艘船到港口的距离
4. 返港任务优先级最低（urgency=100）

## 使用方法

### 基本使用

```python
from ship_scheduler import (
    ShipScheduler, ship_initial_positions, personnel_locations,
    platform_needs, platform_coordinates, MAX_DOCKINGS
)

# 创建调度器
scheduler = ShipScheduler(
    ships=ship_initial_positions,
    personnel_loc=personnel_locations,
    needs=platform_needs,
    coords=platform_coordinates,
    max_dockings=MAX_DOCKINGS,
    strategy='return_to_port'  # 使用返港策略
)

# 运行调度
scheduler.run()
scheduler.add_return_tasks()  # 添加平台间返回任务
scheduler.add_port_return_tasks()  # 添加返港任务

# 显示结果
display_schedule_summary(scheduler.ship_agents, "返港策略")
```

### 运行示例

```bash
# 运行主程序（测试所有策略）
python ship_scheduler.py

# 运行测试
python test_ship_scheduler.py
```

## 输出示例

```
🚢 【铭洋12】 (日常停靠: 1/3, 总停靠: 2)
   - 载重状态: 0.8吨 / 50吨 (1.6%) ✓
   - 航行足迹: ['A', 'PORT', 'R']
   - 任务清单:
     - [主线] 运送制冷剂 (ID: C12): 从 A 到 R 🔥
     - [返港] 返回港口 (ID: PORT_铭洋12): 从 R 到 PORT 

🚢 【东远503】 (日常停靠: 3/3, 总停靠: 4)
   - 载重状态: 9.0吨 / 90吨 (10.0%) ✓
   - 航行足迹: ['C', 'G', 'H', 'M', 'PORT']
   - 任务清单:
     - [主线] 运送钻修机物料 (ID: C09): 从 H 到 G ⚠️
     - [主线] 运送油漆 (ID: C11): 从 M 到 C 
     - [返港] 返回港口 (ID: PORT_东远503): 从 C 到 PORT 
```

## 任务标签说明

- `🔥` - 紧急任务（urgency=1）
- `⚠️` - 重要任务（urgency=2）
- `[主线]` - 主要任务
- `[零成本]` - 船只起始位置即在取货点
- `[顺路]` - 返程或通用顺路任务
- `[返港]` - 返回港口任务

## 约束条件

1. **停靠限制**：每艘船最多停靠3个平台（可配置）
2. **载重限制**：船只载重不应超过其容量
3. **任务优先级**：
   - 人员运送 > 紧急物资 > 重要物资 > 普通物资 > 返回任务 > 返港任务

## 测试

运行测试套件：

```bash
python test_ship_scheduler.py
```

测试包括：
- ✓ 港口坐标配置测试
- ✓ 载重跟踪功能测试
- ✓ 返港策略测试
- ✓ 所有策略对比测试

## 依赖

```
numpy
pandas
```

安装依赖：
```bash
pip install numpy pandas
```

## 策略对比

| 策略 | 使用船只 | 返港功能 | 载重跟踪 | 优化目标 |
|------|---------|---------|---------|----------|
| default | 6 | ✗ | ✓ | 距离最短 |
| minimize_ships | 5 | ✗ | ✓ | 船只最少 |
| return_to_port | 5 | ✓ | ✓ | 船只最少+返港 |

## 特性总结

### 实现的功能 ✓

1. ✓ 船舶容量数据结构（每艘船的载重量）
2. ✓ 人员和物资重量数据
3. ✓ 港口返回坐标配置
4. ✓ 任务分配时的载重跟踪
5. ✓ 路线规划考虑港口距离
6. ✓ 返港任务自动生成
7. ✓ 载重超标检测和警告
8. ✓ 载重信息显示在最终报告中

### 返港优化策略

返港策略的特点：
- 在任务分配时，给予靠近港口的平台轻微优势（降低10%成本）
- 鼓励船只在完成任务时逐步向港口方向移动
- 所有活跃船只完成任务后自动返港
- 实时监控载重，确保安全返港

## 文件结构

```
.
├── ship_scheduler.py      # 主程序
├── test_ship_scheduler.py # 测试套件
└── README_SCHEDULER.md    # 本文档
```

## 作者

hhr1236

## 许可证

本项目仅供学习和研究使用。
