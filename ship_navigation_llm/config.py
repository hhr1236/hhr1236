"""
Configuration file for Ship Navigation LLM System
船舶航行LLM系统配置文件
"""

# Data directories
DATA_DIR = "data"
NAVIGATION_RULES_DIR = "data/navigation_rules"
VECTOR_STORE_DIR = "data/vector_store"
PDF_DIR = "data/pdfs"

# LLM settings
DEFAULT_MODEL = "gpt-3.5-turbo"
EMBEDDING_MODEL = "text-embedding-ada-002"
FALLBACK_EMBEDDING_DIM = 384

# Text processing settings
CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 200  # Overlapping characters between chunks

# Vector search settings
TOP_K_RESULTS = 3  # Number of documents to retrieve for each query

# LLM generation settings
TEMPERATURE = 0.7
MAX_TOKENS = 1000

# System prompts
SYSTEM_PROMPT = "你是一个专业的船舶航行专家，精通各个水域的通航规则和航行注意事项。"

QUERY_PROMPT_TEMPLATE = """你是一个专业的船舶航行专家，精通各个水域的通航规则和航行注意事项。

{context}

用户问题: {question}

请基于以上文档内容，提供详细、准确的回答。如果文档中没有相关信息，请说明你不确定。

回答时请注意：
1. 列出具体的航行注意点
2. 说明适用的水域或区域
3. 如果涉及海图要素，请明确指出需要关注的要素类型（如航道、锚地、禁航区等）
4. 提供安全建议

回答:"""

# Nautical chart features to highlight
NAUTICAL_CHART_FEATURES = [
    "航道 (Channels)",
    "锚地 (Anchorages)", 
    "禁航区 (Prohibited Areas)",
    "警戒区 (Caution Areas)",
    "浅水区 (Shallow Waters)",
    "沉船 (Wrecks)",
    "导航标志 (Navigation Marks)",
    "灯塔 (Lighthouses)",
    "潮汐站 (Tide Stations)",
    "交通分隔带 (Traffic Separation Schemes)"
]

# Supported water regions (can be extended)
WATER_REGIONS = [
    "渤海湾 (Bohai Bay)",
    "长江口 (Yangtze River Estuary)",
    "珠江口 (Pearl River Estuary)",
    "东海 (East China Sea)",
    "南海 (South China Sea)",
    "黄海 (Yellow Sea)",
    "台湾海峡 (Taiwan Strait)"
]
