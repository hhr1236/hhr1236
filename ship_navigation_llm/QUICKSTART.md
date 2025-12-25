# 快速开始指南 (Quick Start Guide)

## 5分钟快速上手 (5-Minute Quick Start)

### 1. 安装依赖 (Install Dependencies)

```bash
cd ship_navigation_llm
pip install -r requirements.txt
```

### 2. 创建示例数据 (Create Example Data)

```bash
python main.py --create-examples
```

输出 (Output):
```
创建示例航行规则文件...
Created: data/navigation_rules/渤海湾.txt
Created: data/navigation_rules/长江口.txt
Created: data/navigation_rules/珠江口.txt
✓ 示例文件已创建在 data/navigation_rules/
```

### 3. 导入文档 (Ingest Documents)

```bash
python main.py --ingest data/navigation_rules
```

输出 (Output):
```
开始导入文档...
处理了 3 个文档
正在为 渤海湾 创建嵌入向量...
正在为 长江口 创建嵌入向量...
正在为 珠江口 创建嵌入向量...
✓ 成功导入 3 个水域的航行规则
```

### 4. 开始查询 (Start Querying)

#### 方式1: 交互式查询 (Interactive Mode)

```bash
python main.py --interactive
```

然后输入您的问题 (Then enter your questions):
```
问题 > 渤海湾航行需要注意什么？
问题 > 长江口的主要航道有哪些？
问题 > 珠江口大型船舶有什么要求？
```

#### 方式2: 单次查询 (Single Query)

```bash
python main.py --query "渤海湾航行需要注意什么？"
```

---

## 使用您自己的PDF文档 (Using Your Own PDF Documents)

### 1. 准备PDF文件 (Prepare PDF Files)

将您的航行规则PDF文件放入目录：
```bash
ship_navigation_llm/data/navigation_rules/
```

建议命名方式 (Recommended naming):
- `东海航行规则.pdf`
- `南海通航规定.pdf`
- `黄海航行手册.pdf`

### 2. 导入PDF (Ingest PDFs)

```bash
python main.py --ingest data/navigation_rules
```

系统会自动：
- 提取PDF中的文本
- 分割成合适大小的文本块
- 创建向量嵌入
- 存储到向量数据库

### 3. 查询 (Query)

```bash
python main.py --interactive
```

---

## 常见问题解答 (FAQ)

### Q1: 需要OpenAI API密钥吗？

**A:** 不是必须的。系统有两种工作模式：

1. **无API模式** (默认):
   - 使用简单的哈希嵌入算法
   - 可以进行文档检索和基本问答
   - 适合测试和本地使用

2. **OpenAI API模式** (推荐):
   ```bash
   python main.py --api-key "your-api-key" --interactive
   ```
   - 更智能的理解和回答
   - 更准确的语义检索
   - 更好的中文理解能力

### Q2: 支持哪些文档格式？

**A:** 当前支持：
- ✅ PDF格式 (`.pdf`)
- ✅ 纯文本格式 (`.txt`)

未来计划支持：
- 📋 Word文档 (`.docx`)
- 📊 Excel表格 (`.xlsx`)
- 🌐 网页内容 (HTML)

### Q3: 如何提高回答质量？

**A:** 建议：

1. **使用高质量的源文档**
   - 确保PDF文本可以正确提取
   - 避免扫描版PDF（图片格式）
   - 使用结构化的文档

2. **合理命名文件**
   - 使用水域名称命名
   - 便于系统识别来源

3. **使用OpenAI API**
   - 提供更智能的回答
   - 更好的上下文理解

4. **详细提问**
   - 具体说明水域和场景
   - 例如："渤海湾冬季航行需要注意什么？"

### Q4: 可以同时查询多个水域吗？

**A:** 可以！系统会自动检索所有相关水域的文档。

示例问题：
```
"东海和南海的航行规则有什么不同？"
"哪些水域需要强制引航？"
"台风季节哪些水域特别危险？"
```

### Q5: 如何查看已导入的水域？

**A:** 在交互模式下，系统启动时会显示：

```
已加载水域: 渤海湾, 长江口, 珠江口
```

### Q6: 数据存储在哪里？

**A:** 数据存储结构：

```
ship_navigation_llm/
└── data/
    ├── navigation_rules/      # 原始文档
    │   ├── 渤海湾.txt
    │   ├── 长江口.txt
    │   └── 珠江口.txt
    ├── vector_store/           # 向量数据库
    │   └── vector_store.json
    └── knowledge_base.json     # 知识库元数据
```

### Q7: 如何更新文档？

**A:** 更新步骤：

1. 删除旧的向量存储：
   ```bash
   rm -rf data/vector_store/vector_store.json
   rm -rf data/knowledge_base.json
   ```

2. 重新导入：
   ```bash
   python main.py --ingest data/navigation_rules
   ```

---

## 高级用法 (Advanced Usage)

### 使用Python API

```python
from core.navigation_system import NavigationKnowledgeSystem

# 初始化系统
system = NavigationKnowledgeSystem(
    data_dir="data",
    api_key="your-api-key"  # 可选
)

# 加载知识库
system.load_knowledge_base()

# 查询
result = system.query("渤海湾航行需要注意什么？")

# 打印结果
system.print_answer(result)

# 获取源文档
for doc in result['source_documents']:
    print(f"来源: {doc['document']['region']}")
    print(f"相关度: {doc['similarity']:.3f}")
```

### 自定义配置

编辑 `config.py` 文件：

```python
# 文本分块大小
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# 检索结果数量
TOP_K_RESULTS = 3

# LLM参数
TEMPERATURE = 0.7
MAX_TOKENS = 1000
```

---

## 典型应用场景 (Typical Use Cases)

### 场景1: 航行规划

**问题**: "我计划从渤海湾驶往长江口，需要注意什么？"

系统会：
- 检索两个水域的相关规则
- 列出航行注意事项
- 指出需要关注的海图要素

### 场景2: 海图建模

**问题**: "在渤海湾建立海图模型需要标注哪些要素？"

系统会回答：
- 航道边界和中心线
- 锚地范围
- 禁航区和限制区
- 导航标志位置
- 浅水区和危险区

### 场景3: 应急准备

**问题**: "台风天气在珠江口应该怎么办？"

系统会提供：
- 台风季节的特殊规定
- 避风锚地位置
- 应急联系方式
- 安全建议

### 场景4: 培训教学

**问题**: "长江口的潮汐对航行有什么影响？"

系统会解释：
- 潮汐特点
- 最佳航行时机
- 流速影响
- 注意事项

---

## 下一步 (Next Steps)

1. **运行完整示例**
   ```bash
   cd examples
   python complete_example.py
   ```

2. **查看详细文档**
   - [README.md](README.md) - 完整系统文档
   - [config.py](config.py) - 配置说明

3. **贡献您的改进**
   - 添加新功能
   - 优化算法
   - 改进文档

---

## 技术支持 (Technical Support)

如有问题，请：
- 查看 [README.md](README.md)
- 在GitHub上提issue
- 查看示例代码

祝您使用愉快！🚢⛵
