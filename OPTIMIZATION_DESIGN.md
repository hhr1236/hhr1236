# 最优改向角选择方案 - 设计文档

## 1. 问题分析

### 1.1 背景
您的代码已经能够计算出一组满足以下约束的安全改向角度：
- **碰撞风险约束**：避免与目标船发生碰撞
- **岸壁风险约束**：避免过度靠近航道边界

例如，计算结果可能是：`[10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]`

### 1.2 核心问题
**如何从这组安全角度中选择一个"最优"的改向角？**

这是一个多目标优化问题，因为"最优"可以有多种定义：
- 改向幅度最小（操纵成本最低）
- 离危险边界最远（安全裕度最大）
- 最快恢复到原航向（航程延误最小）
- 综合多个因素的平衡

## 2. 设计思路

### 2.1 关键考虑因素

我设计了四个主要的优化维度：

#### （1）改向成本
- **定义**：改向角度越大，操纵成本越高
- **影响**：能耗增加、船员工作负担增加、偏离计划航线更远
- **优化目标**：最小化改向幅度

#### （2）岸壁安全裕度
- **定义**：船舶与航道边界的距离
- **影响**：离岸越远，应对突发情况的余地越大
- **优化目标**：最大化离岸距离

#### （3）避让效果
- **定义**：改向后与目标船的距离增加速度
- **影响**：较大的改向角通常能更快拉开距离，更快解除危险
- **优化目标**：最大化避让效率

#### （4）连续性/鲁棒性
- **定义**：所选角度在安全区间中的位置
- **影响**：在连续区间中部的角度，对操作误差的容忍度更高
- **优化目标**：选择鲁棒性强的角度

### 2.2 为什么这个问题有意义？

不同的改向角虽然都安全，但会导致不同的结果：

```
示例：假设安全角度为 [10°, 11°, 12°, ..., 20°]

选择 10°：
  ✓ 改向幅度最小，操作简单
  ✗ 可能离目标船较近，紧迫感较强
  ✗ 安全裕度较小

选择 15°（中间值）：
  ✓ 左右有 ±5° 的安全余地
  ✓ 对操作误差容忍度高
  ≈ 改向适中

选择 20°：
  ✓ 能最快拉开与目标船的距离
  ✓ 快速解除危险
  ✗ 改向幅度大，偏离原航线远
```

## 3. 解决方案

我设计了四种策略，每种适用于不同场景：

### 3.1 策略1：最小改向角策略

#### 核心思想
选择改向幅度最小的安全角度。

#### 适用场景
- 开阔水域，周围船舶较少
- 所有安全角度的安全裕度都足够大
- 希望最小化对正常航行的干扰

#### 优点
- 操作最简单
- 能耗最低
- 对航线影响最小

#### 缺点
- 可能安全裕度较小
- 对操作误差容忍度较低

#### 实现
```python
def strategy_minimal_deviation(safe_angles):
    return min(safe_angles)  # 选择最小的安全角度
```

---

### 3.2 策略2：最大安全裕度策略

#### 核心思想
如果安全角度形成连续区间，选择区间的中点；否则选择最长连续段的中点。

#### 适用场景
- 狭窄水道或复杂水域
- 存在较大不确定性（如恶劣天气）
- 船舶操纵性能受限

#### 优点
- 对不确定性有最大容错空间
- 即使操作有偏差，仍在安全范围内
- 在避让过程中有更多调整余地

#### 缺点
- 可能选择较大的改向角
- 操纵成本较高

#### 实现逻辑
```python
# 假设安全角度为 [10, 11, 12, 13, 14, 15, 16]
# 这是连续区间，选择中点 13°
# 此时左右各有 3° 的安全余地

# 如果是非连续的 [5, 6, 10, 11, 12, 13, 20]
# 找到最长连续段 [10, 11, 12, 13]
# 选择该段中点 11° 或 12°
```

---

### 3.3 策略3：最快复航策略

#### 核心思想
选择能够最快解除危险、恢复原航向的角度（通常是偏大的改向角）。

#### 适用场景
- 需要尽快完成避让动作
- 时间紧迫的情况
- 希望快速恢复原定航线

#### 优点
- 能更快拉开与目标船的距离
- 危险解除速度快
- 可以更早恢复原航向

#### 缺点
- 改向幅度较大
- 短期内偏离航线较远

#### 实现
```python
def strategy_fastest_return(safe_angles):
    # 选择安全区间的75%分位点
    # 偏向较大改向，但不是最大
    sorted_angles = sorted(safe_angles)
    index = int(len(sorted_angles) * 0.75)
    return sorted_angles[index]
```

---

### 3.4 策略4：综合评分策略（推荐）

#### 核心思想
为每个安全角度计算一个综合评分，选择得分最高的角度。

#### 评分公式
```
总分 = w1×改向成本评分 + w2×岸壁安全评分 + w3×避让效果评分 + w4×连续性评分
```

其中权重默认为：
- w1 = 0.3（改向成本）
- w2 = 0.3（岸壁安全）
- w3 = 0.25（避让效果）
- w4 = 0.15（连续性）

#### 各项评分计算

**1. 改向成本评分**
```python
# 归一化到[0,1]，最小改向得1分，最大改向得0分
deviation_score = 1.0 - (angle - min_angle) / (max_angle - min_angle)
```

**2. 岸壁安全评分**
```python
# 基于当前离岸距离
# RR1（近距离）为0分，RR2（远距离）为1分
bank_safety_score = (dist_to_bank - RR1) / (RR2 - RR1)
bank_safety_score = max(0.0, min(1.0, bank_safety_score))
```

**3. 避让效果评分**
```python
# 较大的改向角通常能更快拉开距离
collision_safety_score = (angle - min_angle) / (max_angle - min_angle)
```

**4. 连续性评分**
```python
# 在连续段中心的角度得分最高
# 找到该角度所在的连续段
segment_length = ...
position_in_segment = ...
center_position = segment_length / 2.0
distance_from_center = abs(position_in_segment - center_position)
continuity_score = 1.0 - (distance_from_center / center_position) * 0.5
```

#### 适用场景
- **通用场景**（推荐作为默认策略）
- 需要平衡多个优化目标
- 希望有灵活的自定义能力

#### 优点
- 综合考虑多个因素
- 可以通过调整权重适应不同场景
- 适应性强，鲁棒性好

#### 权重调整示例

**场景1：狭窄水道（优先岸壁安全）**
```python
weights = {
    'deviation': 0.15,      # 降低
    'bank_safety': 0.50,    # 提高
    'collision_safety': 0.25,
    'continuity': 0.10
}
```

**场景2：开阔水域（优先最小改向）**
```python
weights = {
    'deviation': 0.50,      # 提高
    'bank_safety': 0.20,
    'collision_safety': 0.20,
    'continuity': 0.10
}
```

**场景3：紧急情况（优先快速避让）**
```python
weights = {
    'deviation': 0.10,
    'bank_safety': 0.20,
    'collision_safety': 0.60,  # 提高
    'continuity': 0.10
}
```

## 4. 使用建议

### 4.1 决策流程图

```
开始
  │
  ├─ 有安全角度吗？
  │   ├─ 否 → 报警，无法避让
  │   └─ 是 ↓
  │
  ├─ 是否需要最大安全裕度？
  │   ├─ 是（狭窄水道/恶劣天气）→ 使用策略2
  │   └─ 否 ↓
  │
  ├─ 是否需要快速避让？
  │   ├─ 是（紧急情况）→ 使用策略3
  │   └─ 否 ↓
  │
  ├─ 是否需要最小改向？
  │   ├─ 是（开阔水域/交通稀少）→ 使用策略1
  │   └─ 否 ↓
  │
  └─ 一般情况 → 使用策略4（综合评分）
```

### 4.2 实际应用步骤

#### 步骤1：计算安全角度集合（您已有的代码）
```python
safe_angles = get_safe_angle_range(
    model='overtake',
    # ... 其他参数 ...
)
```

#### 步骤2：选择最优角度
```python
from optimal_angle_selection import select_optimal_angle

optimal_angle, explanation, scores = select_optimal_angle(
    safe_angles=safe_angles,
    strategy='comprehensive',  # 推荐使用综合策略
    ship_state=list_own_initial,
    target_state=list_tar_initial,
    bank_p1=p1,
    bank_p2=p2,
    RR1=RR1,
    RR2=RR2,
    original_course=101*pi/180
)

print(f"推荐改向角: {optimal_angle}度")
print(explanation)
```

#### 步骤3：（可选）比较所有策略
```python
from optimal_angle_selection import compare_all_strategies

results = compare_all_strategies(
    safe_angles, ship_state, target_state,
    bank_p1, bank_p2, RR1, RR2
)

print(f"策略1推荐: {results['minimal']['angle']}度")
print(f"策略2推荐: {results['margin']['angle']}度")
print(f"策略3推荐: {results['fastest']['angle']}度")
print(f"策略4推荐: {results['comprehensive']['angle']}度")
```

## 5. 扩展建议

### 5.1 动态权重调整
可以根据实时情况动态调整权重：

```python
def get_dynamic_weights(water_conditions, traffic_density, weather):
    """根据实时情况动态计算权重"""
    if water_conditions == 'narrow':
        # 狭窄水道，提高岸壁安全权重
        return {'deviation': 0.2, 'bank_safety': 0.45, 
                'collision_safety': 0.25, 'continuity': 0.1}
    
    elif traffic_density == 'high':
        # 交通密集，提高避让效果权重
        return {'deviation': 0.2, 'bank_safety': 0.25, 
                'collision_safety': 0.45, 'continuity': 0.1}
    
    elif weather == 'bad':
        # 恶劣天气，提高连续性权重（更保守）
        return {'deviation': 0.25, 'bank_safety': 0.35, 
                'collision_safety': 0.2, 'continuity': 0.2}
    
    else:
        # 默认权重
        return {'deviation': 0.3, 'bank_safety': 0.3, 
                'collision_safety': 0.25, 'continuity': 0.15}
```

### 5.2 引入机器学习
未来可以考虑：
- 收集历史避让案例数据
- 训练模型学习最优选择
- 根据船长偏好个性化推荐

### 5.3 考虑更多因素
可以进一步考虑：
- 风、流等环境因素的影响
- 船舶装载状态（满载/空载）
- 船舶操纵性能参数
- 预计的避让持续时间

## 6. 总结

### 6.1 核心观点
选择最优改向角不是简单的数学问题，而是需要综合考虑多个因素的决策问题。

### 6.2 推荐方案
1. **日常使用**：综合评分策略（策略4）+ 默认权重
2. **特殊场景**：根据实际情况选择专用策略或调整权重
3. **辅助决策**：使用比较功能查看所有策略的推荐结果

### 6.3 未来改进方向
- 根据实际使用反馈调整权重
- 收集案例数据进行验证
- 考虑引入更多优化因素
- 可能结合船长的经验和偏好

---

## 附录：快速参考

### A. 四种策略对比表

| 策略 | 优化目标 | 适用场景 | 优点 | 缺点 |
|------|---------|---------|------|------|
| 最小改向角 | 最小操纵成本 | 开阔水域 | 简单、经济 | 安全裕度小 |
| 最大安全裕度 | 最大容错空间 | 狭窄水道 | 鲁棒性强 | 可能改向大 |
| 最快复航 | 最快解除危险 | 紧急情况 | 效率高 | 短期偏离大 |
| 综合评分 | 平衡多目标 | 通用场景 | 适应性强 | 需要参数调整 |

### B. API快速索引

```python
# 导入
from optimal_angle_selection import (
    select_optimal_angle,           # 统一接口
    compare_all_strategies,         # 比较所有策略
    strategy_minimal_deviation,     # 策略1
    strategy_maximum_margin,        # 策略2
    strategy_fastest_return,        # 策略3
    strategy_comprehensive_score    # 策略4
)

# 基本用法
optimal, explanation, scores = select_optimal_angle(
    safe_angles=[10, 11, 12, ...],
    strategy='comprehensive',       # 选择策略
    ship_state=[...],
    target_state=[...],
    bank_p1=np.array([...]),
    bank_p2=np.array([...]),
    RR1=32.5,
    RR2=65.0,
    original_course=101*pi/180,
    weights={...}                   # 可选的自定义权重
)
```

### C. 联系与反馈

如有问题或建议，欢迎反馈。可以通过以下方式改进：
- 调整权重参数以适应实际需求
- 添加新的评分维度
- 根据实际测试结果优化算法
