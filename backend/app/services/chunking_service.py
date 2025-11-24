"""
Chunking Service
PDF metinlerini anlamsal chunk'lara bölen servis
"""
import re
from typing import List, Dict, Any
from uuid import UUID


class ChunkingService:
    """Smart text chunking service for RAG"""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_chunk_size: int = 100
    ):
        """
        Initialize chunking service

        Args:
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlapping characters between chunks
            min_chunk_size: Minimum chunk size (smaller chunks are discarded)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

    def chunk_text(self, text: str, source_name: str = "") -> List[Dict[str, Any]]:
        """
        Split text into smart chunks with overlap

        Args:
            text: Input text to chunk
            source_name: Name of the source document

        Returns:
            List of chunk dictionaries with content, metadata, and token count
        """
        if not text or len(text.strip()) == 0:
            return []

        # Clean text
        text = self._clean_text(text)

        chunks = []
        current_pos = 0
        chunk_index = 0

        while current_pos < len(text):
            # Calculate chunk end position
            end_pos = min(current_pos + self.chunk_size, len(text))

            # If we're at the end, take all remaining text
            if end_pos >= len(text):
                chunk_text = text[current_pos:].strip()
                if len(chunk_text) >= self.min_chunk_size:
                    chunks.append(self._create_chunk(
                        content=chunk_text,
                        chunk_index=chunk_index,
                        start_char=current_pos,
                        end_char=len(text),
                        source_name=source_name
                    ))
                break

            # Extract chunk text
            chunk_text = text[current_pos:end_pos]

            # Try to break at paragraph boundary
            break_point = self._find_break_point(chunk_text)

            if break_point != -1:
                end_pos = current_pos + break_point

            # Get final chunk text
            final_chunk = text[current_pos:end_pos].strip()

            # Only add if meets minimum size
            if len(final_chunk) >= self.min_chunk_size:
                chunks.append(self._create_chunk(
                    content=final_chunk,
                    chunk_index=chunk_index,
                    start_char=current_pos,
                    end_char=end_pos,
                    source_name=source_name
                ))
                chunk_index += 1

            # Move to next position with overlap
            current_pos = end_pos - self.chunk_overlap

            # Prevent infinite loop
            if current_pos <= 0:
                current_pos = end_pos

        return chunks

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove excessive newlines (keep max 2)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def _find_break_point(self, text: str) -> int:
        """
        Find the best position to break the chunk
        Tries: paragraph > sentence > word boundary

        Returns:
            Position to break, or -1 if no good break point found
        """
        # Try paragraph break (double newline)
        last_para = text.rfind('\n\n')
        if last_para != -1 and last_para > len(text) * 0.5:
            return last_para + 2

        # Try sentence break (. ! ?)
        sentence_ends = [
            text.rfind('. '),
            text.rfind('! '),
            text.rfind('? ')
        ]
        last_sentence = max(sentence_ends)
        if last_sentence != -1 and last_sentence > len(text) * 0.3:
            return last_sentence + 2

        # Try single newline
        last_newline = text.rfind('\n')
        if last_newline != -1 and last_newline > len(text) * 0.3:
            return last_newline + 1

        # Try word boundary
        last_space = text.rfind(' ')
        if last_space != -1 and last_space > len(text) * 0.2:
            return last_space + 1

        return -1

    def _create_chunk(
        self,
        content: str,
        chunk_index: int,
        start_char: int,
        end_char: int,
        source_name: str
    ) -> Dict[str, Any]:
        """Create chunk dictionary with metadata"""
        token_count = self._estimate_tokens(content)

        return {
            "chunk_index": chunk_index,
            "content": content,
            "token_count": token_count,
            "metadata": {
                "chunk_size": len(content),
                "overlap": self.chunk_overlap,
                "source_name": source_name,
                "start_char": start_char,
                "end_char": end_char
            }
        }

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count
        Rule of thumb: 1 token ≈ 4 characters for English
        """
        return max(1, len(text) // 4)

    def get_chunk_statistics(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about chunks"""
        if not chunks:
            return {
                "total_chunks": 0,
                "total_tokens": 0,
                "average_chunk_size": 0,
                "min_chunk_size": 0,
                "max_chunk_size": 0
            }

        chunk_sizes = [len(c["content"]) for c in chunks]
        total_tokens = sum(c["token_count"] for c in chunks)

        return {
            "total_chunks": len(chunks),
            "total_tokens": total_tokens,
            "average_chunk_size": sum(chunk_sizes) // len(chunk_sizes),
            "min_chunk_size": min(chunk_sizes),
            "max_chunk_size": max(chunk_sizes)
        }


# Global instance
chunking_service = ChunkingService(
    chunk_size=1000,
    chunk_overlap=200,
    min_chunk_size=100
)
