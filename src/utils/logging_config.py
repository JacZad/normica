"""
Logging setup for Normica application.
"""
import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO", 
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Konfiguracja logowania dla aplikacji.
    
    Args:
        level: Poziom logowania (DEBUG, INFO, WARNING, ERROR)
        log_file: Opcjonalna ścieżka do pliku logów
        
    Returns:
        logging.Logger: Skonfigurowany logger
    """
    # Konwersja poziomu logowania
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Format logów
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Konfiguracja głównego loggera
    logger = logging.getLogger('normica')
    logger.setLevel(numeric_level)
    
    # Usunięcie istniejących handlerów
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Handler do konsoli
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Opcjonalny handler do pliku
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
