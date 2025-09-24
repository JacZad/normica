"""
Narzędzia dla chatbota Normica.
"""
import datetime
from typing import List, Dict, Any
from langchain_core.tools import tool


@tool
def font_size_calculator(distance: float) -> str:
    """
    Oblicza zalecaną wysokość czcionki w milimetrach na podstawie odległości obserwacji w milimetrach.
    Używaj tego narzędzia, gdy użytkownik pyta o wielkość czcionki, rozmiar tekstu lub podobne kwestie związane z odległością.
    
    Args:
        distance: Odległość obserwacji w milimetrach
        
    Returns:
        str: Zalecana wysokość czcionki w mm
    """
    if distance <= 0:
        return "Odległość musi być większa od zera."
    
    # Wzór: wysokość x (mm) = odległość(mm) * 2.2 / 180
    height = distance * 2.2 / 180
    return f"Dla odległości {distance} mm zalecana wysokość czcionki to {height:.2f} mm."


@tool
def get_current_date() -> str:
    """
    Zwraca aktualną datę w formacie YYYY-MM-DD.
    Używaj, gdy użytkownik pyta o dzisiejszą datę.
    
    Returns:
        str: Aktualna data w formacie YYYY-MM-DD
    """
    return datetime.date.today().strftime('%Y-%m-%d')


def create_norm_search_tool(retriever):
    """
    Tworzy narzędzie do wyszukiwania w normie EN 301 549.
    
    Args:
        retriever: Retriever z bazy wektorowej
        
    Returns:
        tool: Narzędzie do wyszukiwania w normie
    """
    @tool
    def norm_search(query: str) -> List[Dict[str, Any]]:
        """
        Przeszukuje dokumentację normy EN 301 549 w poszukiwaniu odpowiedzi na pytanie użytkownika.
        Używaj tego narzędzia do odpowiadania na pytania dotyczące wymagań, definicji, klauzul i innych treści zawartych w normie.
        
        Args:
            query: Zapytanie do wyszukania w normie
            
        Returns:
            List[Dict]: Lista znalezionych fragmentów dokumentu
        """
        docs = retriever.invoke(query)
        return [{"page_content": doc.page_content} for doc in docs]
    
    return norm_search