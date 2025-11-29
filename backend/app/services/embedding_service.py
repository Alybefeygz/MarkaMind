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

    Handles text processing, AI response generation (fallback mode),
    and knowledge base processing.

    Note: OpenRouter integration removed. Gemini API integration pending.
    """
    
    def __init__(self):
        """
        Initialize EmbeddingService

        Note: OpenRouter integration removed.
        TODO: Integrate Gemini API for AI responses
        """
        # Rate limiting
        self.rate_limit_calls = 60  # calls per minute
        self.rate_limit_window = 60  # seconds
        self.call_history = []

        logger.info("EmbeddingService initialized (temporary fallback mode)")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text (Temporary disabled)

        Args:
            text: Text to embed

        Returns:
            Empty embedding vector (embedding generation disabled)

        Raises:
            ValueError: If text is empty
        """
        try:
            if not text or not text.strip():
                raise ValueError("Text cannot be empty")

            logger.info(f"Embedding generation skipped (not implemented)")

            # TODO: Integrate Gemini API for embeddings
            # Return empty embedding for now
            return []

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            return []
    
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
    
    async def generate_ai_response(
        self,
        user_message: str,
        context: List[Dict[str, Any]],
        chatbot_config: Dict[str, Any],
        conversation_id: Optional[str] = None,
        chatbot_id: Optional[str] = None
    ) -> str:
        """
        Generate AI response (Temporary fallback - AI integration pending)

        Args:
            user_message: User's message
            context: Similar content for context
            chatbot_config: Chatbot configuration
            conversation_id: Conversation ID (for logging)
            chatbot_id: Chatbot ID (for logging)

        Returns:
            AI-generated response

        Raises:
            ValueError: If message is empty
        """
        try:
            if not user_message or not user_message.strip():
                raise ValueError("User message cannot be empty")

            logger.info(f"Generating response for message: {user_message[:50]}...")

            # Get chatbot info
            chatbot_name = chatbot_config.get("name", "Assistant")

            # Temporary fallback response
            # TODO: Integrate Gemini API for real AI responses
            responses = [
                f"Merhaba! Ben {chatbot_name}. Size nasıl yardımcı olabilirim?",
                f"Mesajınızı aldım: '{user_message}'. Şu anda AI entegrasyonu tamamlanıyor.",
                f"Teşekkürler! {chatbot_name} olarak size yardımcı olmak isterim.",
            ]

            # Simple response based on message length
            if len(user_message) < 20:
                response = responses[0]
            elif "?" in user_message:
                response = responses[1]
            else:
                response = responses[2]

            logger.info("Response generated successfully (fallback)")
            return response

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to generate response: {str(e)}")
            # Return simple fallback
            return f"Merhaba! Ben {chatbot_config.get('name', 'asistanınız')}. Size nasıl yardımcı olabilirim?"
    
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


# Singleton instance
embedding_service = EmbeddingService()