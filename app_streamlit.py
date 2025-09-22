import streamlit as st
import os
import datetime
from typing import List, Dict, Any

# Import Langchain
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import MarkdownTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_core.documents import Document

# --- Narzędzia ---
@tool
def font_size_calculator(distance: float) -> str:
    """
    Oblicza zalecaną wysokość czcionki w milimetrach na podstawie odległości obserwacji w milimetrach.
    Używaj tego narzędzia, gdy użytkownik pyta o wielkość czcionki, rozmiar tekstu lub podobne kwestie związane z odległością.
    """
    if distance <= 0:
        return "Odległość musi być większa od zera."
    height = distance * 2.2 / 180
    return f"Dla odległości {distance} mm zalecana wysokość czcionki to {height:.2f} mm."

@tool
def get_current_date() -> str:
    """
    Zwraca aktualną datę w formacie YYYY-MM-DD.
    Używaj, gdy użytkownik pyta o dzisiejszą datę.
    """
    return datetime.date.today().strftime('%Y-%m-%d')

# --- Klasa Chatbota ---
class NormicaChatbot:
    def __init__(self, model_name="gpt-4o", temperature=0):
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.vector_store = self._get_vector_store()
        self._setup_agent()

    def _get_vector_store(self):
        """Tworzy lub wczytuje bazę wektorową FAISS."""
        FAISS_INDEX_PATH = "faiss_index"
        if os.path.exists(FAISS_INDEX_PATH):
            st.info("Wczytuję bazę wiedzy...")
            return FAISS.load_local(FAISS_INDEX_PATH, OpenAIEmbeddings(), allow_dangerous_deserialization=True)
        
        st.info("Tworzę nową bazę wiedzy z dokumentu normy. To może chwilę potrwać...")
        with open("en301549.md", "r", encoding="utf-8") as f:
            norm_text = f.read()
        
        text_splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = [Document(page_content=x) for x in text_splitter.split_text(norm_text)]
        
        vector_store = FAISS.from_documents(docs, OpenAIEmbeddings())
        vector_store.save_local(FAISS_INDEX_PATH)
        st.success("Baza wiedzy została pomyślnie utworzona.")
        return vector_store

    def _setup_agent(self):
        """Konfiguracja agenta LangChain z narzędziami i RAG."""
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})

        # 1. Narzędzie do wyszukiwania w normie
        @tool
        def norm_search(query: str) -> List[Dict[str, Any]]:
            """
            Przeszukuje dokumentację normy EN 301 549 w poszukiwaniu odpowiedzi na pytanie użytkownika.
            Używaj tego narzędzia do odpowiadania na pytania dotyczące wymagań, definicji, klauzul i innych treści zawartych w normie.
            """
            docs = retriever.invoke(query)
            return [{"page_content": doc.page_content} for doc in docs]

        self.tools = [font_size_calculator, get_current_date, norm_search]
        
        # 2. Prompt systemowy dla agenta
        self.system_prompt = """
        Jesteś 'Normica', światowej klasy ekspertem od europejskiej normy EN 301 549 dotyczącej dostępności ICT.
        Twoim zadaniem jest odpowiadać na pytania użytkowników, bazując na dostarczonym kontekście z normy oraz używając dostępnych narzędzi.

        Dostępne narzędzia:
        - `font_size_calculator`: Użyj, gdy pytanie dotyczy obliczania wielkości czcionki.
        - `get_current_date`: Użyj, gdy pytanie dotyczy dzisiejszej daty.
        - `norm_search`: Użyj ZAWSZE, gdy pytanie dotyczy treści normy EN 301 549 (wymagań, definicji, procedur, itp.). To Twoje główne źródło wiedzy.

        Kroki postępowania:
        1. Przeanalizuj pytanie użytkownika.
        2. Jeśli pytanie dotyczy ogólnej wiedzy o świecie, odpowiedz bezpośrednio.
        3. Jeśli pytanie dotyczy daty lub wielkości czcionki, użyj odpowiedniego narzędzia.
        4. Jeśli pytanie dotyczy normy EN 301 549, ZAWSZE użyj narzędzia `norm_search`, aby znaleźć relevantne fragmenty.
        5. Na podstawie wyników z `norm_search`, sformułuj wyczerpującą i dokładną odpowiedź. Cytuj kluczowe informacje i, jeśli to możliwe, odnoś się do numerów klauzul.
        6. Jeśli `norm_search` nie zwróci wyników, poinformuj użytkownika, że nie możesz znaleźć odpowiedzi w dokumencie.
        
        Odpowiadaj po polsku. Bądź precyzyjny, pomocny i trzymaj się faktów z dokumentu.
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=False,
            handle_parsing_errors=True
        )

    def process_message(self, messages: List[Dict[str, Any]], user_input: str) -> Dict[str, Any]:
        """Przetwarzanie wiadomości użytkownika i generowanie odpowiedzi."""
        chat_history = [
            HumanMessage(content=msg["content"]) if msg["role"] == "user" else AIMessage(content=msg["content"])
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

    def change_model(self, model_name: str, temperature: float = 0):
        """Zmiana modelu językowego."""
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self._setup_agent()

# --- Konfiguracja i UI Streamlit ---
st.set_page_config(page_title="Normica - Asystent dla normy EN 301 549", page_icon="📘", layout="centered")

if os.path.exists("normica_logo.svg"):
    st.image("normica_logo.svg", width=150)
else:
    st.title("📘 Normica")

st.subheader("Asystent dla normy EN 301 549")

if not os.getenv("OPENAI_API_KEY"):
    st.warning("⚠️ Brak klucza API OpenAI. Ustaw zmienną środowiskową OPENAI_API_KEY.")
    st.stop()

# Inicjalizacja chatbota i historii
if "chatbot" not in st.session_state:
    st.session_state.chatbot = NormicaChatbot()
    
if "messages" not in st.session_state:
    st.session_state.messages = []

# Wyświetlanie historii
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Panel boczny
with st.sidebar:
    st.subheader("📝 O aplikacji")
    st.write("""
    Normica to inteligentny asystent specjalizujący się w normie EN 301 549. 
    Dzięki bazie wiedzy stworzonej z dokumentu normy, odpowiada na szczegółowe pytania dotyczące dostępności ICT.
    """)
    st.divider()
    st.subheader("⚙️ Konfiguracja")
    model_options = {
        "gpt-4o": "OpenAI GPT-4o",
        "gpt-4-turbo": "OpenAI GPT-4 Turbo",
        "gpt-3.5-turbo": "OpenAI GPT-3.5 Turbo"
    }
    selected_model = st.selectbox("Model językowy:", options=list(model_options.keys()), format_func=lambda x: model_options[x])
    temperature = st.slider("Temperatura (kreatywność):", min_value=0.0, max_value=1.0, value=0.0, step=0.1)
    
    if st.button("Zastosuj ustawienia"):
        st.session_state.chatbot.change_model(selected_model, temperature)
        st.success(f"Zmieniono model na {model_options[selected_model]}")
    
    st.divider()
    st.write("© 2025 Normica")

# Pole do wprowadzania tekstu
if prompt := st.chat_input("Zadaj pytanie o normę EN 301 549..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.spinner("Normica analizuje normę..."):
        response = st.session_state.chatbot.process_message(st.session_state.messages, prompt)
        st.session_state.messages.append(response)
        with st.chat_message("assistant"):
            st.write(response["content"])
