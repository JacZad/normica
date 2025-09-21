import streamlit as st
import os
import datetime
from typing import List, Dict, Any

# Import Langchain
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_openai_functions_agent
from langchain.agents import AgentExecutor

# Definicja narzędzia dla obliczania wielkości czcionki
@tool
def font_size_calculator(distance: float) -> str:
    """
    Oblicza zalecaną wysokość czcionki w milimetrach na podstawie odległości obserwacji w milimetrach.
    Wzór jest oparty o normę EN 301 549 dotyczącą dostępności ICT.
    
    Args:
        distance: Odległość obserwacji w milimetrach
    
    Returns:
        String opisujący zalecaną wielkość czcionki
    """
    if distance <= 0:
        return "Odległość musi być większa od zera."
    
    height = distance * 2.2 / 180
    return f"Dla odległości {distance} mm zalecana wysokość czcionki to {height:.2f} mm."

@tool
def get_current_date() -> str:
    """
    Zwraca aktualną datę w formacie YYYY-MM-DD.
    To narzędzie jest przydatne do uzyskania bieżącej daty,
    np. dla datowania raportów lub planowania wydarzeń.
    """
    return datetime.date.today().strftime('%Y-%m-%d')

# Klasa do zarządzania chatem z różnymi modelami
class NormicaChatbot:
    def __init__(self, model_name="gpt-4o", temperature=0):
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.tools = [font_size_calculator, get_current_date]
        self.system_prompt = """
        Jesteś asystentem eksperckim od normy EN 301 549 dotyczącej dostępności ICT (Information and Communication Technology).
        Odpowiadasz na pytania użytkowników, pomagasz interpretować wymagania normy i doradzasz w kwestiach dostępności.
        
        EN 301 549 to europejska norma dotycząca wymagań dostępności dla produktów i usług ICT. 
        Określa wymagania techniczne, które muszą być spełnione, aby produkty i usługi ICT były dostępne dla wszystkich.
        
        Kiedy użytkownik zapyta o wielkość czcionki dla określonej odległości, użyj funkcji font_size_calculator.
        Możesz także obliczać wielkość czcionki samodzielnie używając wzoru: wysokość x (mm) = odległość(mm) * 2.2 / 180
        
        Gdy użytkownik zapyta o aktualną datę, użyj funkcji get_current_date.
        
        Zawsze staraj się być pomocny i udzielać precyzyjnych informacji.
        """
        self._setup_agent()
        
    def _setup_agent(self):
        """Konfiguracja agenta LangChain z narzędziami"""
        # Tworzenie szablonu promptu
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            ("human", "{input}"),
            ("agent", "{agent_scratchpad}")
        ])
        
        # Tworzenie agenta z narzędziami
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=False,
            handle_parsing_errors=True
        )
    
    def process_message(self, messages: List[Dict[str, Any]], user_input: str) -> Dict[str, Any]:
        """Przetwarzanie wiadomości użytkownika i generowanie odpowiedzi"""
        try:
            # Przekształcenie historii wiadomości na tekst dla kontekstu
            context = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in messages[-10:] if msg['role'] != "system"
            ])
            
            # Wywołanie agenta z kontekstem i nowym pytaniem
            result = self.agent_executor.invoke({
                "input": f"Kontekst poprzedniej rozmowy:\n{context}\n\nAktualne pytanie: {user_input}"
            })
            
            return {"role": "assistant", "content": result["output"]}
        except Exception as e:
            return {"role": "assistant", "content": f"Przepraszam, wystąpił błąd: {str(e)}"}
            
    def change_model(self, model_name: str, temperature: float = 0):
        """Zmiana modelu językowego"""
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self._setup_agent()

# Konfiguracja strony Streamlit
st.set_page_config(
    page_title="Normica - Asystent dla normy EN 301 549",
    page_icon="📘",
    layout="centered"
)

# Wyświetlanie logo aplikacji
try:
    with open("normica_logo.svg", "r") as f:
        svg_content = f.read()
        st.image("normica_logo.svg", width=150)
except:
    # Fallback, gdyby nie znaleziono logo
    st.title("📘 Normica")

st.subheader("Asystent dla normy EN 301 549")

# Sprawdzenie klucza API
if not os.getenv("OPENAI_API_KEY"):
    st.warning("⚠️ Brak klucza API OpenAI. Ustaw zmienną środowiskową OPENAI_API_KEY.")
    st.stop()

# Inicjalizacja chatbota i historii w sesji
if "chatbot" not in st.session_state:
    st.session_state.chatbot = NormicaChatbot()
    
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": st.session_state.chatbot.system_prompt}
    ]

# Wyświetlanie historii chatbota
for message in st.session_state.messages:
    if message["role"] == "system":
        continue  # Nie wyświetlamy wiadomości systemowych
    elif message["role"] == "user":
        st.chat_message("user").write(message["content"])
    elif message["role"] == "assistant":
        if "content" in message and message["content"]:
            st.chat_message("assistant").write(message["content"])

# Panel boczny z informacjami
with st.sidebar:
    st.subheader("📝 O aplikacji")
    st.write("""
    Normica to inteligentny asystent chatbot specjalizujący się w normie EN 301 549 
    dotyczącej dostępności ICT (Information and Communication Technology).
    
    Wykorzystuje LangChain i model LLM do zapewnienia dokładnych i pomocnych odpowiedzi 
    na pytania dotyczące standardów dostępności.
    """)
    
    st.divider()
    
    # Opcje konfiguracji modelu
    st.subheader("⚙️ Konfiguracja")
    model_options = {
        "gpt-4o": "OpenAI GPT-4o",
        "gpt-4-turbo": "OpenAI GPT-4 Turbo",
        "gpt-3.5-turbo": "OpenAI GPT-3.5 Turbo"
    }
    
    selected_model = st.selectbox(
        "Model językowy:",
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x]
    )
    
    temperature = st.slider(
        "Temperatura (kreatywność):", 
        min_value=0.0, 
        max_value=1.0, 
        value=0.0, 
        step=0.1
    )
    
    if st.button("Zastosuj ustawienia"):
        st.session_state.chatbot.change_model(selected_model, temperature)
        st.success(f"Zmieniono model na {model_options[selected_model]}")
    
    st.divider()
    st.write("© 2025 Normica")

# Pole do wprowadzania tekstu
prompt = st.chat_input("Zadaj pytanie o normę EN 301 549...")

if prompt:
    # Dodaj wiadomość użytkownika do historii i interfejsu
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Pokaż spinner podczas generowania odpowiedzi
    with st.spinner("Normica myśli..."):
        # Użyj chatbota do wygenerowania odpowiedzi
        response = st.session_state.chatbot.process_message(
            st.session_state.messages,
            prompt
        )
        
        # Dodaj odpowiedź do historii
        st.session_state.messages.append(response)
        
        # Wyświetl odpowiedź
        st.chat_message("assistant").write(response["content"])
