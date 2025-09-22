"""
Refaktoryzowana aplikacja Streamlit dla Normica.
"""
import streamlit as st
import os
from typing import List, Dict, Any

# Import z naszej biblioteki
from src.config.settings import Config
from src.chatbot.normica_bot import NormicaChatbot


def setup_page_config():
    """Konfiguracja strony Streamlit."""
    st.set_page_config(
        page_title=Config.PAGE_TITLE,
        page_icon=Config.PAGE_ICON,
        layout="centered"
    )


def display_header():
    """Wyświetlenie nagłówka aplikacji."""
    if os.path.exists(Config.LOGO_SVG_PATH):
        st.image(Config.LOGO_SVG_PATH, width=150)
    else:
        st.title("📘 Normica")
    
    st.subheader("Asystent dla normy EN 301 549")


def validate_configuration():
    """Walidacja konfiguracji aplikacji."""
    errors = Config.validate()
    if errors:
        for error in errors:
            st.warning(f"⚠️ {error}")
        st.stop()


def initialize_session_state():
    """Inicjalizacja stanu sesji."""
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = NormicaChatbot()
        
    if "messages" not in st.session_state:
        st.session_state.messages = []


def display_chat_history():
    """Wyświetlenie historii konwersacji."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])


def create_sidebar():
    """Utworzenie panelu bocznego."""
    with st.sidebar:
        st.subheader("📝 O aplikacji")
        st.write("""
        Normica to inteligentny asystent specjalizujący się w normie EN 301 549. 
        Dzięki bazie wiedzy stworzonej z dokumentu normy, odpowiada na szczegółowe pytania dotyczące dostępności ICT.
        """)
        
        st.divider()
        
        # Konfiguracja modelu
        st.subheader("⚙️ Konfiguracja")
        
        selected_model = st.selectbox(
            "Model językowy:",
            options=list(Config.AVAILABLE_MODELS.keys()),
            format_func=lambda x: Config.AVAILABLE_MODELS[x],
            index=list(Config.AVAILABLE_MODELS.keys()).index(Config.DEFAULT_MODEL)
        )
        
        temperature = st.slider(
            "Temperatura (kreatywność):",
            min_value=0.0,
            max_value=1.0,
            value=Config.DEFAULT_TEMPERATURE,
            step=0.1
        )
        
        if st.button("Zastosuj ustawienia"):
            st.session_state.chatbot.change_model(selected_model, temperature)
            model_info = st.session_state.chatbot.get_model_info()
            st.success(f"Zmieniono model na {model_info['display_name']}")
        
        st.divider()
        
        # Informacje o aktualnym modelu
        if hasattr(st.session_state, 'chatbot'):
            model_info = st.session_state.chatbot.get_model_info()
            st.write(f"**Aktualny model:** {model_info['display_name']}")
            st.write(f"**Temperatura:** {model_info['temperature']}")
        
        st.divider()
        st.write("© 2025 Normica")


def handle_user_input():
    """Obsługa wprowadzania tekstu przez użytkownika."""
    if prompt := st.chat_input("Zadaj pytanie o normę EN 301 549..."):
        # Dodanie wiadomości użytkownika
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generowanie odpowiedzi
        with st.spinner("Normica analizuje normę..."):
            response = st.session_state.chatbot.process_message(
                st.session_state.messages, 
                prompt
            )
            
            st.session_state.messages.append(response)
            
            with st.chat_message("assistant"):
                st.write(response["content"])


def main():
    """Główna funkcja aplikacji."""
    # Konfiguracja strony
    setup_page_config()
    
    # Wyświetlenie nagłówka
    display_header()
    
    # Walidacja konfiguracji
    validate_configuration()
    
    # Inicjalizacja stanu sesji
    initialize_session_state()
    
    # Wyświetlenie historii konwersacji
    display_chat_history()
    
    # Panel boczny
    create_sidebar()
    
    # Obsługa wprowadzania tekstu
    handle_user_input()


if __name__ == "__main__":
    main()
