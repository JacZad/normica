# 📘 Normica

Normica to inteligentny asystent chatbot specjalizujący się w normie EN 301 549 dotyczącej dostępności ICT (Information and Communication Technology). Wykorzystuje model GPT-4o do zapewnienia dokładnych i pomocnych odpowiedzi na pytania dotyczące standardów dostępności.

![Normica Logo](normica_logo.svg)

## 🌟 Funkcje

- **Kompleksowa wiedza o normie EN 301 549** - uzyskaj odpowiedzi na pytania dotyczące wymagań dostępności ICT
- **Kalkulator wielkości czcionki** - automatyczne obliczanie zalecanej wysokości czcionki na podstawie odległości obserwacji
- **Konwersacja w języku naturalnym** - zadawaj pytania w zwykłym języku polskim
- **Pamięć kontekstowa** - chatbot pamięta wcześniejsze części rozmowy
- **Interfejs graficzny** - wersja webowa oparta o Streamlit lub wersja konsolowa do wyboru

![Interfejs Streamlit](docs/streamlit_preview.png)

## 🚀 Rozpoczęcie pracy

### Wymagania wstępne

- Python 3.8+
- Klucz API OpenAI (ustaw jako zmienną środowiskową `OPENAI_API_KEY`)

### Instalacja

1. Sklonuj repozytorium lub utwórz nowy projekt
2. Zainstaluj wymagane pakiety:

```bash
pip install -r requirements.txt
```

3. Ustaw klucz API OpenAI jako zmienną środowiskową:

```bash
# W PowerShell:
$env:OPENAI_API_KEY="twój-klucz-api"

# W CMD:
set OPENAI_API_KEY=twój-klucz-api
```

### Uruchomienie

#### Wersja konsolowa

```bash
python app.py
```

#### Interfejs webowy (Streamlit)

```bash
streamlit run app_streamlit.py
```

Po uruchomieniu interfejs webowy będzie dostępny pod adresem: `http://localhost:8501`

## 💬 Przykłady użycia

- "Co to jest norma EN 301 549?"
- "Jakie są wymagania dostępności dla aplikacji mobilnych?"
- "Jaka powinna być wielkość czcionki dla odległości 600 mm?"
- "Czy możesz obliczyć wysokość tekstu dla ekranu w odległości 800 mm?"

## 🧮 Wzór na obliczanie wielkości czcionki

Normica używa następującego wzoru do obliczania zalecanej wysokości czcionki:

```math
wysokość x (mm) = odległość(mm) * 2.2 / 180
```

Gdzie:

- **wysokość x** to minimalna wysokość małej litery x w milimetrach
- **odległość** to typowa odległość obserwacji w milimetrach

## 🛠️ Rozszerzanie funkcjonalności

Aby dodać nowe narzędzia do chatbota:

1. Zdefiniuj nową funkcję w kodzie
2. Dodaj ją do listy narzędzi w formacie OpenAI
3. Zaktualizuj prompt systemowy, aby informował o nowej funkcjonalności

## 📄 Licencja

Ten projekt jest udostępniany na licencji MIT.
