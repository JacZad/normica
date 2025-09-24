"""
Utils module for Normica - zawiera główne komponenty przetwarzania dokumentów.
"""

# Główne komponenty używane przez aplikację
from .advanced_chunking import HybridChunker, EnhancedChunk, ChunkType, chunk_markdown_by_header
from .vector_store import VectorStoreManager

# Opcjonalne narzędzia do analizy i optymalizacji (nie używane przez główną aplikację)
# from .chunking_analyzer import ChunkingAnalyzer 
# from .chunking_optimizer import ChunkingOptimizer

__all__ = [
    "MarkdownChunker",
    "HybridChunker", 
    "EnhancedChunk",
    "ChunkType",
    "chunk_markdown_by_header",
    "VectorStoreManager"
]
