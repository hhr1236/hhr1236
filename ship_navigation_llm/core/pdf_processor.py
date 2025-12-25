"""
PDF Document Processor for Navigation Rules
PDF文档处理器 - 用于处理不同水域的通航规则PDF
"""

import os
from typing import List, Dict, Optional
from pathlib import Path


class PDFProcessor:
    """
    Process PDF documents containing navigation rules.
    处理包含航行规则的PDF文档。
    """
    
    def __init__(self, data_dir: str = "data/pdfs"):
        """
        Initialize PDF processor.
        
        Args:
            data_dir: Directory to store PDF files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text content from PDF file.
        从PDF文件中提取文本内容。
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        try:
            # Using PyPDF2 for PDF extraction
            import PyPDF2
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except ImportError:
            # Fallback: if PyPDF2 is not installed, use pdfplumber
            try:
                import pdfplumber
                
                with pdfplumber.open(pdf_path) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"
                    return text
            except ImportError:
                raise ImportError(
                    "Please install PyPDF2 or pdfplumber: "
                    "pip install PyPDF2 or pip install pdfplumber"
                )
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks for better context preservation.
        将文本分割成重叠的块以更好地保留上下文。
        
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
    
    def process_pdf(self, pdf_path: str, region_name: str) -> Dict[str, any]:
        """
        Process a PDF file and extract structured information.
        处理PDF文件并提取结构化信息。
        
        Args:
            pdf_path: Path to PDF file
            region_name: Name of the water region (e.g., "渤海湾", "长江口")
            
        Returns:
            Dictionary containing processed information
        """
        text = self.extract_text_from_pdf(pdf_path)
        chunks = self.chunk_text(text)
        
        return {
            "region": region_name,
            "source_file": pdf_path,
            "full_text": text,
            "chunks": chunks,
            "metadata": {
                "num_chunks": len(chunks),
                "text_length": len(text)
            }
        }
    
    def batch_process_pdfs(self, pdf_directory: str) -> List[Dict[str, any]]:
        """
        Process all PDFs in a directory.
        处理目录中的所有PDF文件。
        
        Args:
            pdf_directory: Directory containing PDF files
            
        Returns:
            List of processed documents
        """
        pdf_dir = Path(pdf_directory)
        documents = []
        
        for pdf_file in pdf_dir.glob("*.pdf"):
            region_name = pdf_file.stem  # Use filename as region name
            doc = self.process_pdf(str(pdf_file), region_name)
            documents.append(doc)
            
        return documents
