# 船舶智能航行知识系统 (Ship Navigation Knowledge System)

[English](#english) | [中文](#chinese)

<a name="chinese"></a>
## 中文说明

### 项目简介

这是一个基于大语言模型(LLM)的船舶智能航行知识管理系统。系统可以学习不同水域的通航规则PDF文档，并通过自然语言问答的方式帮助用户了解各个水域的航行注意事项，从而指导海图要素的选择和建模。

### 主要功能

1. **文档导入**: 支持导入PDF格式的通航规则文档（也支持纯文本格式）
2. **知识学习**: 使用LLM理解和学习航行规则内容
3. **智能问答**: 通过自然语言提问，获取特定水域的航行注意事项
4. **海图指导**: 系统回答会指出需要在海图上关注的要素（如航道、锚地、禁航区等）
5. **多水域支持**: 可以同时管理多个水域的航行规则

### 系统架构

```
ship_navigation_llm/
├── core/                       # 核心模块
│   ├── pdf_processor.py       # PDF文档处理
│   ├── text_processor.py      # 文本文档处理
│   ├── vector_store.py        # 向量存储和检索
│   ├── llm_interface.py       # LLM接口
│   └── navigation_system.py   # 主系统集成
├── data/                       # 数据目录
│   ├── example_navigation_rules.py  # 示例数据
│   ├── navigation_rules/      # 存放航行规则文档
│   └── vector_store/          # 向量存储
├── utils/                      # 工具模块
├── examples/                   # 示例脚本
├── main.py                     # 主程序入口
└── requirements.txt           # 依赖项
```

### 安装步骤

1. 克隆或下载本项目
2. 安装依赖：

```bash
cd ship_navigation_llm
pip install -r requirements.txt
```

3. （可选）如果需要使用OpenAI API，设置环境变量：

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 使用方法

#### 1. 创建示例数据

```bash
python main.py --create-examples
```

这会在 `data/navigation_rules/` 目录下创建三个示例文件：
- 渤海湾.txt
- 长江口.txt  
- 珠江口.txt

#### 2. 导入航行规则文档

```bash
python main.py --ingest data/navigation_rules
```

系统会：
- 读取所有文档
- 将文档分割成小块
- 为每个文本块创建向量嵌入
- 存储到向量数据库中

#### 3. 交互式查询

```bash
python main.py --interactive
```

然后可以输入问题，例如：
- "渤海湾航行需要注意什么？"
- "长江口大型船舶有什么特殊要求？"
- "珠江口的主要航道有哪些？"
- "在渤海湾建立海图模型需要关注哪些要素？"

#### 4. 单次查询

```bash
python main.py --query "渤海湾航行需要注意什么？"
```

### 工作原理

1. **文档处理阶段**:
   - 读取PDF或文本格式的通航规则文档
   - 将长文档分割成重叠的文本块（便于检索）
   - 为每个文本块生成向量嵌入

2. **查询阶段**:
   - 用户输入问题
   - 将问题转换为向量嵌入
   - 在向量数据库中检索最相关的文档片段
   - 将相关文档和问题一起发送给LLM
   - LLM基于文档内容生成回答

3. **RAG（检索增强生成）**:
   - 系统使用RAG技术，确保回答基于实际文档内容
   - 避免LLM产生无根据的信息
   - 每个回答都会列出参考的源文档

### 添加自己的航行规则

1. 准备PDF文档：将通航规则PDF放入 `data/navigation_rules/` 目录
2. 文件命名：建议使用水域名称命名（如：`东海.pdf`）
3. 导入文档：运行 `python main.py --ingest data/navigation_rules`
4. 开始查询：运行 `python main.py --interactive`

### 不使用OpenAI API

系统设计为可以在没有OpenAI API的情况下工作：
- 使用简单的哈希嵌入算法（基于MD5）
- 生成的回答基于检索到的文档片段
- 适合本地部署和测试

如果需要更好的效果，建议：
- 使用OpenAI API（设置 `--api-key` 参数）
- 或者集成其他LLM服务（如Claude, 文心一言等）

### 扩展功能

未来可以添加：
- Web界面
- 更多文档格式支持（Word, Excel等）
- 海图可视化集成
- 航线规划建议
- 实时天气和海况集成

---

<a name="english"></a>
## English Documentation

### Project Overview

This is an LLM-based intelligent ship navigation knowledge management system. The system can learn navigation rules from PDF documents of different waters and help users understand navigation precautions through natural language Q&A, thereby guiding the selection and modeling of nautical chart features.

### Key Features

1. **Document Import**: Support importing navigation rule documents in PDF format (also supports plain text)
2. **Knowledge Learning**: Use LLM to understand and learn navigation rule content
3. **Intelligent Q&A**: Ask questions in natural language to get navigation precautions for specific waters
4. **Chart Guidance**: System answers indicate features to focus on in nautical charts (channels, anchorages, prohibited areas, etc.)
5. **Multi-Region Support**: Can manage navigation rules for multiple water regions simultaneously

### System Architecture

See the Chinese section above for the directory structure.

### Installation

1. Clone or download this project
2. Install dependencies:

```bash
cd ship_navigation_llm
pip install -r requirements.txt
```

3. (Optional) If using OpenAI API, set environment variable:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Usage

#### 1. Create Example Data

```bash
python main.py --create-examples
```

This creates three example files in `data/navigation_rules/`:
- 渤海湾.txt (Bohai Bay)
- 长江口.txt (Yangtze River Estuary)
- 珠江口.txt (Pearl River Estuary)

#### 2. Ingest Navigation Rule Documents

```bash
python main.py --ingest data/navigation_rules
```

The system will:
- Read all documents
- Split documents into chunks
- Create vector embeddings for each chunk
- Store in vector database

#### 3. Interactive Query Mode

```bash
python main.py --interactive
```

Then ask questions like:
- "What should I be careful about when navigating in Bohai Bay?"
- "What are the special requirements for large vessels in Yangtze River Estuary?"
- "What are the main channels in Pearl River Estuary?"
- "What features should I focus on when modeling nautical charts for Bohai Bay?"

#### 4. Single Query

```bash
python main.py --query "What should I be careful about when navigating in Bohai Bay?"
```

### How It Works

1. **Document Processing Phase**:
   - Read PDF or text format navigation rule documents
   - Split long documents into overlapping text chunks
   - Generate vector embeddings for each chunk

2. **Query Phase**:
   - User inputs question
   - Convert question to vector embedding
   - Retrieve most relevant document fragments from vector database
   - Send relevant documents and question to LLM
   - LLM generates answer based on document content

3. **RAG (Retrieval-Augmented Generation)**:
   - System uses RAG technology to ensure answers are based on actual document content
   - Prevents LLM from generating unfounded information
   - Each answer lists reference source documents

### Adding Your Own Navigation Rules

1. Prepare PDF documents: Place navigation rule PDFs in `data/navigation_rules/` directory
2. File naming: Recommend using water region name (e.g., `EastChinaSea.pdf`)
3. Import documents: Run `python main.py --ingest data/navigation_rules`
4. Start querying: Run `python main.py --interactive`

### Working Without OpenAI API

The system is designed to work without OpenAI API:
- Uses simple hash-based embedding algorithm (MD5-based)
- Generated answers based on retrieved document fragments
- Suitable for local deployment and testing

For better results, recommend:
- Using OpenAI API (set `--api-key` parameter)
- Or integrate other LLM services (Claude, Wenxin, etc.)

### Future Enhancements

Possible additions:
- Web interface
- Support for more document formats (Word, Excel, etc.)
- Nautical chart visualization integration
- Route planning suggestions
- Real-time weather and sea condition integration

### Research Application

This system is designed for research in intelligent ship navigation:
- **Understanding**: LLM learns navigation rules from various waters
- **Querying**: Ask about specific navigation precautions
- **Modeling**: Use LLM responses to select features for nautical chart modeling
- **Learning**: Feed PDFs of navigation rules from different locations

The workflow:
1. Collect navigation rule documents (PDFs) from different regions
2. Feed them to the system for learning
3. Query the system about specific waters or situations
4. Use the responses to guide feature selection in nautical charts
5. Build models based on identified features

---

## License

MIT License

## Contact

For questions or suggestions, please open an issue on GitHub.
