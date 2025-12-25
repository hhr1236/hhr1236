#!/usr/bin/env python3
"""
Example usage script for Ship Navigation LLM System
船舶航行LLM系统使用示例

This script demonstrates the complete workflow.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.navigation_system import NavigationKnowledgeSystem
from core.text_processor import TextDocumentProcessor
from data.example_navigation_rules import create_example_text_files


def example_workflow():
    """
    Demonstrate the complete workflow of the navigation system.
    演示导航系统的完整工作流程。
    """
    print("=" * 70)
    print("船舶航行知识系统 - 完整示例")
    print("Ship Navigation Knowledge System - Complete Example")
    print("=" * 70)
    
    # Step 1: Create example navigation rule files
    print("\n[步骤 1] 创建示例航行规则文件...")
    print("[Step 1] Creating example navigation rule files...")
    create_example_text_files("../data/navigation_rules")
    
    # Step 2: Initialize the system
    print("\n[步骤 2] 初始化系统...")
    print("[Step 2] Initializing system...")
    system = NavigationKnowledgeSystem(data_dir="../data")
    text_processor = TextDocumentProcessor("../data/navigation_rules")
    
    # Step 3: Process and ingest documents
    print("\n[步骤 3] 处理并导入文档...")
    print("[Step 3] Processing and ingesting documents...")
    
    documents = text_processor.batch_process_directory()
    
    for doc in documents:
        region = doc["region"]
        chunks = doc["chunks"]
        
        print(f"\n  处理水域: {region}")
        print(f"  Processing region: {region}")
        print(f"  文档块数量: {len(chunks)}")
        
        # Create embeddings
        embeddings = system.llm.batch_create_embeddings(chunks)
        
        # Store in vector store
        doc_chunks = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            doc_chunks.append({
                "text": chunk,
                "region": region,
                "source": doc["source_file"],
                "chunk_id": i
            })
        
        system.vector_store.add_documents(doc_chunks, embeddings)
        system.knowledge_base.append(doc)
    
    # Step 4: Save knowledge base
    print("\n[步骤 4] 保存知识库...")
    print("[Step 4] Saving knowledge base...")
    system.save_knowledge_base()
    
    # Step 5: Demonstrate queries
    print("\n[步骤 5] 演示查询功能...")
    print("[Step 5] Demonstrating query functionality...")
    
    # Example queries
    queries = [
        "渤海湾航行需要注意什么？",
        "长江口大型船舶有什么特殊要求？",
        "珠江口的主要航道有哪些？",
        "在建立海图模型时，渤海湾需要标注哪些要素？"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*70}")
        print(f"查询示例 {i} / Example Query {i}")
        print(f"{'='*70}")
        
        result = system.query(query, top_k=2)
        system.print_answer(result)
        
        if i < len(queries):
            input("\n按Enter继续下一个查询... (Press Enter to continue...)")
    
    # Step 6: Show statistics
    print(f"\n{'='*70}")
    print("[步骤 6] 系统统计信息")
    print("[Step 6] System Statistics")
    print(f"{'='*70}")
    
    regions = system.list_regions()
    print(f"\n已加载水域数量: {len(regions)}")
    print(f"Loaded regions: {len(regions)}")
    print(f"水域列表: {', '.join(regions)}")
    
    for region in regions:
        info = system.get_region_info(region)
        print(f"\n  {region}:")
        print(f"    文档块数量: {info.get('num_chunks', 0)}")
        print(f"    文本长度: {info.get('text_length', 0)} 字符")
    
    print(f"\n{'='*70}")
    print("示例完成！")
    print("Example completed!")
    print(f"{'='*70}")
    
    print("\n提示 (Tips):")
    print("- 使用 'python main.py --interactive' 进入交互模式")
    print("- Use 'python main.py --interactive' for interactive mode")
    print("- 添加您自己的PDF到 data/navigation_rules/ 目录")
    print("- Add your own PDFs to data/navigation_rules/ directory")
    print("- 使用 'python main.py --ingest data/navigation_rules' 导入新文档")
    print("- Use 'python main.py --ingest data/navigation_rules' to import new documents")


if __name__ == "__main__":
    try:
        example_workflow()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断 (Program interrupted by user)")
    except Exception as e:
        print(f"\n错误 (Error): {e}")
        import traceback
        traceback.print_exc()
