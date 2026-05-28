# EPR Spectrum Analysis / Analiza Widma EPR

Python application for analyzing Electron Paramagnetic Resonance EPR spectra.
Aplikacja w języku Python do analizy widm Elektronowego Rezonansu Paramagnetycznego EPR.

---

## [PL] Opis 

Program umożliwia obróbkę i analizę danych EPR w formatach JSON oraz TXT.

### Funkcje:
- **Automatyczna Analiza**: Wyznaczanie czynnika g, pola rezonansowego, amplitudy oraz intensywności integralnej.
- **Detekcja Multipletów**: Automatyczne rozpoznawanie struktury nadsubtelnej i obliczanie stałej sprzężenia A.

---

## [EN] Project Description

Tool for EPR data processing and analysis, supporting JSON and TXT formats.

### Key Features:
- **Automated Analysis**: Calculation of g-factor, resonance field, amplitude, and integral intensity.
- **Multiplet Detection**: Automatic hyperfine structure recognition and calculation of coupling constant A.

---

## [PL] Wymagania

*   Python 3.x
*   Biblioteki: `numpy`, `scipy`, `matplotlib`

## [EN] Requirements

*   Python 3.x
*   Libraries: `numpy`, `scipy`, `matplotlib`

---

## [PL] Użycie

1.  Upewnij się, że masz zainstalowane wszystkie wymagane biblioteki (np. `pip install numpy scipy matplotlib`).
2.  Uruchom program z terminala w katalogu głównym projektu: `python main.py`
3.  Postępuj zgodnie z instrukcjami w konsoli, aby wybrać plik danych, wprowadzić parametry (częstotliwość, tytuł wykresu, nazwa pliku do zapisu).
4.  Wyniki analizy zostaną zapisane w raporcie tekstowym w folderze `results`, a wygenerowany wykres w folderze `plots`.

## [EN] Usage

1.  Ensure all required libraries are installed (e.g., `pip install numpy scipy matplotlib`).
2.  Run the program from your project's root directory: `python main.py`
3.  Follow the console prompts to select a data file, enter parameters (frequency, plot title, save filename).
4.  Analysis results will be saved in a text report in the `results` folder, and the generated plot in the `plots` folder.
