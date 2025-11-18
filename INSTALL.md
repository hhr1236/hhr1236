# 安装指南

## 环境要求

- Python 3.8+
- NumPy
- Matplotlib
- SciPy

## 安装步骤

### 1. 安装依赖包

```bash
pip install -r requirements.txt
```

或者单独安装：

```bash
pip install numpy matplotlib scipy
```

### 2. 验证安装

```bash
python -c "import numpy; import matplotlib; import scipy; print('安装成功！')"
```

### 3. 运行示例代码

```bash
# 运行实用示例（推荐先运行这个）
python practical_example.py

# 运行完整的分析工具演示
python ship_domain_analysis.py
```

## 常见问题

### Q: 提示找不到模块怎么办？

**A**: 确保已安装所有依赖：
```bash
pip install numpy matplotlib scipy
```

### Q: 中文显示乱码怎么办？

**A**: 代码中已配置使用SimHei字体。如果仍有问题：

**Windows**:
```python
plt.rcParams['font.sans-serif'] = ['SimHei']  # 已包含在代码中
```

**Linux/Mac**:
```python
plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'Arial Unicode MS']
```

或者注释掉中文，使用英文：
```python
# plt.rcParams['font.sans-serif'] = ['SimHei']
# plt.rcParams['axes.unicode_minus'] = False
```

### Q: 如何集成到现有代码？

**A**: 参考以下步骤：

1. 保留你现有的MMG模型函数
2. 导入分析工具：
```python
from ship_domain_analysis import ShipDomainAnalyzer
```

3. 创建分析器并传入你的模型：
```python
def your_shallow_model(rudder_angle_rad, motion):
    # 你的MMG模型实现
    model = MMG_Model_new1(ship_data, motion, 198.5, 23)
    return model.get_next_moment()

analyzer = ShipDomainAnalyzer(
    ship_length=225.0,
    ship_width=28.125,
    shallow_model_func=your_shallow_model
)
```

4. 运行分析：
```python
test_cases = [
    {'rudder_angle': 15, 'speed': 6.0, 'lateral_dist': 150},
    {'rudder_angle': 20, 'speed': 6.5, 'lateral_dist': 150},
]
analyzer.multi_scenario_analysis(test_cases)
analysis = analyzer.recommend_domain_parameters()
```

## 文件说明

- `requirements.txt` - Python依赖包列表
- `ship_domain_analysis.py` - 核心分析工具（完整功能）
- `practical_example.py` - 实用示例（对比演示）
- `长轴确定方法论.md` - 详细理论文档
- `船舶领域长轴确定方案.md` - 快速入门指南

## 推荐学习路径

1. 阅读 `船舶领域长轴确定方案.md` 了解背景和方法（15分钟）
2. 运行 `practical_example.py` 查看对比效果（30分钟）
3. 阅读 `长轴确定方法论.md` 深入理解方法（30分钟）
4. 研究 `ship_domain_analysis.py` 源码（1小时）
5. 集成到自己的项目中（1-2小时）

## 技术支持

如遇到问题，请检查：
1. Python版本是否>=3.8
2. 是否已安装所有依赖包
3. 是否有足够的内存运行仿真
4. 图形显示是否正常工作

---

祝使用顺利！
