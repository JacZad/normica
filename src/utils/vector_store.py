"""
Zarządzanie bazą wektorową FAISS.
"""
import os
import streamlit as st
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import MarkdownTextSplitter
from langchain_core.documents import Document
from typing import Optional

from ..config.settings import Config
from .advanced_chunking import HybridChunker


class VectorStoreManager:
    """Zarządza bazą wektorową FAISS."""
    
    def __init__(self, embeddings: Optional[OpenAIEmbeddings] = None):
        self.embeddings = embeddings or OpenAIEmbeddings()
        self.vector_store: Optional[FAISS] = None
    
    def get_or_create_vector_store(self) -> FAISS:
        """
        Wczytuje istniejącą bazę wektorową lub tworzy nową.
        
        Returns:
            FAISS: Baza wektorowa
        """
        if self.vector_store is not None:
            return self.vector_store
            
        if os.path.exists(Config.FAISS_INDEX_PATH):
            self.vector_store = self._load_existing_index()
        else:
            self.vector_store = self._create_new_index()
            
        return self.vector_store
    
    def _load_existing_index(self) -> FAISS:
        """Wczytuje istniejący indeks FAISS."""
        st.info("Wczytuję bazę wiedzy...")
        return FAISS.load_local(
            Config.FAISS_INDEX_PATH, 
            self.embeddings, 
            allow_dangerous_deserialization=True
        )
    
    def _create_new_index(self) -> FAISS:
        """Tworzy nowy indeks FAISS z dokumentu normy."""
        st.info("Tworzę nową bazę wiedzy z dokumentu normy. To może chwilę potrwać...")

        # Wczytanie dokumentu normy
        with open(Config.NORM_FILE_PATH, "r", encoding="utf-8") as f:
            norm_text = f.read()

        # Zaawansowany chunking
        # chunker = HybridChunker(
        #     chunk_size=Config.CHUNK_SIZE,
        #     chunk_overlap=Config.CHUNK_OVERLAP
        # )
        # docs = chunker.chunk_document(norm_text)
        from .advanced_chunking import chunk_markdown_by_header
        docs = chunk_markdown_by_header(norm_text)

        # Utworzenie bazy wektorowej
        vector_store = FAISS.from_documents(docs, self.embeddings)
        
        # Zapisanie indeksu
        vector_store.save_local(Config.FAISS_INDEX_PATH)
        st.success(f"Baza wiedzy została pomyślnie utworzona z {len(docs)} chunków.")
        
        return vector_store
    
    def get_retriever(self, **kwargs):
        """
        Zwraca retriever dla bazy wektorowej.
        
        Returns:
            VectorStoreRetriever: Retriever do wyszukiwania
        """
        vector_store = self.get_or_create_vector_store()
        return vector_store.as_retriever(
            search_kwargs={"k": kwargs.get("k", Config.RETRIEVAL_K)}
        )
