"""
LLM Interface for Navigation Query
LLM接口 - 用于航行查询
"""

from typing import List, Dict, Optional
import json


class NavigationLLM:
    """
    Interface with LLM for navigation rule understanding and querying.
    与LLM交互以理解和查询航行规则。
    """
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", api_key: Optional[str] = None):
        """
        Initialize LLM interface.
        
        Args:
            model_name: Name of the LLM model to use
            api_key: API key for the LLM service
        """
        self.model_name = model_name
        self.api_key = api_key
        self.conversation_history = []
        
    def create_embedding(self, text: str) -> List[float]:
        """
        Create embedding for text using the LLM.
        使用LLM为文本创建嵌入。
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        try:
            import openai
            
            if self.api_key:
                openai.api_key = self.api_key
                
            response = openai.Embedding.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response['data'][0]['embedding']
            
        except ImportError:
            # Fallback: simple hash-based embedding for demonstration
            print("Warning: OpenAI not installed. Using simple embedding.")
            return self._simple_embedding(text)
        except Exception as e:
            print(f"Error creating embedding: {e}")
            return self._simple_embedding(text)
    
    def _simple_embedding(self, text: str, dim: int = 384) -> List[float]:
        """
        Create a simple embedding based on text hash (fallback).
        基于文本哈希创建简单嵌入（后备方案）。
        
        Args:
            text: Input text
            dim: Embedding dimension
            
        Returns:
            Simple embedding vector
        """
        import hashlib
        import numpy as np
        
        # Create deterministic embedding from text hash
        hash_obj = hashlib.md5(text.encode('utf-8'))
        seed = int(hash_obj.hexdigest(), 16) % (2**32)
        np.random.seed(seed)
        
        embedding = np.random.randn(dim)
        embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
        
        return embedding.tolist()
    
    def batch_create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for multiple texts.
        为多个文本创建嵌入。
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        return [self.create_embedding(text) for text in texts]
    
    def query(self, question: str, context_documents: List[Dict[str, any]] = None) -> str:
        """
        Query the LLM about navigation rules.
        查询LLM关于航行规则的问题。
        
        Args:
            question: User's question
            context_documents: Relevant documents for context
            
        Returns:
            LLM response
        """
        # Build context from documents
        context = ""
        if context_documents:
            context = "\n\n相关文档内容 (Relevant Documents):\n"
            for i, doc in enumerate(context_documents, 1):
                doc_text = doc.get("document", {}).get("text", "")
                region = doc.get("document", {}).get("region", "未知")
                context += f"\n[文档 {i} - {region}]:\n{doc_text}\n"
        
        # Create prompt
        prompt = f"""你是一个专业的船舶航行专家，精通各个水域的通航规则和航行注意事项。

{context}

用户问题: {question}

请基于以上文档内容，提供详细、准确的回答。如果文档中没有相关信息，请说明你不确定。

回答时请注意：
1. 列出具体的航行注意点
2. 说明适用的水域或区域
3. 如果涉及海图要素，请明确指出需要关注的要素类型（如航道、锚地、禁航区等）
4. 提供安全建议

回答:"""

        try:
            import openai
            
            if self.api_key:
                openai.api_key = self.api_key
            
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一个专业的船舶航行专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            return answer
            
        except ImportError:
            # Fallback response when OpenAI is not available
            return self._generate_fallback_response(question, context_documents)
        except Exception as e:
            return f"错误: 无法获取LLM响应。{str(e)}\n\n使用后备响应模式...\n\n" + \
                   self._generate_fallback_response(question, context_documents)
    
    def _generate_fallback_response(self, question: str, context_documents: List[Dict[str, any]] = None) -> str:
        """
        Generate a fallback response when LLM is not available.
        当LLM不可用时生成后备响应。
        
        Args:
            question: User's question
            context_documents: Relevant documents
            
        Returns:
            Fallback response
        """
        response = f"问题: {question}\n\n"
        response += "基于检索到的文档，以下是相关的航行注意事项:\n\n"
        
        if context_documents:
            for i, doc in enumerate(context_documents, 1):
                doc_text = doc.get("document", {}).get("text", "")
                region = doc.get("document", {}).get("region", "未知")
                similarity = doc.get("similarity", 0)
                
                response += f"{i}. 【{region}水域】(相关度: {similarity:.2f})\n"
                response += f"   {doc_text[:200]}...\n\n"
        else:
            response += "未找到相关文档。请确保已加载导航规则PDF文件。\n"
        
        response += "\n建议:\n"
        response += "- 请查阅完整的通航规则文档\n"
        response += "- 在海图上标注相关航道、锚地和禁航区\n"
        response += "- 咨询当地海事部门获取最新规定\n"
        
        return response
