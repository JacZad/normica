"""
Konfiguracja aplikacji Normica.
"""
import os
from typing import Dict, List


class Config:
    """Konfiguracja aplikacji."""
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Modele dostępne w aplikacji
    AVAILABLE_MODELS: Dict[str, str] = {
        "gpt-4o": "OpenAI GPT-4o",
        "gpt-4o-mini": "OpenAI GPT-4o Mini", 
        "gpt-4-turbo": "OpenAI GPT-4 Turbo",
        "gpt-3.5-turbo": "OpenAI GPT-3.5 Turbo"
    }
    
    # Domyślne ustawienia
    DEFAULT_MODEL = "gpt-4o-mini"
    DEFAULT_TEMPERATURE = 0.0
    
    # Ścieżki plików
    NORM_FILE_PATH = "en301549.md"
    FAISS_INDEX_PATH = "faiss_index"
    LOGO_SVG_PATH = "normica_logo.svg"
    
    # Ustawienia RAG
    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 128
    RETRIEVAL_K = 5
    
    # Ustawienia Streamlit
    PAGE_TITLE = "Normica - Asystent dla normy EN 301 549"
    PAGE_ICON = "📘"
    
    @classmethod
    def validate(cls) -> List[str]:
        """
        Walidacja konfiguracji.
        
        Returns:
            List[str]: Lista błędów konfiguracji
        """
        errors = []
        
        if not cls.OPENAI_API_KEY:
            errors.append("Brak zmiennej środowiskowej OPENAI_API_KEY")
            
        if not os.path.exists(cls.NORM_FILE_PATH):
            errors.append(f"Nie znaleziono pliku normy: {cls.NORM_FILE_PATH}")
            
        return errors
