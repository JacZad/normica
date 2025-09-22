"""
Testy konfiguracji aplikacji.
"""
import os
import tempfile
from unittest.mock import patch
from src.config.settings import Config


class TestConfig:
    """Testy dla konfiguracji aplikacji."""
    
    def test_available_models(self):
        """Test dostępnych modeli."""
        assert "gpt-4o" in Config.AVAILABLE_MODELS
        assert "gpt-4o-mini" in Config.AVAILABLE_MODELS
        assert len(Config.AVAILABLE_MODELS) >= 4
    
    def test_default_values(self):
        """Test wartości domyślnych."""
        assert Config.DEFAULT_MODEL == "gpt-4o-mini"
        assert Config.DEFAULT_TEMPERATURE == 0.0
        assert Config.CHUNK_SIZE == 1000
        assert Config.CHUNK_OVERLAP == 100
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    def test_validate_with_api_key(self):
        """Test walidacji z kluczem API."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test norm content")
            temp_norm_file = f.name
        
        original_path = Config.NORM_FILE_PATH
        Config.NORM_FILE_PATH = temp_norm_file
        
        try:
            errors = Config.validate()
            assert len(errors) == 0
        finally:
            Config.NORM_FILE_PATH = original_path
            os.unlink(temp_norm_file)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_validate_without_api_key(self):
        """Test walidacji bez klucza API."""
        # Resetowanie OPENAI_API_KEY w Config
        Config.OPENAI_API_KEY = None
        
        errors = Config.validate()
        assert any("OPENAI_API_KEY" in error for error in errors)
