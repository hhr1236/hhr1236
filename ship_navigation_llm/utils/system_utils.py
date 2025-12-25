#!/usr/bin/env python3
"""
Utility functions for Ship Navigation LLM System
辅助工具函数
"""

import os
import json
from pathlib import Path
from typing import Dict, List


def check_system_status(data_dir: str = "data") -> Dict[str, any]:
    """
    Check the current status of the system.
    检查系统当前状态。
    
    Args:
        data_dir: Data directory path
        
    Returns:
        Dictionary with system status information
    """
    data_path = Path(data_dir)
    
    status = {
        "data_dir_exists": data_path.exists(),
        "navigation_rules_dir": None,
        "vector_store_exists": False,
        "knowledge_base_exists": False,
        "num_documents": 0,
        "num_regions": 0,
        "regions": []
    }
    
    # Check navigation rules directory
    nav_rules_dir = data_path / "navigation_rules"
    if nav_rules_dir.exists():
        txt_files = list(nav_rules_dir.glob("*.txt"))
        pdf_files = list(nav_rules_dir.glob("*.pdf"))
        status["navigation_rules_dir"] = {
            "exists": True,
            "txt_files": len(txt_files),
            "pdf_files": len(pdf_files),
            "total_files": len(txt_files) + len(pdf_files)
        }
    
    # Check vector store
    vector_store_file = data_path / "vector_store" / "vector_store.json"
    status["vector_store_exists"] = vector_store_file.exists()
    
    # Check knowledge base
    kb_file = data_path / "knowledge_base.json"
    if kb_file.exists():
        status["knowledge_base_exists"] = True
        try:
            with open(kb_file, 'r', encoding='utf-8') as f:
                kb_data = json.load(f)
                status["num_documents"] = len(kb_data)
                regions = [doc.get("region", "未知") for doc in kb_data]
                status["regions"] = sorted(set(regions))
                status["num_regions"] = len(status["regions"])
        except Exception as e:
            print(f"Error reading knowledge base: {e}")
    
    return status


def print_system_status(data_dir: str = "data"):
    """
    Print system status in a readable format.
    以可读格式打印系统状态。
    
    Args:
        data_dir: Data directory path
    """
    status = check_system_status(data_dir)
    
    print("=" * 60)
    print("系统状态检查 (System Status Check)")
    print("=" * 60)
    
    # Data directory
    print(f"\n📁 数据目录: {status['data_dir_exists']}")
    if status['data_dir_exists']:
        print("   ✓ 数据目录存在")
    else:
        print("   ✗ 数据目录不存在")
    
    # Navigation rules
    print(f"\n📄 航行规则文档:")
    if status['navigation_rules_dir']:
        nav_info = status['navigation_rules_dir']
        print(f"   ✓ 目录存在")
        print(f"   - TXT文件: {nav_info['txt_files']}")
        print(f"   - PDF文件: {nav_info['pdf_files']}")
        print(f"   - 总计: {nav_info['total_files']} 个文件")
    else:
        print("   ✗ 目录不存在或为空")
    
    # Vector store
    print(f"\n🔍 向量存储:")
    if status['vector_store_exists']:
        print("   ✓ 向量存储已创建")
    else:
        print("   ✗ 向量存储未创建 (需要先导入文档)")
    
    # Knowledge base
    print(f"\n📚 知识库:")
    if status['knowledge_base_exists']:
        print("   ✓ 知识库已创建")
        print(f"   - 文档数量: {status['num_documents']}")
        print(f"   - 水域数量: {status['num_regions']}")
        if status['regions']:
            print(f"   - 水域列表: {', '.join(status['regions'])}")
    else:
        print("   ✗ 知识库未创建 (需要先导入文档)")
    
    print("\n" + "=" * 60)
    
    # Recommendations
    print("\n💡 建议 (Recommendations):")
    if not status['navigation_rules_dir'] or status['navigation_rules_dir']['total_files'] == 0:
        print("   1. 运行: python main.py --create-examples")
        print("      (创建示例文档)")
    
    if not status['knowledge_base_exists']:
        print("   2. 运行: python main.py --ingest data/navigation_rules")
        print("      (导入文档到系统)")
    
    if status['knowledge_base_exists']:
        print("   3. 运行: python main.py --interactive")
        print("      (开始查询)")
    
    print()


def clean_data(data_dir: str = "data", confirm: bool = True):
    """
    Clean all data (vector store and knowledge base).
    清理所有数据（向量存储和知识库）。
    
    Args:
        data_dir: Data directory path
        confirm: Ask for confirmation before deleting
    """
    data_path = Path(data_dir)
    
    files_to_delete = [
        data_path / "vector_store" / "vector_store.json",
        data_path / "knowledge_base.json"
    ]
    
    print("=" * 60)
    print("清理数据 (Clean Data)")
    print("=" * 60)
    print("\n将要删除以下文件:")
    for f in files_to_delete:
        if f.exists():
            print(f"   - {f}")
    
    if confirm:
        response = input("\n确认删除? (y/n): ").strip().lower()
        if response != 'y':
            print("操作已取消")
            return
    
    deleted_count = 0
    for f in files_to_delete:
        if f.exists():
            try:
                f.unlink()
                print(f"✓ 已删除: {f}")
                deleted_count += 1
            except Exception as e:
                print(f"✗ 删除失败: {f} - {e}")
    
    print(f"\n完成！删除了 {deleted_count} 个文件")
    print("运行 'python main.py --ingest data/navigation_rules' 重新导入文档")


def list_documents(data_dir: str = "data"):
    """
    List all documents in the knowledge base.
    列出知识库中的所有文档。
    
    Args:
        data_dir: Data directory path
    """
    kb_file = Path(data_dir) / "knowledge_base.json"
    
    if not kb_file.exists():
        print("知识库不存在。请先导入文档。")
        return
    
    try:
        with open(kb_file, 'r', encoding='utf-8') as f:
            kb_data = json.load(f)
        
        print("=" * 60)
        print("知识库文档列表 (Knowledge Base Documents)")
        print("=" * 60)
        print(f"\n总计: {len(kb_data)} 个文档\n")
        
        for i, doc in enumerate(kb_data, 1):
            region = doc.get("region", "未知")
            source = doc.get("source_file", "未知")
            metadata = doc.get("metadata", {})
            num_chunks = metadata.get("num_chunks", 0)
            text_length = metadata.get("text_length", 0)
            
            print(f"{i}. 水域: {region}")
            print(f"   来源: {source}")
            print(f"   文档块数: {num_chunks}")
            print(f"   文本长度: {text_length} 字符")
            print()
        
    except Exception as e:
        print(f"读取知识库失败: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "status":
            print_system_status()
        elif command == "clean":
            clean_data()
        elif command == "list":
            list_documents()
        else:
            print(f"未知命令: {command}")
            print("\n可用命令:")
            print("  status - 检查系统状态")
            print("  clean  - 清理数据")
            print("  list   - 列出文档")
    else:
        print_system_status()
