"""
Opcjonalna implementacja z ChromaDB jako alternatywa dla FAISS.
"""
import os
import streamlit as st
from typing import Optional
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from ..config.settings import Config
from .advanced_chunking import HybridChunker


class ChromaVectorStoreManager:
    """Zarządca bazy wektorowej ChromaDB (alternatywa dla FAISS)."""
    
    def __init__(self, embeddings: Optional[OpenAIEmbeddings] = None):
        self.embeddings = embeddings or OpenAIEmbeddings()
        self.vector_store: Optional[Chroma] = None
        self.persist_directory = "chroma_db"
    
    def get_or_create_vector_store(self) -> Chroma:
        """
        Wczytuje istniejącą bazę ChromaDB lub tworzy nową.
        
        Returns:
            Chroma: Baza wektorowa
        """
        if self.vector_store is not None:
            return self.vector_store
            
        if os.path.exists(self.persist_directory):
            self.vector_store = self._load_existing_index()
        else:
            self.vector_store = self._create_new_index()
            
        return self.vector_store
    
    def _load_existing_index(self) -> Chroma:
        """Wczytuje istniejący indeks ChromaDB."""
        st.info("Wczytuję bazę wiedzy ChromaDB...")
        return Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )
    
    def _create_new_index(self) -> Chroma:
        """Tworzy nowy indeks ChromaDB z dokumentu normy."""
        st.info("Tworzę nową bazę wiedzy ChromaDB z dokumentu normy...")
        
        # Wczytanie dokumentu normy
        with open(Config.NORM_FILE_PATH, "r", encoding="utf-8") as f:
            norm_text = f.read()
        
        # Zaawansowany chunking
        chunker = HybridChunker(
            chunk_size=Config.CHUNK_SIZE, 
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        docs = chunker.chunk_document(norm_text)
        
        # Utworzenie bazy ChromaDB
        vector_store = Chroma.from_documents(
            docs, 
            self.embeddings,
            persist_directory=self.persist_directory
        )
        
        # Zapisanie
        vector_store.persist()
        st.success(f"Baza wiedzy ChromaDB została pomyślnie utworzona z {len(docs)} chunków.")
        
        return vector_store
    
    def get_retriever(self, **kwargs):
        """
        Zwraca retriever dla bazy wektorowej.
        
        Returns:
            VectorStoreRetriever: Retriever do wyszukiwania
        """
        vector_store = self.get_or_create_vector_store()
        
        # ChromaDB obsługuje zaawansowane filtrowanie
        search_kwargs = {
            "k": kwargs.get("k", Config.RETRIEVAL_K)
        }
        
        # Opcjonalne filtrowanie po metadanych
        if "filter" in kwargs:
            search_kwargs["filter"] = kwargs["filter"]
            
        return vector_store.as_retriever(search_kwargs=search_kwargs)
    
    def search_by_metadata(self, query: str, metadata_filter: dict = None):
        """
        Wyszukiwanie z filtrowaniem po metadanych (zaleta ChromaDB).
        
        Args:
            query: Zapytanie tekstowe
            metadata_filter: Filtr metadanych, np. {"chunk_type": "requirement"}
            
        Returns:
            List[Document]: Znalezione dokumenty
        """
        vector_store = self.get_or_create_vector_store()
        
        if metadata_filter:
            return vector_store.similarity_search(
                query, 
                k=Config.RETRIEVAL_K,
                filter=metadata_filter
            )
        else:
            return vector_store.similarity_search(query, k=Config.RETRIEVAL_K)


# Przykład użycia z filtrowaniem:
def demo_chroma_advanced_search():
    """Demo zaawansowanego wyszukiwania z ChromaDB."""
    manager = ChromaVectorStoreManager()
    
    # Wyszukiwanie tylko wymagań (requirements)
    requirements = manager.search_by_metadata(
        "audio description", 
        metadata_filter={"chunk_type": "requirement"}
    )
    
    # Wyszukiwanie tylko w sekcji 4
    section4_docs = manager.search_by_metadata(
        "accessibility", 
        metadata_filter={"section_number": "4"}
    )
    
    return requirements, section4_docs
