"""
Zaawansowane narzędzia wyszukiwania wykorzystujące metadane chunków.
"""
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from langchain_core.vectorstores import VectorStoreRetriever


def create_advanced_search_tools(retriever: VectorStoreRetriever):
    """
    Tworzy zaawansowane narzędzia wyszukiwania wykorzystujące metadane.
    
    Args:
        retriever: Retriever z bazy wektorowej
        
    Returns:
        List: Lista zaawansowanych narzędzi
    """
    
    @tool
    def norm_search(query: str) -> List[Dict[str, Any]]:
        """
        Przeszukuje dokumentację normy EN 301 549 w poszukiwaniu odpowiedzi na pytanie użytkownika.
        Używaj tego narzędzia do odpowiadania na pytania dotyczące wymagań, definicji, klauzul i innych treści zawartych w normie.
        
        Args:
            query: Zapytanie do wyszukania w normie
            
        Returns:
            List[Dict]: Lista znalezionych fragmentów dokumentu z metadanymi
        """
        docs = retriever.invoke(query)
        results = []
        
        for doc in docs:
            result = {
                "page_content": doc.page_content,
                "metadata": doc.metadata
            }
            results.append(result)
        
        return results
    
    @tool
    def search_requirements(query: str) -> List[Dict[str, Any]]:
        """
        Wyszukuje konkretne wymagania w normie EN 301 549.
        Używaj gdy użytkownik pyta o konkretne wymagania dostępności.
        
        Args:
            query: Zapytanie dotyczące wymagań
            
        Returns:
            List[Dict]: Lista znalezionych wymagań
        """
        # Wyszukiwanie z filtrem na typ chunka "requirement"
        docs = retriever.invoke(query)
        requirements = []
        
        for doc in docs:
            if doc.metadata.get("chunk_type") == "requirement":
                requirements.append({
                    "requirement_number": doc.metadata.get("section_number"),
                    "requirement_title": doc.metadata.get("section_title"),
                    "content": doc.page_content,
                    "parent_section": doc.metadata.get("parent_section"),
                    "keywords": doc.metadata.get("keywords", [])
                })
        
        return requirements
    
    @tool
    def search_by_section(section_number: str) -> List[Dict[str, Any]]:
        """
        Wyszukuje informacje z konkretnej sekcji normy.
        Używaj gdy użytkownik pyta o konkretną sekcję (np. "sekcja 4", "punkt 5.2").
        
        Args:
            section_number: Numer sekcji (np. "4", "5.2", "6.1.1")
            
        Returns:
            List[Dict]: Lista fragmentów z danej sekcji
        """
        # Wyszukiwanie po numerze sekcji
        docs = retriever.invoke(f"section {section_number}")
        results = []
        
        for doc in docs:
            doc_section = doc.metadata.get("section_number", "")
            if doc_section.startswith(section_number):
                results.append({
                    "section_number": doc_section,
                    "section_title": doc.metadata.get("section_title"),
                    "content": doc.page_content,
                    "chunk_type": doc.metadata.get("chunk_type"),
                    "keywords": doc.metadata.get("keywords", [])
                })
        
        return results
    
    @tool
    def search_definitions(term: str) -> List[Dict[str, Any]]:
        """
        Wyszukuje definicje pojęć w normie EN 301 549.
        Używaj gdy użytkownik pyta o definicję lub znaczenie pojęcia.
        
        Args:
            term: Pojęcie do zdefiniowania
            
        Returns:
            List[Dict]: Lista znalezionych definicji
        """
        docs = retriever.invoke(f"definition {term}")
        definitions = []
        
        for doc in docs:
            if (doc.metadata.get("chunk_type") == "definition" or 
                "definition" in doc.page_content.lower()):
                definitions.append({
                    "term": term,
                    "definition": doc.page_content,
                    "section": doc.metadata.get("parent_section"),
                    "keywords": doc.metadata.get("keywords", [])
                })
        
        return definitions
    
    @tool
    def search_by_keywords(keywords: str) -> List[Dict[str, Any]]:
        """
        Wyszukuje fragmenty normy zawierające określone słowa kluczowe.
        Używaj gdy chcesz znaleźć wszystkie fragmenty dotyczące konkretnej dziedziny.
        
        Args:
            keywords: Słowa kluczowe oddzielone spacjami
            
        Returns:
            List[Dict]: Lista fragmentów zawierających słowa kluczowe
        """
        keyword_list = keywords.lower().split()
        docs = retriever.invoke(keywords)
        results = []
        
        for doc in docs:
            doc_keywords = [kw.lower() for kw in doc.metadata.get("keywords", [])]
            
            # Sprawdzenie czy chunk zawiera któreś ze słów kluczowych
            if any(kw in doc_keywords for kw in keyword_list):
                results.append({
                    "content": doc.page_content,
                    "section": doc.metadata.get("parent_section"),
                    "matching_keywords": [kw for kw in doc_keywords if kw in keyword_list],
                    "all_keywords": doc_keywords,
                    "chunk_type": doc.metadata.get("chunk_type")
                })
        
        return results
    
    return [
        norm_search,
        search_requirements, 
        search_by_section,
        search_definitions,
        search_by_keywords
    ]
