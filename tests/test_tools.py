"""
Testy jednostkowe dla narzędzi chatbota.
"""
import pytest
from datetime import date
from src.chatbot.tools import font_size_calculator, get_current_date


class TestFontSizeCalculator:
    """Testy dla kalkulatora wielkości czcionki."""
    
    def test_valid_distance(self):
        """Test dla prawidłowej odległości."""
        result = font_size_calculator.func(100)
        expected = "Dla odległości 100 mm zalecana wysokość czcionki to 1.22 mm."
        assert result == expected
    
    def test_zero_distance(self):
        """Test dla odległości zero."""
        result = font_size_calculator.func(0)
        assert result == "Odległość musi być większa od zera."
    
    def test_negative_distance(self):
        """Test dla ujemnej odległości."""
        result = font_size_calculator.func(-50)
        assert result == "Odległość musi być większa od zera."
    
    def test_calculation_formula(self):
        """Test poprawności wzoru matematycznego."""
        distance = 180
        result = font_size_calculator.func(distance)
        # 180 * 2.2 / 180 = 2.2
        expected = "Dla odległości 180 mm zalecana wysokość czcionki to 2.20 mm."
        assert result == expected


class TestGetCurrentDate:
    """Testy dla funkcji pobierania daty."""
    
    def test_date_format(self):
        """Test formatu zwracanej daty."""
        result = get_current_date.func()
        today = date.today().strftime('%Y-%m-%d')
        assert result == today
    
    def test_date_pattern(self):
        """Test czy data ma prawidłowy format YYYY-MM-DD."""
        result = get_current_date.func()
        assert len(result) == 10
        assert result[4] == '-'
        assert result[7] == '-'
