"""
Text-based Document Processor (Alternative to PDF)
基于文本的文档处理器（PDF的替代方案）

For systems where PDF processing is not available or for text-based inputs.
"""

from typing import List, Dict
from pathlib import Path


class TextDocumentProcessor:
    """
    Process plain text documents containing navigation rules.
    处理包含航行规则的纯文本文档。
    """
    
    def __init__(self, data_dir: str = "data/navigation_rules"):
        """
        Initialize text document processor.
        
        Args:
            data_dir: Directory containing text files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def load_text_file(self, file_path: str) -> str:
        """
        Load text from a file.
        从文件加载文本。
        
        Args:
            file_path: Path to text file
            
        Returns:
            File content as string
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks.
        将文本分割成重叠的块。
        
        Args:
            text: Input text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Number of overlapping characters between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += (chunk_size - overlap)
            
        return chunks
    
    def process_text_file(self, file_path: str, region_name: str = None) -> Dict[str, any]:
        """
        Process a text file and extract structured information.
        处理文本文件并提取结构化信息。
        
        Args:
            file_path: Path to text file
            region_name: Name of the water region (defaults to filename)
            
        Returns:
            Dictionary containing processed information
        """
        if region_name is None:
            region_name = Path(file_path).stem
        
        text = self.load_text_file(file_path)
        chunks = self.chunk_text(text)
        
        return {
            "region": region_name,
            "source_file": file_path,
            "full_text": text,
            "chunks": chunks,
            "metadata": {
                "num_chunks": len(chunks),
                "text_length": len(text)
            }
        }
    
    def batch_process_directory(self, directory: str = None) -> List[Dict[str, any]]:
        """
        Process all text files in a directory.
        处理目录中的所有文本文件。
        
        Args:
            directory: Directory containing text files (defaults to self.data_dir)
            
        Returns:
            List of processed documents
        """
        if directory is None:
            directory = self.data_dir
        else:
            directory = Path(directory)
        
        documents = []
        
        for text_file in directory.glob("*.txt"):
            region_name = text_file.stem
            doc = self.process_text_file(str(text_file), region_name)
            documents.append(doc)
            print(f"Processed: {region_name}")
        
        return documents
