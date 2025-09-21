from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from openai import OpenAI
import os
import json
from typing import Dict, Any

# Definicja narzędzia dla obliczania wielkości czcionki
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

# Definicja narzędzia w formacie dla OpenAI
font_size_tool = {
    "type": "function",
    "function": {
        "name": "font_size_calculator",
        "description": "Oblicza zalecaną wysokość czcionki w milimetrach na podstawie odległości obserwacji w milimetrach.",
        "parameters": {
            "type": "object",
            "properties": {
                "distance": {
                    "type": "number",
                    "description": "Odległość obserwacji w milimetrach"
                }
            },
            "required": ["distance"]
        }
    }
}

def normica_chatbot():
    print("Inicjalizuję Normica Chatbota...")
    
    # Sprawdź, czy klucz API jest dostępny
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("UWAGA: Nie znaleziono klucza API OpenAI. Ustaw zmienną środowiskową OPENAI_API_KEY.")
        return
    
    # Utwórz klienta OpenAI
    client = OpenAI()
    
    # Komunikat systemowy
    system_prompt = """
    Jesteś asystentem eksperckim od normy EN 301 549 dotyczącej dostępności ICT (Information and Communication Technology).
    Odpowiadasz na pytania użytkowników, pomagasz interpretować wymagania normy i doradzasz w kwestiach dostępności.
    
    EN 301 549 to europejska norma dotycząca wymagań dostępności dla produktów i usług ICT. 
    Określa wymagania techniczne, które muszą być spełnione, aby produkty i usługi ICT były dostępne dla wszystkich.
    
    Kiedy użytkownik zapyta o wielkość czcionki dla określonej odległości, użyj funkcji font_size_calculator.
    Możesz także obliczać wielkość czcionki samodzielnie używając wzoru: wysokość x (mm) = odległość(mm) * 2.2 / 180
    
    Zawsze staraj się być pomocny i udzielać precyzyjnych informacji.
    """
    
    print("Witaj! Jestem Normica - chatbot specjalizujący się w normie EN 301 549 i dostępności ICT.")
    print("Możesz zadawać mi ogólne pytania lub zapytać o obliczenie wielkości czcionki.")
    print("Wpisz 'exit' aby zakończyć rozmowę.")
    
    # Historia konwersacji
    messages = [{"role": "system", "content": system_prompt}]
    
    while True:
        user_input = input("\nTy: ")
        if user_input.lower() == 'exit':
            print("Do zobaczenia!")
            break
        
        # Dodaj wiadomość użytkownika do historii
        messages.append({"role": "user", "content": user_input})
        
        try:
            # Wywołaj model z funkcjami
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=[font_size_tool],
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            
            # Dodaj odpowiedź asystenta do historii konwersacji
            messages.append(response_message.model_dump())
            
            # Sprawdź, czy model chce wywołać funkcję
            if response_message.tool_calls:
                # Model zdecydował się użyć funkcji
                for tool_call in response_message.tool_calls:
                    # Parsuj argumenty funkcji
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Znajdź i wywołaj odpowiednią funkcję
                    if function_name == "font_size_calculator":
                        tool_response = font_size_calculator(distance=function_args.get("distance"))
                        
                        # Dodaj wynik narzędzia do historii
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": tool_response
                        })
                        
                        # Uzyskaj odpowiedź modelu na podstawie wyniku narzędzia
                        second_response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=messages
                        )
                        
                        second_message = second_response.choices[0].message
                        messages.append(second_message.model_dump())
                        print(f"\nNormica: {second_message.content}")
                    else:
                        print(f"\nNormica: Nie znam funkcji {function_name}")
            else:
                # Model odpowiedział bez używania narzędzi
                print(f"\nNormica: {response_message.content}")
                
        except Exception as e:
            print(f"Wystąpił błąd: {e}")
            # Usuń ostatnią wiadomość użytkownika w przypadku błędu
            if messages and messages[-1]["role"] == "user":
                messages.pop()

if __name__ == "__main__":
    normica_chatbot()

