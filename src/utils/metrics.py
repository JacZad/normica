"""
Metryki i monitoring dla aplikacji Normica.
"""
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ConversationMetrics:
    """Metryki konwersacji."""
    user_id: str
    session_id: str
    start_time: datetime = field(default_factory=datetime.now)
    total_messages: int = 0
    total_response_time: float = 0.0
    tools_used: Dict[str, int] = field(default_factory=dict)
    errors_count: int = 0
    
    def add_message(self, response_time: float, tools_used: list = None, error: bool = False):
        """Dodaje metryki dla nowej wiadomości."""
        self.total_messages += 1
        self.total_response_time += response_time
        
        if tools_used:
            for tool in tools_used:
                self.tools_used[tool] = self.tools_used.get(tool, 0) + 1
        
        if error:
            self.errors_count += 1
    
    def get_average_response_time(self) -> float:
        """Zwraca średni czas odpowiedzi."""
        if self.total_messages == 0:
            return 0.0
        return self.total_response_time / self.total_messages
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje metryki do słownika."""
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "total_messages": self.total_messages,
            "average_response_time": self.get_average_response_time(),
            "tools_used": self.tools_used,
            "errors_count": self.errors_count,
            "session_duration": (datetime.now() - self.start_time).total_seconds()
        }


class MetricsCollector:
    """Kolektor metryk aplikacji."""
    
    def __init__(self):
        self.conversations: Dict[str, ConversationMetrics] = {}
    
    def start_conversation(self, user_id: str, session_id: str) -> ConversationMetrics:
        """Rozpoczyna nową konwersację."""
        metrics = ConversationMetrics(user_id=user_id, session_id=session_id)
        self.conversations[session_id] = metrics
        return metrics
    
    def get_conversation(self, session_id: str) -> Optional[ConversationMetrics]:
        """Pobiera metryki konwersacji."""
        return self.conversations.get(session_id)
    
    def record_message(
        self, 
        session_id: str, 
        response_time: float, 
        tools_used: list = None, 
        error: bool = False
    ):
        """Rejestruje metryki wiadomości."""
        if session_id in self.conversations:
            self.conversations[session_id].add_message(
                response_time=response_time,
                tools_used=tools_used,
                error=error
            )
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Zwraca globalne statystyki."""
        if not self.conversations:
            return {"total_conversations": 0}
        
        total_messages = sum(conv.total_messages for conv in self.conversations.values())
        total_response_time = sum(conv.total_response_time for conv in self.conversations.values())
        total_errors = sum(conv.errors_count for conv in self.conversations.values())
        
        all_tools = {}
        for conv in self.conversations.values():
            for tool, count in conv.tools_used.items():
                all_tools[tool] = all_tools.get(tool, 0) + count
        
        return {
            "total_conversations": len(self.conversations),
            "total_messages": total_messages,
            "average_response_time": total_response_time / total_messages if total_messages > 0 else 0,
            "total_errors": total_errors,
            "error_rate": total_errors / total_messages if total_messages > 0 else 0,
            "most_used_tools": sorted(all_tools.items(), key=lambda x: x[1], reverse=True)
        }
