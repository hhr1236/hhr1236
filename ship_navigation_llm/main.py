#!/usr/bin/env python3
"""
Main script for Ship Navigation LLM System
船舶航行LLM系统主脚本

Usage examples:
    # Interactive mode
    python main.py --interactive
    
    # Query mode
    python main.py --query "渤海湾航行需要注意什么？"
    
    # Ingest documents
    python main.py --ingest data/navigation_rules
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.navigation_system import NavigationKnowledgeSystem
from core.text_processor import TextDocumentProcessor
from data.example_navigation_rules import create_example_text_files


class NavigationCLI:
    """Command-line interface for the navigation system."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize CLI.
        
        Args:
            api_key: OpenAI API key (optional)
        """
        self.system = NavigationKnowledgeSystem(
            data_dir="data",
            api_key=api_key
        )
        self.text_processor = TextDocumentProcessor()
        
    def ingest_documents(self, directory: str):
        """
        Ingest documents from directory.
        
        Args:
            directory: Path to directory containing text files
        """
        print(f"\n开始导入文档 (Ingesting documents from {directory})...")
        print("=" * 60)
        
        documents = self.text_processor.batch_process_directory(directory)
        
        print(f"\n处理了 {len(documents)} 个文档")
        
        # Add documents to the system
        for doc in documents:
            region = doc["region"]
            chunks = doc["chunks"]
            
            print(f"\n正在为 {region} 创建嵌入向量...")
            embeddings = self.system.llm.batch_create_embeddings(chunks)
            
            # Store chunks with metadata
            doc_chunks = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                doc_chunks.append({
                    "text": chunk,
                    "region": region,
                    "source": doc["source_file"],
                    "chunk_id": i
                })
            
            self.system.vector_store.add_documents(doc_chunks, embeddings)
            self.system.knowledge_base.append(doc)
        
        # Save knowledge base
        self.system.save_knowledge_base()
        
        print(f"\n✓ 成功导入 {len(documents)} 个水域的航行规则")
        
    def query_interactive(self):
        """Run interactive query mode."""
        print("\n" + "=" * 60)
        print("船舶航行知识问答系统 (Ship Navigation Knowledge Q&A System)")
        print("=" * 60)
        
        # Try to load existing knowledge base
        try:
            self.system.load_knowledge_base()
        except Exception as e:
            print(f"未找到已保存的知识库: {e}")
            print("请先使用 --ingest 导入文档")
            return
        
        regions = self.system.list_regions()
        print(f"\n已加载水域: {', '.join(regions)}")
        print("\n输入问题进行查询，输入 'quit' 或 'exit' 退出")
        print("=" * 60)
        
        while True:
            try:
                question = input("\n问题 > ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("\n再见！")
                    break
                
                if not question:
                    continue
                
                result = self.system.query(question)
                self.system.print_answer(result)
                
            except KeyboardInterrupt:
                print("\n\n再见！")
                break
            except Exception as e:
                print(f"\n错误: {e}")
    
    def query_single(self, question: str):
        """
        Run single query.
        
        Args:
            question: Question to ask
        """
        # Load knowledge base
        try:
            self.system.load_knowledge_base()
        except Exception as e:
            print(f"错误: 未找到知识库。请先使用 --ingest 导入文档")
            return
        
        result = self.system.query(question)
        self.system.print_answer(result)
    
    def create_examples(self):
        """Create example navigation rule files."""
        print("\n创建示例航行规则文件...")
        create_example_text_files()
        print("\n✓ 示例文件已创建在 data/navigation_rules/")
        print("  使用 --ingest data/navigation_rules 导入这些文件")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="船舶航行知识系统 (Ship Navigation Knowledge System)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 1. 创建示例文件
  python main.py --create-examples
  
  # 2. 导入文档
  python main.py --ingest data/navigation_rules
  
  # 3. 交互式查询
  python main.py --interactive
  
  # 4. 单次查询
  python main.py --query "渤海湾航行需要注意什么？"
        """
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='启动交互式查询模式'
    )
    
    parser.add_argument(
        '--query', '-q',
        type=str,
        help='单次查询问题'
    )
    
    parser.add_argument(
        '--ingest',
        type=str,
        help='导入指定目录中的文档'
    )
    
    parser.add_argument(
        '--create-examples',
        action='store_true',
        help='创建示例航行规则文件'
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        help='OpenAI API密钥 (可选)'
    )
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    # Create CLI instance
    cli = NavigationCLI(api_key=args.api_key)
    
    # Handle commands
    if args.create_examples:
        cli.create_examples()
    
    if args.ingest:
        cli.ingest_documents(args.ingest)
    
    if args.interactive:
        cli.query_interactive()
    
    if args.query:
        cli.query_single(args.query)


if __name__ == "__main__":
    main()
