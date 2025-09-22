"""
Zaawansowane strategie chunkingu dla dokumentów normatywnych.
"""
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from enum import Enum


class ChunkType(Enum):
    """Typy chunków w dokumencie normatywnym."""
    SECTION = "section"           # Główne sekcje (np. "1 Scope")
    SUBSECTION = "subsection"     # Podsekcje (np. "2.1 Normative references")
    REQUIREMENT = "requirement"   # Konkretne wymagania
    DEFINITION = "definition"     # Definicje
    EXAMPLE = "example"          # Przykłady
    NOTE = "note"                # Notatki
    TABLE = "table"              # Tabele
    LIST = "list"                # Listy


@dataclass
class EnhancedChunk:
    """Wzbogacony chunk z metadanymi."""
    content: str
    chunk_type: ChunkType
    section_number: Optional[str] = None
    section_title: Optional[str] = None
    parent_section: Optional[str] = None
    keywords: List[str] = None
    requirements_refs: List[str] = None
    
    def to_document(self) -> Document:
        """Konwertuje do Document z metadanymi."""
        metadata = {
            "chunk_type": self.chunk_type.value,
            "section_number": self.section_number,
            "section_title": self.section_title,
            "parent_section": self.parent_section,
            "keywords": self.keywords or [],
            "requirements_refs": self.requirements_refs or []
        }
        return Document(page_content=self.content, metadata=metadata)


class SmartNormChunker:
    """Inteligentny chunker dla dokumentów normatywnych."""
    
    def __init__(self):
        # Wzorce dla różnych elementów normy
        self.patterns = {
            'heading': re.compile(r'^#+\s*(\d[\d\.]*)\s+(.*)', re.MULTILINE),
        }
        
        # Słowa kluczowe dla różnych dziedzin
        self.domain_keywords = {
            'accessibility': ['accessibility', 'barrier', 'disability', 'impairment', 'accessible'],
            'audio': ['audio', 'sound', 'hearing', 'volume', 'frequency'],
            'visual': ['visual', 'display', 'color', 'contrast', 'brightness', 'font'],
            'keyboard': ['keyboard', 'navigation', 'shortcut', 'focus'],
            'mobile': ['mobile', 'touch', 'gesture', 'orientation'],
            'web': ['web', 'html', 'css', 'javascript', 'browser'],
            'testing': ['test', 'evaluation', 'procedure', 'conformance']
        }
    
    def chunk_document(self, text: str) -> List[EnhancedChunk]:
        """
        Dzieli dokument na inteligentne chunki.
        
        Args:
            text: Tekst dokumentu normy
            
        Returns:
            List[EnhancedChunk]: Lista wzbogaconych chunków
        """
        chunks = []
        last_end = 0

        for match in self.patterns['heading'].finditer(text):
            start, end = match.span()
            if last_end != 0:
                # Create a chunk for the content before the current heading
                content = text[last_end:start].strip()
                if content:
                    # This is content under the previous heading, so we need to find the previous heading's info
                    # This is a bit tricky, we will find the last heading before this content
                    prev_heading_match = list(self.patterns['heading'].finditer(text, 0, last_end))[-1]
                    section_number = prev_heading_match.group(1)
                    section_title = prev_heading_match.group(2)
                    chunk = EnhancedChunk(
                        content=content,
                        chunk_type=ChunkType.SECTION,
                        section_number=section_number,
                        section_title=section_title,
                        keywords=self._extract_keywords(content)
                    )
                    chunks.append(chunk)

            section_number = match.group(1)
            section_title = match.group(2)
            heading_content = match.group(0)

            chunk = EnhancedChunk(
                content=heading_content,
                chunk_type=ChunkType.SECTION,
                section_number=section_number,
                section_title=section_title,
                keywords=self._extract_keywords(heading_content)
            )
            chunks.append(chunk)
            last_end = end

        # Add the last chunk of the document
        content = text[last_end:].strip()
        if content:
            prev_heading_match = list(self.patterns['heading'].finditer(text, 0, last_end))[-1]
            section_number = prev_heading_match.group(1)
            section_title = prev_heading_match.group(2)
            chunk = EnhancedChunk(
                content=content,
                chunk_type=ChunkType.SECTION,
                section_number=section_number,
                section_title=section_title,
                keywords=self._extract_keywords(content)
            )
            chunks.append(chunk)

        return chunks
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Wyodrębnia słowa kluczowe z tekstu."""
        keywords = []
        text_lower = text.lower()
        
        for domain, domain_keywords in self.domain_keywords.items():
            for keyword in domain_keywords:
                if keyword in text_lower:
                    keywords.append(keyword)
        
        return list(set(keywords))
    
    def _merge_short_chunks(self, chunks: List[EnhancedChunk], min_length: int = 100) -> List[EnhancedChunk]:
        """Łączy zbyt krótkie chunki z sąsiednimi."""
        merged_chunks = []
        i = 0
        
        while i < len(chunks):
            current_chunk = chunks[i]
            
            # Jeśli chunk jest za krótki i nie jest to kluczowy typ
            if (len(current_chunk.content) < min_length and 
                current_chunk.chunk_type not in [ChunkType.REQUIREMENT, ChunkType.SECTION]):
                
                # Próba połączenia z następnym chunkiem
                if i + 1 < len(chunks) and chunks[i + 1].parent_section == current_chunk.parent_section:
                    next_chunk = chunks[i + 1]
                    merged_content = current_chunk.content + "\n\n" + next_chunk.content
                    
                    merged_chunk = EnhancedChunk(
                        content=merged_content,
                        chunk_type=current_chunk.chunk_type,
                        section_number=current_chunk.section_number,
                        section_title=current_chunk.section_title,
                        parent_section=current_chunk.parent_section,
                        keywords=list(set((current_chunk.keywords or []) + (next_chunk.keywords or []))),
                        requirements_refs=list(set((current_chunk.requirements_refs or []) + 
                                                 (next_chunk.requirements_refs or [])))
                    )
                    merged_chunks.append(merged_chunk)
                    i += 2  # Pomiń następny chunk, bo został połączony
                    continue
            
            merged_chunks.append(current_chunk)
            i += 1
        
        return merged_chunks
    
    def _add_cross_references(self, chunks: List[EnhancedChunk]) -> List[EnhancedChunk]:
        """Dodaje cross-referencje między chunkami."""
        # Budowanie mapy referencji
        section_map = {}
        for chunk in chunks:
            if chunk.section_number:
                section_map[chunk.section_number] = chunk.section_title
        
        # Dodawanie referencji do chunków
        for chunk in chunks:
            refs = []
            # Szukanie referencji do innych sekcji w treści
            for section_num in section_map.keys():
                if section_num in chunk.content and section_num != chunk.section_number:
                    refs.append(section_num)
            
            if refs:
                chunk.requirements_refs = list(set((chunk.requirements_refs or []) + refs))
        
        return chunks


class HybridChunker:
    """Hybrydowy chunker łączący różne strategie."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        self.smart_chunker = SmartNormChunker()
        self.fallback_chunker = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )
    
    def chunk_document(self, text: str) -> List[Document]:
        """
        Dzieli dokument używając hybrydowej strategii.
        
        Args:
            text: Tekst dokumentu
            
        Returns:
            List[Document]: Lista dokumentów z metadanymi
        """
        try:
            # Próba inteligentnego chunkingu
            smart_chunks = self.smart_chunker.chunk_document(text)
            documents = [chunk.to_document() for chunk in smart_chunks]
            
            # Sprawdzenie czy chunki nie są za duże
            oversized_docs = [doc for doc in documents if len(doc.page_content) > 2000]
            
            if oversized_docs:
                # Dodatkowe dzielenie dużych chunków
                additional_docs = []
                for doc in oversized_docs:
                    sub_docs = self.fallback_chunker.create_documents([doc.page_content])
                    for sub_doc in sub_docs:
                        sub_doc.metadata = doc.metadata.copy()
                        additional_docs.append(sub_doc)
                
                # Zastąpienie dużych chunków
                documents = [doc for doc in documents if len(doc.page_content) <= 2000]
                documents.extend(additional_docs)
            
            return documents
            
        except Exception as e:
            # Fallback do standardowego chunkingu
            print(f"Smart chunking failed: {e}. Using fallback chunker.")
            return self.fallback_chunker.create_documents([text])
