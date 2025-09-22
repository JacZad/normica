## ✅ Lista narzędzi

- [x] `font_size_calculator` – obliczanie zalecanej wysokości czcionki na podstawie odległości obserwacji
- [x] `get_current_date` – zwracanie aktualnej daty


**Propozycje kolejnych narzędzi:**

- [ ] `norm_search` – wyszukiwanie konkretnych wymagań, definicji lub sekcji w treści normy EN 301 549
- [ ] `requirement_explainer` – wyjaśnianie i interpretacja wybranego wymagania normy
- [ ] `clause_comparator` – porównywanie wymagań pomiędzy różnymi wersjami normy lub z innymi standardami (np. WCAG)
- [ ] `norm_reference_generator` – generowanie cytatów i odwołań do konkretnych punktów normy
- [ ] `checklist_builder` – tworzenie listy kontrolnej na podstawie wybranych rozdziałów normy
- [ ] `report_template_creator` – generowanie szablonów raportów zgodnych z EN 301 549
- [ ] `faq_extractor` – automatyczne tworzenie FAQ na podstawie najczęściej zadawanych pytań o normę
- [ ] `norm_update_notifier` – informowanie o zmianach i nowych wersjach normy
- [ ] `term_glossary` – słownik pojęć używanych w normie EN 301 549
- [ ] `norm_application_examples` – generowanie praktycznych przykładów wdrożenia wymagań normy


# 📘 Normica

Normica to inteligentny asystent chatbot specjalizujący się w normie EN 301 549 dotyczącej dostępności ICT (Information and Communication Technology). Wykorzystuje modele LLM (np. GPT-4o) przez LangChain do zapewnienia dokładnych i pomocnych odpowiedzi na pytania dotyczące standardów dostępności.

![Normica](normica_logo.svg)

## 🌟 Funkcje

- **Kompleksowa wiedza o normie EN 301 549** – uzyskaj odpowiedzi na pytania dotyczące wymagań dostępności ICT
- **Obliczanie wielkości czcionki** – automatyczne obliczanie zalecanej wysokości czcionki na podstawie odległości obserwacji (narzędzie `font_size_calculator`)
- **Podawanie aktualnej daty** – narzędzie `get_current_date` dostępne dla użytkownika
- **Konwersacja w języku naturalnym** – zadawaj pytania w zwykłym języku polskim
- **Pamięć kontekstowa** – chatbot pamięta wcześniejsze części rozmowy
- **Interfejs webowy** – całość obsługiwana przez Streamlit
- **Panel konfiguracji** – wybór modelu LLM i temperatury w sidebar

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

```bash
streamlit run app.py
```

Po uruchomieniu interfejs webowy będzie dostępny pod adresem: `http://localhost:8501`

## 💬 Przykłady użycia

- "Co to jest norma EN 301 549?"
- "Jaka jest dzisiaj data?"
- "Jaka powinna być wielkość czcionki dla odległości 600 mm?"
- "Oblicz wysokość tekstu dla ekranu w odległości 800 mm."

## 🧮 Wzór na obliczanie wielkości czcionki

Normica używa następującego wzoru do obliczania zalecanej wysokości czcionki:

```math
wysokość x (mm) = odległość(mm) * 2.2 / 180
```

Gdzie:

- **wysokość x** to minimalna wysokość mdużej litery H w milimetrach
- **odległość** to typowa odległość obserwacji w milimetrach

## 🛠️ Rozszerzanie funkcjonalności

Aby dodać nowe narzędzia do chatbota:

1. Zdefiniuj nową funkcję z dekoratorem `@tool` w kodzie
2. Dodaj ją do listy `self.tools` w klasie `NormicaChatbot`
3. Zaktualizuj prompt systemowy (`self.system_prompt`), aby informował o nowej funkcjonalności

## 📄 Licencja

Ten projekt jest udostępniany na licencji MIT.
