import re
from typing import List, Dict, Any
from langchain_core.documents import Document

def chunk_markdown_by_header(markdown_text: str) -> List[Document]:
    """Chunks markdown text based on headers H1-H4 using a custom implementation.

    Args:
        markdown_text: The markdown text to chunk.

    Returns:
        A list of Document objects, ready to be used with FAISS or other vector stores.
    """
    # Dodajmy trochę debugowania
    print(f"Długość tekstu wejściowego: {len(markdown_text)} znaków")
    
    # Sprawdźmy czy plik ma nagłówki
    headers_count = {
        "H1": markdown_text.count("# "),
        "H2": markdown_text.count("## "),
        "H3": markdown_text.count("### "),
        "H4": markdown_text.count("#### ")
    }
    print(f"Znalezione nagłówki: {headers_count}")
    
    # Własna implementacja podziału tekstu na chunki według nagłówków
    # Wzorzec regex dla nagłówków H1-H4
    header_pattern = r'^(#{1,4})\s+(.+)$'
    
    # Dzielimy tekst na linie
    lines = markdown_text.split('\n')
    chunks = []
    current_headers = {"H1": None, "H2": None, "H3": None, "H4": None}
    current_content = []
    current_header_level = None
    current_header_text = None
    
    for line in lines:
        # Sprawdzamy, czy linia zawiera nagłówek
        match = re.match(header_pattern, line)
        
        if match:
            # Jeśli mamy już zebrany jakiś content, zapisujemy go jako chunk
            if current_content and current_header_text:
                content = '\n'.join(current_content)
                # Tworzenie metadanych dla chunka
                metadata = {
                    "H1": current_headers["H1"],
                    "H2": current_headers["H2"],
                    "H3": current_headers["H3"],
                    "H4": current_headers["H4"],
                    "header_level": current_header_level,
                    "header_text": current_header_text
                }
                # Usuwamy None z metadanych
                metadata = {k: v for k, v in metadata.items() if v is not None}
                
                # Tworzymy dokument
                doc = Document(page_content=content, metadata=metadata)
                chunks.append(doc)
                current_content = []
            
            # Aktualizujemy nagłówek i poziom
            header_mark = match.group(1)
            header_text = match.group(2)
            header_level = len(header_mark)  # Liczba znaków #
            
            # Aktualizujemy informacje o bieżącym nagłówku
            level_name = f"H{header_level}"
            current_headers[level_name] = header_text
            
            # Resetujemy nagłówki niższych poziomów
            for i in range(header_level + 1, 5):
                current_headers[f"H{i}"] = None
                
            current_header_level = level_name
            current_header_text = header_text
            
            # Dodajemy nagłówek do aktualnej zawartości
            current_content.append(line)
        else:
            # Dodajemy linię do aktualnej zawartości
            current_content.append(line)
    
    # Dodajemy ostatni chunk, jeśli istnieje
    if current_content:
        content = '\n'.join(current_content)
        metadata = {
            "H1": current_headers["H1"],
            "H2": current_headers["H2"],
            "H3": current_headers["H3"],
            "H4": current_headers["H4"],
            "header_level": current_header_level,
            "header_text": current_header_text
        }
        # Usuwamy None z metadanych
        metadata = {k: v for k, v in metadata.items() if v is not None}
        
        doc = Document(page_content=content, metadata=metadata)
        chunks.append(doc)
    
    print(f"Utworzono {len(chunks)} chunków dokumentu")
    if chunks:
        print(f"Przykładowe metadane pierwszego chunka: {chunks[0].metadata}")
        
    return chunks
    return chunks
