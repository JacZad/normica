"""
Główna klasa chatbota Normica.
"""
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_openai_functions_agent, AgentExecutor
import streamlit as st

from ..config.settings import Config
from ..utils.vector_store import VectorStoreManager
from .tools import font_size_calculator, get_current_date, create_norm_search_tool


class NormicaChatbot:
    """Główna klasa chatbota Normica."""
    
    def __init__(self, model_name: str = Config.DEFAULT_MODEL, temperature: float = Config.DEFAULT_TEMPERATURE):
        self.model_name = model_name
        self.temperature = temperature
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        
        # Inicjalizacja bazy wektorowej
        self.vector_store_manager = VectorStoreManager()
        
        # Konfiguracja agenta
        self._setup_agent()
    
    def _setup_agent(self):
        """Konfiguracja agenta LangChain z narzędziami i RAG."""
        # Pobranie retrievera
        retriever = self.vector_store_manager.get_retriever()
        
        # Utworzenie narzędzi
        norm_search_tool = create_norm_search_tool(retriever)
        self.tools = [font_size_calculator, get_current_date, norm_search_tool]
        
        # Prompt systemowy
        system_prompt = self._get_system_prompt()
        
        # Utworzenie prompta
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Utworzenie agenta
        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=False,
            handle_parsing_errors=True
        )
    
    def _get_system_prompt(self) -> str:
        """Zwraca prompt systemowy dla agenta."""
        return """
        Jesteś 'Normica', światowej klasy ekspertem od europejskiej normy EN 301 549 dotyczącej dostępności ICT.
        Twoim zadaniem jest odpowiadać na pytania użytkowników, bazując na dostarczonym kontekście z normy oraz używając dostępnych narzędzi.

        Dostępne narzędzia:
        - `font_size_calculator`: Użyj, gdy pytanie dotyczy obliczania wielkości czcionki.
        - `get_current_date`: Użyj, gdy pytanie dotyczy dzisiejszej daty.
        - `norm_search`: Użyj ZAWSZE, gdy pytanie dotyczy treści normy EN 301 549 (wymagań, definicji, procedur, itp.). To Twoje główne źródło wiedzy.

        Kroki postępowania:
        1. Przeanalizuj pytanie użytkownika.
        2. Jeśli pytanie dotyczy ogólnej wiedzy o świecie, odpowiedz że nie znasz się na tym.
        3. Jeśli pytanie dotyczy daty lub wielkości czcionki, użyj odpowiedniego narzędzia.
        4. Jeśli pytanie dotyczy normy EN 301 549, ZAWSZE użyj narzędzia `norm_search`, aby znaleźć relevantne fragmenty.
        5. Na podstawie wyników z `norm_search`, sformułuj wyczerpującą i dokładną odpowiedź. Cytuj kluczowe informacje i, jeśli to możliwe, odnoś się do numerów klauzul.
        6. Jeśli `norm_search` nie zwróci wyników, poinformuj użytkownika, że nie możesz znaleźć odpowiedzi w dokumencie.
        
        Odpowiadaj po polsku. Bądź precyzyjny, pomocny i trzymaj się faktów z dokumentu.
        """
    
    def process_message(self, messages: List[Dict[str, Any]], user_input: str) -> Dict[str, Any]:
        """
        Przetwarzanie wiadomości użytkownika i generowanie odpowiedzi.
        
        Args:
            messages: Historia wiadomości
            user_input: Wiadomość użytkownika
            
        Returns:
            Dict: Odpowiedź asystenta
        """
        # Konwersja historii na format LangChain
        chat_history = [
            HumanMessage(content=msg["content"]) if msg["role"] == "user" 
            else AIMessage(content=msg["content"])
            for msg in messages if msg["role"] in ["user", "assistant"]
        ]
        
        try:
            result = self.agent_executor.invoke({
                "input": user_input,
                "chat_history": chat_history
            })
            return {"role": "assistant", "content": result["output"]}
        except Exception as e:
            st.error(f"Wystąpił błąd agenta: {e}")
            return {"role": "assistant", "content": f"Przepraszam, wystąpił błąd: {str(e)}"}
    
    def change_model(self, model_name: str, temperature: float = None):
        """
        Zmiana modelu językowego.
        
        Args:
            model_name: Nazwa modelu
            temperature: Temperatura modelu (opcjonalne)
        """
        self.model_name = model_name
        if temperature is not None:
            self.temperature = temperature
            
        self.llm = ChatOpenAI(model_name=model_name, temperature=self.temperature)
        self._setup_agent()
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Zwraca informacje o aktualnym modelu.
        
        Returns:
            Dict: Informacje o modelu
        """
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "display_name": Config.AVAILABLE_MODELS.get(self.model_name, self.model_name)
        }
