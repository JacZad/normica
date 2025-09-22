"""
Uproszczony optymalizator parametrów chunkingu.
"""
import itertools
from typing import Dict, List, Tuple, Any
import numpy as np
from dataclasses import dataclass

from .advanced_chunking import HybridChunker
from .simple_analyzer import SimpleChunkingAnalyzer


@dataclass
class ChunkingParams:
    """Parametry chunkingu do optymalizacji."""
    chunk_size: int
    chunk_overlap: int
    score: float = 0.0
    metrics: Dict[str, Any] = None


class SimpleChunkingOptimizer:
    """Uproszczony optymalizator parametrów chunkingu."""
    
    def __init__(self, text: str):
        self.text = text
        self.results = []
    
    def optimize_parameters(
        self,
        chunk_sizes: List[int] = [500, 750, 1000, 1250, 1500],
        overlap_ratios: List[float] = [0.05, 0.1, 0.15, 0.2],
        scoring_weights: Dict[str, float] = None
    ) -> ChunkingParams:
        """
        Optymalizuje parametry chunkingu.
        
        Args:
            chunk_sizes: Lista rozmiarów chunków do testowania
            overlap_ratios: Lista współczynników overlap (jako % chunk_size)
            scoring_weights: Wagi dla różnych metryk w funkcji celu
            
        Returns:
            ChunkingParams: Najlepsze parametry
        """
        if scoring_weights is None:
            scoring_weights = {
                'avg_length_score': 0.25,      # Preferujemy średnią długość ~800-1200
                'consistency_score': 0.20,     # Niska wariancja długości
                'keyword_coverage': 0.25,      # Wysokie pokrycie słów kluczowych
                'type_diversity': 0.15,        # Różnorodność typów chunków
                'section_coverage': 0.15       # Pokrycie sekcji
            }
        
        best_params = None
        best_score = -1
        
        print(f"🔍 Optymalizacja parametrów chunkingu...")
        print(f"Testowanie {len(chunk_sizes)} × {len(overlap_ratios)} = {len(chunk_sizes) * len(overlap_ratios)} kombinacji")
        
        for i, (chunk_size, overlap_ratio) in enumerate(itertools.product(chunk_sizes, overlap_ratios)):
            overlap = int(chunk_size * overlap_ratio)
            
            try:
                # Testowanie parametrów
                chunker = HybridChunker(chunk_size=chunk_size, chunk_overlap=overlap)
                docs = chunker.chunk_document(self.text)
                
                # Analiza wyników
                analyzer = SimpleChunkingAnalyzer(docs)
                dist_stats = analyzer.analyze_chunk_distribution()
                type_stats = analyzer.analyze_chunk_types()
                keyword_stats = analyzer.analyze_keyword_richness()
                coverage_stats = analyzer.analyze_section_coverage()
                
                # Obliczenie score
                score = self._calculate_score(
                    dist_stats, type_stats, keyword_stats, coverage_stats, scoring_weights
                )
                
                params = ChunkingParams(
                    chunk_size=chunk_size,
                    chunk_overlap=overlap,
                    score=score,
                    metrics={
                        'distribution': dist_stats,
                        'types': type_stats,
                        'keywords': keyword_stats,
                        'coverage': coverage_stats
                    }
                )
                
                self.results.append(params)
                
                if score > best_score:
                    best_score = score
                    best_params = params
                
                print(f"  {i+1:2d}. chunk_size={chunk_size}, overlap={overlap} → score={score:.3f}")
                
            except Exception as e:
                print(f"  {i+1:2d}. chunk_size={chunk_size}, overlap={overlap} → ERROR: {e}")
        
        print(f"\n🏆 Najlepsze parametry:")
        print(f"   chunk_size={best_params.chunk_size}")
        print(f"   chunk_overlap={best_params.chunk_overlap}")
        print(f"   score={best_params.score:.3f}")
        
        return best_params
    
    def _calculate_score(
        self,
        dist_stats: Dict,
        type_stats: Dict, 
        keyword_stats: Dict,
        coverage_stats: Dict,
        weights: Dict[str, float]
    ) -> float:
        """Oblicza łączny score dla parametrów."""
        
        # 1. Score dla średniej długości (optymalna: 800-1200)
        avg_length = dist_stats['avg_length']
        if 800 <= avg_length <= 1200:
            avg_length_score = 1.0
        elif 600 <= avg_length <= 1500:
            avg_length_score = 0.8
        elif 400 <= avg_length <= 1800:
            avg_length_score = 0.6
        else:
            avg_length_score = 0.3
        
        # 2. Score dla konsystencji (niska wariancja)
        std_length = dist_stats['std_length']
        cv = std_length / avg_length if avg_length > 0 else 1
        consistency_score = max(0, 1 - cv)  # Niższy CV = wyższy score
        
        # 3. Score dla pokrycia słów kluczowych
        keyword_coverage = keyword_stats['keyword_coverage']
        
        # 4. Score dla różnorodności typów
        total_types = type_stats['total_types']
        type_diversity = min(1.0, total_types / 6)  # Maksymalnie 6 typów
        
        # 5. Score dla pokrycia sekcji
        total_chunks = dist_stats['total_chunks']
        sections_covered = coverage_stats['sections_covered']
        section_coverage = (sections_covered / total_chunks) if total_chunks > 0 else 0
        
        # Obliczenie łącznego score
        total_score = (
            weights['avg_length_score'] * avg_length_score +
            weights['consistency_score'] * consistency_score +
            weights['keyword_coverage'] * keyword_coverage +
            weights['type_diversity'] * type_diversity +
            weights['section_coverage'] * section_coverage
        )
        
        return total_score
    
    def get_optimization_report(self) -> str:
        """Generuje raport z optymalizacji."""
        if not self.results:
            return "Brak wyników optymalizacji."
        
        best = max(self.results, key=lambda x: x.score)
        worst = min(self.results, key=lambda x: x.score)
        
        report = "# 🎯 Raport optymalizacji chunkingu\n\n"
        
        report += f"## 🏆 Najlepsze parametry\n"
        report += f"- **Chunk size:** {best.chunk_size}\n"
        report += f"- **Chunk overlap:** {best.chunk_overlap}\n"
        report += f"- **Score:** {best.score:.3f}\n\n"
        
        if best.metrics:
            dist = best.metrics['distribution']
            keywords = best.metrics['keywords']
            report += f"### Metryki najlepszego rozwiązania:\n"
            report += f"- **Łączna liczba chunków:** {dist['total_chunks']}\n"
            report += f"- **Średnia długość:** {dist['avg_length']:.0f} znaków\n"
            report += f"- **Odchylenie standardowe:** {dist['std_length']:.0f}\n"
            report += f"- **Pokrycie słów kluczowych:** {keywords['keyword_coverage']:.1%}\n\n"
        
        report += f"## 📉 Najgorsze parametry\n"
        report += f"- **Chunk size:** {worst.chunk_size}\n" 
        report += f"- **Chunk overlap:** {worst.chunk_overlap}\n"
        report += f"- **Score:** {worst.score:.3f}\n\n"
        
        # Analiza trendów
        report += f"## 📊 Analiza trendów\n"
        
        # Grupowanie wyników po chunk_size
        size_groups = {}
        for result in self.results:
            size = result.chunk_size
            if size not in size_groups:
                size_groups[size] = []
            size_groups[size].append(result.score)
        
        report += f"### Wpływ chunk_size na score:\n"
        for size in sorted(size_groups.keys()):
            avg_score = np.mean(size_groups[size])
            report += f"- **{size}:** {avg_score:.3f} (avg)\n"
        
        return report
    
    def get_top_configurations(self, n: int = 5) -> List[ChunkingParams]:
        """Zwraca top N konfiguracji."""
        return sorted(self.results, key=lambda x: x.score, reverse=True)[:n]
