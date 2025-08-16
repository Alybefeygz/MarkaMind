import openai
import httpx
from typing import List, Dict, Optional, Any
import os
import asyncio
import logging
from pathlib import Path
import json
import re
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    AI and Embedding service for chatbot functionality
    
    Handles text embedding, similarity search, AI response generation,
    and knowledge base processing using OpenRouter API.
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize EmbeddingService
        
        Args:
            api_key: OpenRouter API key (defaults to env var)
            base_url: OpenRouter base URL (defaults to env var)
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = base_url or os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.default_model = os.getenv("DEFAULT_MODEL", "meta-llama/llama-3.1-8b-instruct:free")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("MAX_TOKENS", "4000"))
        
        # Rate limiting
        self.rate_limit_calls = 60  # calls per minute
        self.rate_limit_window = 60  # seconds
        self.call_history = []
        
        # Configure OpenAI client for OpenRouter
        if self.api_key:
            openai.api_key = self.api_key
            openai.api_base = self.base_url
        
        logger.info("EmbeddingService initialized")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
            
        Raises:
            ValueError: If text is empty or too long
            Exception: If API call fails
        """
        try:
            if not text or not text.strip():
                raise ValueError("Text cannot be empty")
            
            # Clean and truncate text
            cleaned_text = self._clean_text(text)
            if len(cleaned_text) > 8000:  # Reasonable limit for embeddings
                cleaned_text = cleaned_text[:8000]
                logger.warning("Text truncated for embedding generation")
            
            logger.info(f"Generating embedding for text ({len(cleaned_text)} chars)")
            
            # Rate limiting check
            await self._check_rate_limit()
            
            # Generate embedding using OpenAI API (compatible with OpenRouter)
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.embedding_model,
                        "input": cleaned_text
                    }
                )
                
                if response.status_code != 200:
                    error_msg = f"Embedding API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
                result = response.json()
                embedding = result["data"][0]["embedding"]
                
                logger.info("Embedding generated successfully")
                return embedding
                
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            raise Exception(f"Failed to generate embedding: {str(e)}")
    
    async def find_similar_content(self, query_embedding: List[float], knowledge_base_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find similar content using embedding similarity
        
        Args:
            query_embedding: Query embedding vector
            knowledge_base_id: ID of the knowledge base (chatbot_id)
            limit: Maximum number of results
            
        Returns:
            List of similar content with similarity scores
            
        Note:
            This is a simplified implementation. In production, you'd use
            a vector database like Pinecone, Weaviate, or pgvector.
        """
        try:
            logger.info(f"Finding similar content for chatbot {knowledge_base_id}")
            
            # This is a placeholder implementation
            # In a real system, you would:
            # 1. Query a vector database
            # 2. Calculate cosine similarity
            # 3. Return ranked results
            
            # For now, return mock similar content
            similar_content = [
                {
                    "id": "mock-1",
                    "content": "This is a mock similar content entry.",
                    "similarity_score": 0.85,
                    "source_type": "text",
                    "source_url": None
                },
                {
                    "id": "mock-2", 
                    "content": "Another mock content entry for testing.",
                    "similarity_score": 0.78,
                    "source_type": "url",
                    "source_url": "https://example.com"
                }
            ]
            
            logger.info(f"Found {len(similar_content)} similar content entries")
            return similar_content[:limit]
            
        except Exception as e:
            logger.error(f"Failed to find similar content: {str(e)}")
            return []
    
    async def generate_ai_response(self, user_message: str, context: List[Dict[str, Any]], chatbot_config: Dict[str, Any]) -> str:
        """
        Generate AI response using OpenRouter API
        
        Args:
            user_message: User's message
            context: Similar content for context
            chatbot_config: Chatbot configuration
            
        Returns:
            AI-generated response
            
        Raises:
            ValueError: If message is empty
            Exception: If API call fails
        """
        try:
            if not user_message or not user_message.strip():
                raise ValueError("User message cannot be empty")
            
            logger.info(f"Generating AI response for message: {user_message[:50]}...")
            
            # Rate limiting check
            await self._check_rate_limit()
            
            # Build context from similar content
            context_text = ""
            if context:
                context_text = "\n\nRelevant information:\n"
                for item in context[:3]:  # Use top 3 similar items
                    context_text += f"- {item.get('content', '')}\n"
            
            # Create system prompt
            chatbot_name = chatbot_config.get("name", "Assistant")
            brand_name = chatbot_config.get("brand", {}).get("name", "Company")
            
            system_prompt = f"""You are {chatbot_name}, a helpful AI assistant for {brand_name}. 
            Respond in a friendly, professional manner. If you don't know something, say so honestly.
            Keep responses concise and helpful.{context_text}"""
            
            # Generate response using OpenRouter
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.default_model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message}
                        ],
                        "temperature": self.temperature,
                        "max_tokens": min(self.max_tokens, 1000),  # Reasonable limit for chat
                        "stream": False
                    }
                )
                
                if response.status_code != 200:
                    error_msg = f"AI API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    # Fallback response
                    return f"I'm sorry, I'm having trouble processing your request right now. Please try again later."
                
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"].strip()
                
                logger.info("AI response generated successfully")
                return ai_response
                
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to generate AI response: {str(e)}")
            # Return fallback response instead of raising
            return f"Hello! I'm {chatbot_config.get('name', 'your assistant')}. How can I help you today?"
    
    async def process_knowledge_content(self, content: str, chatbot_id: str, source_type: str = "text", source_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Process knowledge content for storage
        
        Args:
            content: Text content to process
            chatbot_id: ID of the chatbot
            source_type: Type of source (text, url, file, document)
            source_url: URL of the source (if applicable)
            
        Returns:
            Processed content data with embedding and metadata
            
        Raises:
            ValueError: If content is invalid
            Exception: If processing fails
        """
        try:
            if not content or not content.strip():
                raise ValueError("Content cannot be empty")
            
            logger.info(f"Processing knowledge content for chatbot {chatbot_id}")
            
            # Clean and prepare content
            cleaned_content = self._clean_text(content)
            
            # Count tokens (approximate)
            token_count = self.count_tokens(cleaned_content)
            
            # Generate embedding
            try:
                embedding = await self.generate_embedding(cleaned_content)
                embedding_status = "success"
            except Exception as e:
                logger.warning(f"Failed to generate embedding: {str(e)}")
                embedding = []
                embedding_status = "failed"
            
            # Extract metadata
            metadata = {
                "token_count": token_count,
                "character_count": len(cleaned_content),
                "word_count": len(cleaned_content.split()),
                "source_type": source_type,
                "source_url": source_url,
                "processed_at": datetime.utcnow().isoformat(),
                "embedding_status": embedding_status
            }
            
            processed_data = {
                "chatbot_id": chatbot_id,
                "content": cleaned_content,
                "embedding": embedding,
                "metadata": metadata,
                "status": "processed" if embedding_status == "success" else "pending"
            }
            
            logger.info(f"Knowledge content processed successfully: {token_count} tokens")
            return processed_data
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to process knowledge content: {str(e)}")
            raise Exception(f"Failed to process knowledge content: {str(e)}")
    
    def count_tokens(self, text: str) -> int:
        """
        Count approximate number of tokens in text
        
        Args:
            text: Input text
            
        Returns:
            Approximate token count
            
        Note:
            This is a rough approximation. For accurate counting,
            you'd use tiktoken or similar library.
        """
        try:
            if not text:
                return 0
            
            # Rough approximation: 1 token ≈ 4 characters for English
            # More accurate would be to use tiktoken library
            words = text.split()
            # Average tokens per word is about 1.3 for English
            token_count = int(len(words) * 1.3)
            
            return token_count
            
        except Exception as e:
            logger.error(f"Failed to count tokens: {str(e)}")
            return 0
    
    async def extract_text_from_file(self, file_path: str) -> str:
        """
        Extract text content from various file types
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text content
            
        Raises:
            ValueError: If file not found or unsupported
            Exception: If extraction fails
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise ValueError(f"File not found: {file_path}")
            
            logger.info(f"Extracting text from file: {file_path.name}")
            
            # Get file extension
            extension = file_path.suffix.lower()
            
            if extension == ".txt":
                return await self._extract_from_txt(file_path)
            elif extension == ".md":
                return await self._extract_from_markdown(file_path)
            elif extension == ".json":
                return await self._extract_from_json(file_path)
            elif extension == ".csv":
                return await self._extract_from_csv(file_path)
            elif extension in [".pdf"]:
                # PDF extraction would require additional libraries
                raise ValueError("PDF extraction not implemented yet")
            elif extension in [".doc", ".docx"]:
                # Word document extraction would require additional libraries
                raise ValueError("Word document extraction not implemented yet")
            else:
                raise ValueError(f"Unsupported file type: {extension}")
                
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to extract text from file: {str(e)}")
            raise Exception(f"Failed to extract text from file: {str(e)}")
    
    async def _extract_from_txt(self, file_path: Path) -> str:
        """Extract text from .txt file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self._clean_text(content)
        except Exception as e:
            raise Exception(f"Failed to read text file: {str(e)}")
    
    async def _extract_from_markdown(self, file_path: Path) -> str:
        """Extract text from .md file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove markdown formatting (basic)
            content = re.sub(r'#{1,6}\s*', '', content)  # Headers
            content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # Bold
            content = re.sub(r'\*(.*?)\*', r'\1', content)  # Italic
            content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)  # Links
            
            return self._clean_text(content)
        except Exception as e:
            raise Exception(f"Failed to read markdown file: {str(e)}")
    
    async def _extract_from_json(self, file_path: Path) -> str:
        """Extract text from .json file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert JSON to readable text
            def json_to_text(obj, prefix=""):
                text = ""
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        text += f"{prefix}{key}: {json_to_text(value, prefix + '  ')}\n"
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        text += f"{prefix}Item {i+1}: {json_to_text(item, prefix + '  ')}\n"
                else:
                    text += str(obj)
                return text
            
            content = json_to_text(data)
            return self._clean_text(content)
        except Exception as e:
            raise Exception(f"Failed to read JSON file: {str(e)}")
    
    async def _extract_from_csv(self, file_path: Path) -> str:
        """Extract text from .csv file"""
        try:
            import csv
            
            content = ""
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row_num, row in enumerate(reader):
                    if row_num == 0:
                        content += f"Headers: {', '.join(row)}\n"
                    else:
                        content += f"Row {row_num}: {', '.join(row)}\n"
            
            return self._clean_text(content)
        except Exception as e:
            raise Exception(f"Failed to read CSV file: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text content
        
        Args:
            text: Raw text input
            
        Returns:
            Cleaned text
        """
        try:
            if not text:
                return ""
            
            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Remove special characters but keep basic punctuation
            text = re.sub(r'[^\w\s\.,!?;:()\-\'"]+', '', text)
            
            # Trim whitespace
            text = text.strip()
            
            return text
            
        except Exception as e:
            logger.error(f"Failed to clean text: {str(e)}")
            return text
    
    async def _check_rate_limit(self):
        """
        Check and enforce rate limiting
        
        Raises:
            Exception: If rate limit exceeded
        """
        try:
            current_time = time.time()
            
            # Remove calls outside the window
            self.call_history = [
                call_time for call_time in self.call_history 
                if current_time - call_time < self.rate_limit_window
            ]
            
            # Check if we're at the limit
            if len(self.call_history) >= self.rate_limit_calls:
                sleep_time = self.rate_limit_window - (current_time - self.call_history[0])
                if sleep_time > 0:
                    logger.warning(f"Rate limited, waiting {sleep_time:.2f} seconds")
                    await asyncio.sleep(sleep_time)
            
            # Add current call to history
            self.call_history.append(current_time)
            
        except Exception as e:
            logger.error(f"Rate limiting error: {str(e)}")
            # Don't block on rate limiting errors
            pass
    
    async def get_knowledge_base_summary(self, chatbot_id: str) -> Dict[str, Any]:
        """
        Get summary of knowledge base for a chatbot
        
        Args:
            chatbot_id: ID of the chatbot
            
        Returns:
            Knowledge base summary statistics
        """
        try:
            logger.info(f"Getting knowledge base summary for chatbot {chatbot_id}")
            
            # This would typically query your database
            # For now, return mock summary
            summary = {
                "total_entries": 0,
                "total_tokens": 0,
                "processed_entries": 0,
                "pending_entries": 0,
                "average_similarity_threshold": 0.75,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get knowledge base summary: {str(e)}")
            return {
                "total_entries": 0,
                "total_tokens": 0,
                "processed_entries": 0,
                "pending_entries": 0,
                "error": str(e)
            }