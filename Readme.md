# EPR Spectrum Analysis / Analiza Widma EPR

Python application for analyzing Electron Paramagnetic Resonance EPR spectra.
Aplikacja w języku Python do analizy widm Elektronowego Rezonansu Paramagnetycznego EPR.

---

## [PL] Opis Projektu Głównego

Program `main.py` umożliwia obróbkę i analizę danych EPR w formatach JSON oraz TXT.

### Funkcje:
- **Automatyczna Analiza**: Wyznaczanie czynnika g, pola rezonansowego, amplitudy oraz intensywności integralnej.
- **Detekcja Multipletów**: Automatyczne rozpoznawanie struktury nadsubtelnej i obliczanie stałej sprzężenia A.

---

## [EN] Main Project Description

The `main.py` tool for EPR data processing and analysis, supporting JSON and TXT formats.

### Key Features:
- **Automated Analysis**: Calculation of g-factor, resonance field, amplitude, and integral intensity.
- **Multiplet Detection**: Automatic hyperfine structure recognition and calculation of coupling constant A.

---

## [PL] Moduł Weryfikacji Danych (`checking_epr_data.py`)

Ten moduł służy do weryfikacji eksperymentalnych parametrów EPR (czynnik g, stałe sprzężenia) z danymi referencyjnymi. Wykorzystuje bazę danych pułapek spinowych z NIEHS - National Institute of Environmental Health Sciences, dostępną pod adresem: [https://www.niehs.nih.gov/research/resources/databases/spintrap](https://www.niehs.nih.gov/research/resources/databases/spintrap).

### Funkcje:
- **Wyszukiwarka Parametrów**: Pozwala na wyszukiwanie substancji w bazie i obliczanie oczekiwanego pola rezonansowego.
- **Weryfikacja Pojedynczego Eksperymentu**: Porównanie zmierzonych parametrów z danymi referencyjnymi dla konkretnej pułapki i rodnika.
- **Weryfikacja Batchowa**: Automatyczna analiza i weryfikacja wielu plików danych z folderu `data` względem danych referencyjnych.
- **Lista Pułapek Spinowych**: Wyświetla wszystkie dostępne pułapki spinowe z bazy danych.

---

## [EN] Data Verification Module (`checking_epr_data.py`)

This module is used to verify experimental EPR parameters (g-factor, coupling constants) against reference data. It utilizes the spintrap database from NIEHS - National Institute of Environmental Health Sciences, available at: [https://www.niehs.nih.gov/research/resources/databases/spintrap](https://www.niehs.nih.gov/research/resources/databases/spintrap).

### Features:
- **Parameter Search**: Allows searching for substances in the database and calculating the expected resonance field.
- **Single Experiment Verification**: Comparison of measured parameters with reference data for a specific spintrap and radical.
- **Batch Verification**: Automatic analysis and verification of multiple data files from the `data` folder against reference data.
- **Spintrap List**: Displays all available spintraps from the database.

---

## [PL] Wymagania

*   Python 3.x
*   Biblioteki: `matplotlib`, `numpy`, `pandas`, `scipy`
    *   Możesz zainstalować je za pomocą: `pip install -r requirements.txt`

## [EN] Requirements

*   Python 3.x
*   Libraries: `matplotlib`, `numpy`, `pandas`, `scipy`
    *   You can install them using: `pip install -r requirements.txt`

---

## [PL] Użycie

### `main.py`
1.  Uruchom program z terminala w katalogu głównym projektu: `python main.py`
2.  Postępuj zgodnie z instrukcjami w konsoli, aby wybrać plik danych, wprowadzić parametry (częstotliwość, tytuł wykresu, nazwa pliku do zapisu).
3.  Wyniki analizy zostaną zapisane w raporcie tekstowym w folderze `results`, a wygenerowany wykres w folderze `plots`.

### `checking_epr_data.py`
1.  Uruchom program z terminala w katalogu głównym projektu: `python checking_epr_data.py`
2.  Wybierz opcję z menu, aby wyszukać, zweryfikować dane lub wyświetlić listę pułapek spinowych.

## [EN] Usage

### `main.py`
1.  Run the program from your project's root directory: `python main.py`
2.  Follow the console prompts to select a data file, enter parameters (frequency, plot title, save filename).
3.  Analysis results will be saved in a text report in the `results` folder, and the generated plot in the `plots` folder.

### `checking_epr_data.py`
1.  Run the program from your project's root directory: `python checking_epr_data.py`
2.  Select an option from the menu to search, verify data, or display the list of spintraps.
