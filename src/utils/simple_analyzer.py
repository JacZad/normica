"""
Uproszczona wersja analizatora chunkingu bez matplotlib.
"""
import pandas as pd
from typing import List, Dict, Any, Tuple
from collections import Counter
import numpy as np
from langchain_core.documents import Document


class SimpleChunkingAnalyzer:
    """Uproszczony analizator jakości chunkingu bez wizualizacji."""
    
    def __init__(self, documents: List[Document]):
        self.documents = documents
        self.analysis_results = {}
    
    def analyze_chunk_distribution(self) -> Dict[str, Any]:
        """Analizuje rozkład długości chunków."""
        lengths = [len(doc.page_content) for doc in self.documents]
        
        stats = {
            "total_chunks": len(self.documents),
            "avg_length": np.mean(lengths),
            "median_length": np.median(lengths),
            "std_length": np.std(lengths),
            "min_length": min(lengths),
            "max_length": max(lengths),
            "length_distribution": lengths
        }
        
        self.analysis_results["distribution"] = stats
        return stats
    
    def analyze_chunk_types(self) -> Dict[str, Any]:
        """Analizuje typy chunków."""
        chunk_types = [doc.metadata.get("chunk_type", "unknown") for doc in self.documents]
        type_counts = Counter(chunk_types)
        
        stats = {
            "type_distribution": dict(type_counts),
            "total_types": len(type_counts),
            "most_common_type": type_counts.most_common(1)[0] if type_counts else None
        }
        
        self.analysis_results["types"] = stats
        return stats
    
    def analyze_section_coverage(self) -> Dict[str, Any]:
        """Analizuje pokrycie sekcji."""
        sections = [doc.metadata.get("section_number", "unknown") for doc in self.documents]
        section_counts = Counter(sections)
        
        stats = {
            "sections_covered": len([s for s in sections if s != "unknown"]),
            "section_distribution": dict(section_counts),
            "unknown_sections": section_counts.get("unknown", 0)
        }
        
        self.analysis_results["coverage"] = stats
        return stats
    
    def analyze_keyword_richness(self) -> Dict[str, Any]:
        """Analizuje bogactwo słów kluczowych."""
        all_keywords = []
        chunks_with_keywords = 0
        
        for doc in self.documents:
            keywords = doc.metadata.get("keywords", [])
            if keywords:
                chunks_with_keywords += 1
                all_keywords.extend(keywords)
        
        keyword_counts = Counter(all_keywords)
        
        stats = {
            "total_unique_keywords": len(keyword_counts),
            "avg_keywords_per_chunk": len(all_keywords) / len(self.documents) if self.documents else 0,
            "chunks_with_keywords": chunks_with_keywords,
            "keyword_coverage": chunks_with_keywords / len(self.documents) if self.documents else 0,
            "most_common_keywords": keyword_counts.most_common(10)
        }
        
        self.analysis_results["keywords"] = stats
        return stats
    
    def find_potential_improvements(self) -> List[Dict[str, Any]]:
        """Identyfikuje potencjalne ulepszenia."""
        improvements = []
        
        # Analiza długości chunków
        dist_stats = self.analysis_results.get("distribution", {})
        avg_length = dist_stats.get("avg_length", 0)
        
        if avg_length < 200:
            improvements.append({
                "type": "length",
                "issue": "Chunki są zbyt krótkie",
                "recommendation": "Zwiększ chunk_size lub ulepsz strategię łączenia",
                "current_avg": avg_length
            })
        elif avg_length > 1500:
            improvements.append({
                "type": "length", 
                "issue": "Chunki są zbyt długie",
                "recommendation": "Zmniejsz chunk_size lub ulepsz strategię dzielenia",
                "current_avg": avg_length
            })
        
        # Analiza pokrycia słów kluczowych
        keyword_stats = self.analysis_results.get("keywords", {})
        keyword_coverage = keyword_stats.get("keyword_coverage", 0)
        
        if keyword_coverage < 0.7:
            improvements.append({
                "type": "keywords",
                "issue": "Niska pokrycie słów kluczowych",
                "recommendation": "Ulepsz ekstrakcję słów kluczowych",
                "current_coverage": keyword_coverage
            })
        
        # Analiza typów chunków
        type_stats = self.analysis_results.get("types", {})
        unknown_ratio = type_stats.get("type_distribution", {}).get("unknown", 0) / len(self.documents) if self.documents else 0
        
        if unknown_ratio > 0.3:
            improvements.append({
                "type": "classification",
                "issue": "Wysokil odsetek niezklasyfikowanych chunków",
                "recommendation": "Ulepsz klasyfikację typów chunków", 
                "unknown_ratio": unknown_ratio
            })
        
        return improvements
    
    def generate_report(self) -> str:
        """Generuje raport z analizy."""
        # Uruchomienie wszystkich analiz
        self.analyze_chunk_distribution()
        self.analyze_chunk_types()
        self.analyze_section_coverage()
        self.analyze_keyword_richness()
        improvements = self.find_potential_improvements()
        
        report = "# 📊 Raport analizy chunkingu\n\n"
        
        # Statystyki podstawowe
        dist_stats = self.analysis_results["distribution"]
        report += f"## 📈 Statystyki podstawowe\n"
        report += f"- **Łączna liczba chunków:** {dist_stats['total_chunks']}\n"
        report += f"- **Średnia długość:** {dist_stats['avg_length']:.0f} znaków\n"
        report += f"- **Mediana długości:** {dist_stats['median_length']:.0f} znaków\n"
        report += f"- **Zakres długości:** {dist_stats['min_length']} - {dist_stats['max_length']} znaków\n\n"
        
        # Typy chunków
        type_stats = self.analysis_results["types"]
        report += f"## 🏷️ Typy chunków\n"
        for chunk_type, count in type_stats["type_distribution"].items():
            percentage = (count / dist_stats['total_chunks']) * 100
            report += f"- **{chunk_type}:** {count} ({percentage:.1f}%)\n"
        report += "\n"
        
        # Pokrycie sekcji
        coverage_stats = self.analysis_results["coverage"]
        report += f"## 📋 Pokrycie sekcji\n"
        report += f"- **Sekcje z identyfikatorem:** {coverage_stats['sections_covered']}\n"
        report += f"- **Sekcje nieznane:** {coverage_stats['unknown_sections']}\n\n"
        
        # Słowa kluczowe
        keyword_stats = self.analysis_results["keywords"]
        report += f"## 🔍 Słowa kluczowe\n"
        report += f"- **Unikalne słowa kluczowe:** {keyword_stats['total_unique_keywords']}\n"
        report += f"- **Pokrycie słów kluczowych:** {keyword_stats['keyword_coverage']:.1%}\n"
        report += f"- **Średnia słów kluczowych na chunk:** {keyword_stats['avg_keywords_per_chunk']:.1f}\n"
        
        if keyword_stats['most_common_keywords']:
            report += f"\n**Najczęstsze słowa kluczowe:**\n"
            for keyword, count in keyword_stats['most_common_keywords'][:5]:
                report += f"- {keyword}: {count}\n"
        
        # Rekomendacje
        if improvements:
            report += f"\n## 💡 Rekomendacje ulepszeń\n"
            for i, improvement in enumerate(improvements, 1):
                report += f"{i}. **{improvement['issue']}**\n"
                report += f"   - Rekomendacja: {improvement['recommendation']}\n\n"
        else:
            report += f"\n## ✅ Jakość chunkingu\nJakość chunkingu jest zadowalająca. Nie wykryto poważnych problemów.\n"
        
        return report


def simple_compare_chunking_strategies(
    text: str, 
    strategies: List[Tuple[str, Any]]
) -> pd.DataFrame:
    """
    Porównuje różne strategie chunkingu - uproszczona wersja.
    
    Args:
        text: Tekst do podzielenia
        strategies: Lista tupli (nazwa, chunker)
        
    Returns:
        pd.DataFrame: Porównanie strategii
    """
    results = []
    
    for name, chunker in strategies:
        try:
            if hasattr(chunker, 'chunk_document'):
                chunks = chunker.chunk_document(text)
                docs = [chunk.to_document() if hasattr(chunk, 'to_document') else chunk for chunk in chunks]
            else:
                docs = chunker.create_documents([text])
            
            analyzer = SimpleChunkingAnalyzer(docs)
            dist_stats = analyzer.analyze_chunk_distribution()
            type_stats = analyzer.analyze_chunk_types()
            keyword_stats = analyzer.analyze_keyword_richness()
            
            results.append({
                'Strategy': name,
                'Total Chunks': dist_stats['total_chunks'],
                'Avg Length': dist_stats['avg_length'],
                'Std Length': dist_stats['std_length'],
                'Unique Types': type_stats['total_types'],
                'Keyword Coverage': keyword_stats['keyword_coverage'],
                'Unique Keywords': keyword_stats['total_unique_keywords']
            })
            
        except Exception as e:
            print(f"Error with strategy {name}: {e}")
            results.append({
                'Strategy': name,
                'Total Chunks': 0,
                'Avg Length': 0,
                'Std Length': 0,
                'Unique Types': 0,
                'Keyword Coverage': 0,
                'Unique Keywords': 0
            })
    
    return pd.DataFrame(results)
