"""
Ship Navigation Knowledge System
船舶航行知识系统

Main system integrating PDF processing, vector storage, and LLM querying.
"""

from typing import List, Dict, Optional
from pathlib import Path
import json

from .pdf_processor import PDFProcessor
from .vector_store import VectorStore
from .llm_interface import NavigationLLM


class NavigationKnowledgeSystem:
    """
    Complete system for ship navigation knowledge management and querying.
    完整的船舶航行知识管理和查询系统。
    """
    
    def __init__(
        self,
        data_dir: str = "data",
        model_name: str = "gpt-3.5-turbo",
        api_key: Optional[str] = None
    ):
        """
        Initialize the navigation knowledge system.
        
        Args:
            data_dir: Directory for data storage
            model_name: LLM model name
            api_key: API key for LLM service
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.pdf_processor = PDFProcessor(str(self.data_dir / "pdfs"))
        self.vector_store = VectorStore(str(self.data_dir / "vector_store"))
        self.llm = NavigationLLM(model_name=model_name, api_key=api_key)
        
        self.knowledge_base = []
        
    def ingest_pdf(self, pdf_path: str, region_name: str):
        """
        Ingest a single PDF document into the system.
        将单个PDF文档导入系统。
        
        Args:
            pdf_path: Path to the PDF file
            region_name: Name of the water region
        """
        print(f"Processing PDF: {pdf_path} for region: {region_name}")
        
        # Process PDF
        processed_doc = self.pdf_processor.process_pdf(pdf_path, region_name)
        
        # Create embeddings for chunks
        print(f"Creating embeddings for {len(processed_doc['chunks'])} chunks...")
        chunk_embeddings = self.llm.batch_create_embeddings(processed_doc['chunks'])
        
        # Store chunks with metadata
        documents = []
        for i, (chunk, embedding) in enumerate(zip(processed_doc['chunks'], chunk_embeddings)):
            documents.append({
                "text": chunk,
                "region": region_name,
                "source": pdf_path,
                "chunk_id": i
            })
        
        # Add to vector store
        self.vector_store.add_documents(documents, chunk_embeddings)
        self.knowledge_base.append(processed_doc)
        
        print(f"Successfully ingested {region_name} navigation rules")
        
    def ingest_pdf_directory(self, pdf_directory: str):
        """
        Ingest all PDFs from a directory.
        从目录中导入所有PDF文件。
        
        Args:
            pdf_directory: Directory containing PDF files
        """
        pdf_dir = Path(pdf_directory)
        pdf_files = list(pdf_dir.glob("*.pdf"))
        
        print(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            region_name = pdf_file.stem
            self.ingest_pdf(str(pdf_file), region_name)
        
        print(f"\nIngestion complete. Total documents: {len(self.knowledge_base)}")
        
    def query(self, question: str, top_k: int = 3) -> Dict[str, any]:
        """
        Query the system about navigation rules.
        查询系统关于航行规则的问题。
        
        Args:
            question: User's question
            top_k: Number of relevant documents to retrieve
            
        Returns:
            Dictionary containing answer and source documents
        """
        print(f"\n查询问题: {question}")
        print("=" * 60)
        
        # Create embedding for the question
        question_embedding = self.llm.create_embedding(question)
        
        # Retrieve relevant documents
        relevant_docs = self.vector_store.similarity_search(question_embedding, top_k=top_k)
        
        print(f"\n检索到 {len(relevant_docs)} 个相关文档片段")
        for i, doc in enumerate(relevant_docs, 1):
            region = doc["document"].get("region", "未知")
            similarity = doc.get("similarity", 0)
            print(f"  {i}. {region} (相关度: {similarity:.3f})")
        
        # Generate answer using LLM
        print("\n正在生成回答...")
        answer = self.llm.query(question, relevant_docs)
        
        result = {
            "question": question,
            "answer": answer,
            "source_documents": relevant_docs,
            "timestamp": self._get_timestamp()
        }
        
        return result
    
    def save_knowledge_base(self, filename: str = "knowledge_base.json"):
        """
        Save the knowledge base to disk.
        保存知识库到磁盘。
        
        Args:
            filename: Name of the file to save
        """
        save_path = self.data_dir / filename
        
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
        
        self.vector_store.save()
        
        print(f"\nKnowledge base saved to {save_path}")
        
    def load_knowledge_base(self, filename: str = "knowledge_base.json"):
        """
        Load the knowledge base from disk.
        从磁盘加载知识库。
        
        Args:
            filename: Name of the file to load
        """
        load_path = self.data_dir / filename
        
        if load_path.exists():
            with open(load_path, 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)
            print(f"Knowledge base loaded from {load_path}")
        
        self.vector_store.load()
        
    def list_regions(self) -> List[str]:
        """
        List all water regions in the knowledge base.
        列出知识库中的所有水域。
        
        Returns:
            List of region names
        """
        regions = set()
        for doc in self.knowledge_base:
            regions.add(doc.get("region", "未知"))
        return sorted(list(regions))
    
    def get_region_info(self, region_name: str) -> Dict[str, any]:
        """
        Get information about a specific region.
        获取特定水域的信息。
        
        Args:
            region_name: Name of the region
            
        Returns:
            Dictionary containing region information
        """
        for doc in self.knowledge_base:
            if doc.get("region") == region_name:
                return {
                    "region": region_name,
                    "source_file": doc.get("source_file"),
                    "num_chunks": doc.get("metadata", {}).get("num_chunks", 0),
                    "text_length": doc.get("metadata", {}).get("text_length", 0)
                }
        return {}
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def print_answer(self, result: Dict[str, any]):
        """
        Pretty print the query result.
        美观地打印查询结果。
        
        Args:
            result: Query result dictionary
        """
        print("\n" + "=" * 60)
        print("回答 (Answer):")
        print("=" * 60)
        print(result["answer"])
        print("\n" + "=" * 60)
        print(f"来源文档数量: {len(result['source_documents'])}")
        print("=" * 60)
