import pandas as pd
import zipfile
import re
import os
import numpy as np
from src.data_loader import load_epr_data
from src.analysis import analyze_spectrum, calculate_g_factor

# === STAŁE FIZYCZNE I PARAMETRY ===
PLANCK_H = 6.62607e-34  # [J*s]
BOHR_MB = 9.27401e-24  # [J/T]
T_G = 0.0010  # Tolerancja dla czynnika g
T_A = 0.05    # Tolerancja dla stałej sprzężenia [mT]


def load_database(zip_filename="spintrap_data (1).zip"):

    possible_paths = [zip_filename, os.path.join('data', zip_filename)]
    zip_path = None

    for path in possible_paths:
        if os.path.exists(path):
            zip_path = path
            break

    if not zip_path:
        print(f"\n[BŁĄD KRYTYCZNY] Nie znaleziono pliku '{zip_filename}'.")
        return None

    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            with z.open('stdb_main.csv') as f:
                df = pd.read_csv(f, encoding='utf-8')
                df['SPINTRAP'] = df['SPINTRAP'].astype(str).str.strip()
                df['RADICAL'] = df['RADICAL'].astype(str).str.strip()
                return df
    except Exception as e:
        print(f"\n[BŁĄD KRYTYCZNY] Błąd odczytu archiwum: {e}")
        return None


def extract_g_factor(comment_string):
    """Izoluje wartość czynnika g z tekstu przy pomocy wyrażeń regularnych."""
    match = re.search(r'(?:g\s*=\s*)?(2\.\d{3,})', str(comment_string))
    if match:
        return float(match.group(1))
    return None


def calculate_b_ref(g_ref, freq_ghz):
    """Zastosowanie wyprowadzonego wzoru na pole rezonansowe w mT."""
    freq_hz = freq_ghz * 1e9
    b_ref_tesla = (PLANCK_H * freq_hz) / (g_ref * BOHR_MB)
    return b_ref_tesla * 1000


def action_search(df):
    print("\n=== WYSZUKIWARKA PARAMETRÓW ===")
    query = input("Podaj szukaną frazę (np. DMPO, .OH, Fenton): ").strip().upper()
    try:
        freq_ghz = float(input("Podaj częstotliwość spektrometru [GHz] (np. 9.4): "))
    except ValueError:
        print("[BŁĄD] Niepoprawny format częstotliwości.")
        return

    mask = (
            df['SPINTRAP'].str.upper().str.contains(query, na=False) |
            df['RADICAL'].str.upper().str.contains(query, na=False) |
            df['STDB_COMMENT'].str.upper().str.contains(query, na=False)
    )

    results = df[mask]

    if results.empty:
        print(f"\n[!] Brak wyników dla frazy: '{query}'.")
        return

    print(f"\nZnaleziono {len(results)} dopasowań. (Wyświetlam max 5 pierwszych):")
    for index, row in results.head(5).iterrows():
        trap = row.get('SPINTRAP', 'Nieznana')
        radical = row.get('RADICAL', 'Nieznany')
        comment = str(row.get('STDB_COMMENT', ''))

        an_mt = float(row['AN']) * 0.1 if pd.notna(row['AN']) else None
        ah_mt = float(row['AH']) * 0.1 if pd.notna(row['AH']) else None
        g_ref = extract_g_factor(comment)

        print(f"\n> Układ: {trap} + {radical}")
        if an_mt: print(f"  - Stała AN: {an_mt:.2f} mT")
        if ah_mt: print(f"  - Stała AH: {ah_mt:.2f} mT")
        if g_ref:
            print(f"  - Czynnik g: {g_ref:.4f}")

            b_ref = calculate_b_ref(g_ref, freq_ghz)
            print(f"  - Oczekiwane pole sygnału: {b_ref:.2f} mT (dla {freq_ghz} GHz)")
        print(f"  - Komentarz: {comment}")


def action_verify(df):
    print("\n=== WERYFIKACJA WYNIKÓW EKSPERYMENTALNYCH ===")
    spintrap = input("Podaj nazwę pułapki (np. DMPO): ").strip()
    radical = input("Podaj nazwę rodnika (np. .OH): ").strip()

    match = df[(df['SPINTRAP'].str.upper() == spintrap.upper()) &
               (df['RADICAL'].str.upper() == radical.upper())]

    if match.empty:
        print(f"\n[!] Brak układu {spintrap}-{radical} w bazie referencyjnej.")
        return

    record = match.iloc[0]
    an_ref_mT = float(record['AN']) * 0.1 if pd.notna(record['AN']) else None
    ah_ref_mT = float(record['AH']) * 0.1 if pd.notna(record['AH']) else None
    g_ref = extract_g_factor(record['STDB_COMMENT'])

    try:
        exp_g = float(input(f"Podaj zmierzony czynnik g (oczekiwany ok. {g_ref if g_ref else 'brak danych'}): "))
        exp_an = float(input(f"Podaj zmierzoną stałą AN w mT (oczekiwana ok. {an_ref_mT:.2f}): "))
        exp_ah = float(input(f"Podaj zmierzoną stałą AH w mT (oczekiwana ok. {ah_ref_mT:.2f}): "))
    except ValueError:
        print("[BŁĄD] Wprowadzono niepoprawną wartość liczbową.")
        return

    print("\n--- RAPORT Z WERYFIKACJI ---")


    if g_ref:
        delta_g = abs(exp_g - g_ref)
        status = "[OK]" if delta_g <= T_G else "[BŁĄD]"
        print(f"{status} Czynnik g: Zmierzono {exp_g:.4f} | Wzorzec {g_ref:.4f} | Odchylenie: {delta_g:.4f}")

    if an_ref_mT:
        delta_an = abs(exp_an - an_ref_mT)
        status = "[OK]" if delta_an <= T_A else "[BŁĄD]"
        print(
            f"{status} Stała AN: Zmierzono {exp_an:.2f} mT | Wzorzec {an_ref_mT:.2f} mT | Odchylenie: {delta_an:.3f} mT")

    if ah_ref_mT:
        delta_ah = abs(exp_ah - ah_ref_mT)
        status = "[OK]" if delta_ah <= T_A else "[BŁĄD]"
        print(
            f"{status} Stała AH: Zmierzono {exp_ah:.2f} mT | Wzorzec {ah_ref_mT:.2f} mT | Odchylenie: {delta_ah:.3f} mT")


def action_batch_verify(df):
    print("\n=== WERYFIKACJA PLIKÓW Z FOLDERU 'data' ===")
    data_folder = 'data'
    if not os.path.exists(data_folder):
        print(f"[BŁĄD] Folder '{data_folder}' nie istnieje.")
        return

    spintrap = input("Podaj nazwę pułapki dla wszystkich plików (np. DMPO): ").strip()
    radical = input("Podaj nazwę rodnika dla wszystkich plików (np. .OH): ").strip()
    try:
        freq_ghz = float(input("Podaj częstotliwość spektrometru [GHz] dla wszystkich plików (np. 9.4): "))
    except ValueError:
        print("[BŁĄD] Niepoprawny format częstotliwości.")
        return

    match = df[(df['SPINTRAP'].str.upper() == spintrap.upper()) &
               (df['RADICAL'].str.upper() == radical.upper())]

    if match.empty:
        print(f"\n[!] Brak układu {spintrap}-{radical} w bazie referencyjnej. Nie można przeprowadzić weryfikacji.")
        return

    record = match.iloc[0]
    an_ref_mT = float(record['AN']) * 0.1 if pd.notna(record['AN']) else None
    ah_ref_mT = float(record['AH']) * 0.1 if pd.notna(record['AH']) else None
    g_ref = extract_g_factor(record['STDB_COMMENT'])

    print(f"\n--- Weryfikacja dla układu {spintrap}-{radical} (Ref: g={g_ref:.4f}, AN={an_ref_mT:.2f} mT, AH={ah_ref_mT:.2f} mT) ---")

    for filename in os.listdir(data_folder):
        if filename.endswith(('.txt', '.json')):
            file_path = os.path.join(data_folder, filename)
            print(f"\nAnaliza pliku: {filename}")

            try:
                b_field, y_values, accumulation_count, meta = load_epr_data(file_path)
                if b_field is None or y_values is None or len(b_field) == 0:
                    print(f"  [BŁĄD] Nie udało się wczytać danych z pliku {filename}.")
                    continue

                smoothing_points = meta.get('smoothing_points', 5)
                if smoothing_points % 2 == 0: smoothing_points += 1
                if smoothing_points < 3: smoothing_points = 3

                res = analyze_spectrum(b_field, y_values, accumulation_count, expected_lines=None, smoothing_points=smoothing_points)
                exp_g = calculate_g_factor(res['b_resonance'], freq_ghz)
                exp_an = res['coupling_a'] if res['line_count'] > 1 else None
                exp_ah = None
                exp_delta_b_pp = res['delta_b_pp']
                exp_amplitude_pp = res['amplitude_pp']
                exp_integral_intensity = res['integral_intensity']


                print(f"  - Czynnik g (zmierzony): {exp_g:.4f}")
                if g_ref:
                    delta_g = abs(exp_g - g_ref)
                    status = "[OK]" if delta_g <= T_G else "[BŁĄD]"
                    print(f"    {status} Odchylenie g: {delta_g:.4f} (Ref: {g_ref:.4f})")

                if exp_an is not None:
                    print(f"  - Stała AN (zmierzona): {exp_an:.2f} mT")
                    if an_ref_mT:
                        delta_an = abs(exp_an - an_ref_mT)
                        status = "[OK]" if delta_an <= T_A else "[BŁĄD]"
                        print(f"    {status} Odchylenie AN: {delta_an:.3f} mT (Ref: {an_ref_mT:.2f} mT)")
                elif an_ref_mT:
                    print(f"  - Stała AN (referencyjna): {an_ref_mT:.2f} mT (Brak zmierzonej dla singletu)")

                if exp_ah is not None:
                    print(f"  - Stała AH (zmierzona): {exp_ah:.2f} mT")
                    if ah_ref_mT:
                        delta_ah = abs(exp_ah - ah_ref_mT)
                        status = "[OK]" if delta_ah <= T_A else "[BŁĄD]"
                        print(f"    {status} Odchylenie AH: {delta_ah:.3f} mT (Ref: {ah_ref_mT:.2f} mT)")
                elif ah_ref_mT:
                    print(f"  - Stała AH (referencyjna): {ah_ref_mT:.2f} mT (Brak zmierzonej)")

                print(f"  - Szerokość linii (zmierzona): {exp_delta_b_pp:.4f} mT")
                print(f"  - Amplituda (zmierzona): {exp_amplitude_pp:.4f}")
                print(f"  - Intensywność integralna (zmierzona): {exp_integral_intensity:.4f}")


            except Exception as e:
                print(f"  [BŁĄD] Wystąpił błąd podczas analizy pliku {filename}: {e}")


def action_summary(df):
    print("\n=== PODSUMOWANIE BAZY DANYCH ===")
    traps_counts = df['SPINTRAP'].value_counts()
    print(f"Całkowita liczba rekordów: {len(df)}")
    print("\nTop 5 najpopularniejszych pułapek:")
    for trap, count in traps_counts.head(5).items():
        print(f"  - {trap:<10} ({count} wpisów)")


def action_list_spintrap_names(df):
    print("\n=== DOSTĘPNE PUŁAPKI SPINOWE ===")
    valid_traps = df['SPINTRAP'].dropna().astype(str)
    unique_traps = valid_traps.unique()
    unique_traps = unique_traps[(unique_traps != 'nan') & (unique_traps != '')]
    unique_traps = np.sort(unique_traps)

    if not unique_traps.size:
        print("[!] Brak pułapek spinowych w bazie danych.")
        return

    num_columns = 5
    max_len = max(len(trap) for trap in unique_traps) if unique_traps.size > 0 else 0

    col_width = max_len + 4

    for i in range(0, len(unique_traps), num_columns):
        row_items = unique_traps[i:i + num_columns]
        print("".join(f"{item:<{col_width}}" for item in row_items))

def main():
    print("Ładowanie bazy danych...")
    df = load_database()
    if df is None:
        return

    while True:
        print("\n=================================")
        print("   SPRAWDZANIE PARAMETRÓW EPR")
        print("=================================")
        print("1. Szukaj substancji i oblicz pole rezonansowe")
        print("2. Zweryfikuj parametry z eksperymentu (pojedynczy plik)")
        print("3. Zweryfikuj parametry z eksperymentu (batch z folderu 'data')")
        print("4. Pokaż statystyki bazy")
        print("5. Wyświetl listę pułapek spinowych")
        print("6. Wyjście")

        choice = input("Wybierz opcję (1-6): ").strip()

        if choice == '1':
            action_search(df)
        elif choice == '2':
            action_verify(df)
        elif choice == '3':
            action_batch_verify(df)
        elif choice == '4':
            action_summary(df)
        elif choice == '5':
            action_list_spintrap_names(df)
        elif choice == '6':
            print("Zamykanie programu. Do widzenia!")
            break
        else:
            print("Niepoprawny wybór, spróbuj ponownie.")


if __name__ == "__main__":
    main()