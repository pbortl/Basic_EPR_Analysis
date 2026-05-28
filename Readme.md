# EPR Spectrum Analysis / Analiza Widma EPR

Python application for analyzing Electron Paramagnetic Resonance (EPR) spectra.
Aplikacja w języku Python do analizy widm Elektronowego Rezonansu Paramagnetycznego.

---

## [PL] Opis Projektu
Program umożliwia profesjonalną obróbkę i analizę danych EPR w formatach JSON oraz TXT.

### Główne funkcje:
- **Wielojęzyczność**: Obsługa języka polskiego i angielskiego.
- **Automatyczna Analiza**: Wyznaczanie czynnika g, pola rezonansowego oraz intensywności integralnej.
- **Detekcja Multipletów**: Automatyczne rozpoznawanie struktury nadsubtelnej i obliczanie stałej sprzężenia A.
- **Profesjonalne Raporty**: Automatyczne generowanie wykresów PNG oraz raportów tekstowych w folderze `results/`.
- **Modułowa Architektura**: Kod podzielony na logiczne części (Analysis, Loading, Visualization).

### Instalacja i Uruchomienie:
1. Zainstaluj wymagane biblioteki:
   ```bash
   pip install -r requirements.txt
   ```
2. Uruchom program:
   ```bash
   python main.py
   ```
3. Pliki z danymi umieszczaj w folderze `data/`.

---

## [EN] Project Description
A professional tool for EPR data processing and analysis, supporting JSON and TXT formats.

### Key Features:
- **Multi-language Support**: Full English and Polish localization.
- **Automated Analysis**: Calculation of g-factor, resonance field, and integral intensity.
- **Multiplet Detection**: Automatic hyperfine structure recognition and calculation of coupling constant A.
- **Professional Outputs**: Generates high-quality PNG plots and text reports in the `results/` folder.
- **Modular Architecture**: Clean code separated into logical modules (Analysis, Loading, Visualization).

### Installation and Usage:
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python main.py
   ```
3. Place your raw data files in the `data/` folder.

---

## Project Structure / Struktura Projektu:
- `main.py`: Entry point / Punkt wejścia.
- `src/`: Source code / Kod źródłowy (modules).
- `config/`: Configuration & translations / Konfiguracja i tłumaczenia.
- `data/`: Raw data input / Surowe dane.
- `results/`: Output plots and reports / Wyniki i raporty.
- `requirements.txt`: List of dependencies / Lista bibliotek.
