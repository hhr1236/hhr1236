# 船舶避让最优改向角选择系统

这个项目提供了一套完整的解决方案，用于从一组安全的改向角度中选择最优的避让角度。

## 问题背景

在船舶避让场景中，我们已经能够计算出所有满足安全约束的改向角度（避免碰撞风险和岸壁风险），但面临一个新问题：

**如何从多个安全角度中选择一个"最优"的角度？**

例如，如果安全角度集合是 `[10°, 11°, 12°, 13°, 14°, 15°, 16°, 17°, 18°, 19°, 20°]`，应该选择哪一个？

## 解决方案

本项目提供了**四种策略**来选择最优角度，每种策略适用于不同的场景：

### 1️⃣ 最小改向角策略
- **目标**：最小化操纵成本
- **适用场景**：开阔水域、交通稀少
- **特点**：选择改向幅度最小的角度

### 2️⃣ 最大安全裕度策略
- **目标**：最大化安全余地
- **适用场景**：狭窄水道、恶劣天气
- **特点**：选择连续安全区间的中间值

### 3️⃣ 最快复航策略
- **目标**：最快解除危险
- **适用场景**：紧急情况、时间紧迫
- **特点**：选择较大的改向角以快速拉开距离

### 4️⃣ 综合评分策略（推荐）
- **目标**：平衡多个优化目标
- **适用场景**：通用场景（推荐默认使用）
- **特点**：综合考虑改向成本、岸壁安全、避让效果、连续性四个维度

## 文件说明

### 核心代码
- **`optimal_angle_selection.py`** - 核心算法实现
  - 四种选择策略的完整实现
  - 支持 Numba 加速
  - 提供统一的调用接口

### 使用示例
- **`optimal_angle_usage_example.py`** - 详细的使用示例
  - 每种策略的使用方法
  - 自定义权重的方法
  - 边界情况处理
  - 集成到现有代码的方法

### 文档
- **`OPTIMIZATION_DESIGN.md`** - 完整的设计文档
  - 问题分析
  - 设计思路
  - 每种策略的详细说明
  - 使用建议和扩展方向

## 快速开始

### 安装依赖
```bash
pip install numpy numba
```

### 基本使用

```python
from optimal_angle_selection import select_optimal_angle
import numpy as np
from math import pi

# 假设从您的代码得到的安全角度集合
safe_angles = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

# 船舶和环境数据
ship_state = [13129232.354082255, 4714024.311997643, 1.74, 0.012, 5.08, 0.0]
target_state = [13130154.550863445, 4713911.276295917, 1.754, 0.0, 2.51, 0.0]
bank_p1 = np.array([13126214.0, 4714473.0])
bank_p2 = np.array([13127587.0, 4714219.0])
RR1, RR2 = 32.5, 65.0

# 使用综合评分策略（推荐）
optimal_angle, explanation, scores = select_optimal_angle(
    safe_angles=safe_angles,
    strategy='comprehensive',
    ship_state=ship_state,
    target_state=target_state,
    bank_p1=bank_p1,
    bank_p2=bank_p2,
    RR1=RR1,
    RR2=RR2,
    original_course=101*pi/180
)

print(f"推荐的最优改向角: {optimal_angle}度")
print(explanation)
```

### 比较所有策略

```python
from optimal_angle_selection import compare_all_strategies

# 获取所有策略的推荐结果
results = compare_all_strategies(
    safe_angles, ship_state, target_state,
    bank_p1, bank_p2, RR1, RR2
)

print(f"策略1（最小改向）推荐: {results['minimal']['angle']}度")
print(f"策略2（最大裕度）推荐: {results['margin']['angle']}度")
print(f"策略3（最快复航）推荐: {results['fastest']['angle']}度")
print(f"策略4（综合评分）推荐: {results['comprehensive']['angle']}度")
```

### 自定义权重

```python
# 针对狭窄水道，提高岸壁安全权重
custom_weights = {
    'deviation': 0.15,
    'bank_safety': 0.50,    # 提高岸壁安全权重
    'collision_safety': 0.25,
    'continuity': 0.10
}

optimal_angle, explanation, _ = select_optimal_angle(
    safe_angles=safe_angles,
    strategy='comprehensive',
    ship_state=ship_state,
    target_state=target_state,
    bank_p1=bank_p1,
    bank_p2=bank_p2,
    RR1=RR1,
    RR2=RR2,
    weights=custom_weights  # 传入自定义权重
)
```

## 策略选择指南

| 场景 | 推荐策略 | 说明 |
|------|---------|------|
| 开阔水域，交通稀少 | 最小改向角 | 减少操纵负担，节省能耗 |
| 狭窄水道，需精确控制 | 最大安全裕度 | 提高容错能力，更安全 |
| 紧急避让，时间紧迫 | 最快复航 | 快速解除危险 |
| 一般情况（推荐） | 综合评分 | 平衡多个目标，适应性强 |
| 不确定如何选择 | 综合评分 + 比较功能 | 先比较所有策略结果再决策 |

## 运行示例

运行完整的示例程序：

```bash
python optimal_angle_usage_example.py
```

这将展示：
- 每种策略的使用方法
- 自定义权重的效果
- 不同场景下的推荐结果
- 边界情况的处理

## 集成到现有代码

在您的主程序中添加：

```python
# 1. 导入模块
from optimal_angle_selection import select_optimal_angle

# 2. 计算安全角度（您已有的代码）
safe_angles = get_safe_angle_range(
    model='overtake',
    # ... 其他参数 ...
)

# 3. 选择最优角度（新增）
if safe_angles:
    optimal_angle, explanation, _ = select_optimal_angle(
        safe_angles=safe_angles,
        strategy='comprehensive',
        ship_state=list_own_initial,
        target_state=list_tar_initial,
        bank_p1=p1,
        bank_p2=p2,
        RR1=RR1,
        RR2=RR2
    )
    
    print(f"\n推荐的最优改向角: {optimal_angle}度")
    print(explanation)
else:
    print("警告: 没有找到安全的改向角度")
```

## 主要特性

✅ **四种优化策略**：覆盖不同的应用场景  
✅ **灵活的权重配置**：可根据实际情况自定义  
✅ **Numba加速**：关键计算函数支持JIT编译  
✅ **完整的文档**：设计思路、使用示例、API参考  
✅ **边界情况处理**：空集合、单个角度、非连续区间等  
✅ **策略比较功能**：帮助决策者选择最合适的策略  

## 技术细节

### 综合评分策略的评分维度

1. **改向成本** (权重默认0.3)
   - 越小的改向角得分越高
   - 考虑操纵负担和能耗

2. **岸壁安全** (权重默认0.3)
   - 离岸距离越大得分越高
   - 基于 RR1、RR2 参数计算

3. **避让效果** (权重默认0.25)
   - 较大改向角能更快拉开距离
   - 考虑危险解除速度

4. **连续性** (权重默认0.15)
   - 连续区间中部的角度得分更高
   - 提高对操作误差的容忍度

### 评分公式

```
总分 = 0.3×改向成本评分 + 0.3×岸壁安全评分 + 0.25×避让效果评分 + 0.15×连续性评分
```

## 扩展建议

### 1. 动态权重调整
根据实时条件（水域特征、交通密度、天气状况）动态调整权重

### 2. 机器学习优化
收集历史案例，训练模型学习最优选择

### 3. 更多优化因素
- 风、流等环境因素
- 船舶装载状态
- 操纵性能参数
- 预计避让时间

## 贡献

欢迎提出问题和改进建议！可以通过以下方式参与：
- 报告 bug
- 提出新的优化策略
- 改进现有算法
- 完善文档

## 许可证

本项目开源，可自由使用和修改。

---

## 常见问题 (FAQ)

**Q: 为什么需要选择最优角度？所有安全角度不都可以吗？**  
A: 虽然都安全，但不同角度会导致不同的操纵成本、安全裕度和避让效率。选择最优角度可以在保证安全的前提下，优化这些指标。

**Q: 应该选择哪个策略？**  
A: 推荐使用综合评分策略作为默认选择。如果有特殊需求，可以根据场景选择专用策略或调整权重。

**Q: 如何调整权重？**  
A: 在调用 `select_optimal_angle` 时传入 `weights` 参数。权重总和应为1.0。例如在狭窄水道中可以提高 `bank_safety` 的权重。

**Q: 代码性能如何？**  
A: 核心计算函数使用 Numba JIT 编译，性能优秀。对于典型的安全角度集合（10-30个角度），选择过程在毫秒级完成。

**Q: 可以添加新的优化维度吗？**  
A: 可以。在 `strategy_comprehensive_score` 函数中添加新的评分项，并调整权重配置即可。

---

**祝您的船舶避让系统运行顺利！** ⚓🚢
