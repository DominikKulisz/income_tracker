# 💰 Finance Tracker – macOS Menu Bar App

Prosta aplikacja do śledzenia wydatków działająca jako nakładka w pasku menu macOS.

## Funkcje

- 🟢 **Wskaźnik w pasku menu** – zielony/żółty/pomarańczowy/czerwony w zależności od wykorzystania limitu
- ➕ **Szybkie dodawanie wydatków** – kwota, kategoria, opis, data
- 📋 **Historia** – przeglądaj i usuwaj wydatki miesiąc po miesiącu
- ⚠️ **Powiadomienia** – alert przy 75%, 90% i 100% limitu miesięcznego
- ⚙️ **Ustawienia** – zmiana limitu i dodawanie własnych kategorii
- 💾 **SQLite** – dane zapisywane lokalnie w `~/.finance_tracker/expenses.db`

---

## Instalacja

### Wymagania
- macOS 10.14+
- Python 3.8+

### Kroki

```bash
# 1. Sklonuj lub pobierz folder finance_tracker

# 2. Uruchom skrypt instalacyjny (zainstaluje zależności i odpali aplikację)
chmod +x run.sh
./run.sh
```

Po uruchomieniu w pasku menu pojawi się ikona 🟢 z aktualną sumą wydatków.

---

## Autostart przy logowaniu

Aby aplikacja uruchamiała się automatycznie:

```bash
# 1. Znajdź swoją nazwę użytkownika
whoami

# 2. Znajdź ścieżkę do folderu
pwd   # w folderze finance_tracker

# 3. Edytuj plik com.financetracker.app.plist
#    Zastąp TWOJA_NAZWA_UZYTKOWNIKA i /SCIEZKA/DO/FOLDERU

# 4. Skopiuj do LaunchAgents
cp com.financetracker.app.plist ~/Library/LaunchAgents/

# 5. Wczytaj agenta
launchctl load ~/Library/LaunchAgents/com.financetracker.app.plist
```

Aby wyłączyć autostart:
```bash
launchctl unload ~/Library/LaunchAgents/com.financetracker.app.plist
```

---

## Struktura plików

```
finance_tracker/
├── app.py              # Główna aplikacja (menu bar)
├── database.py         # Baza danych SQLite
├── ui_windows.py       # Okna UI (Tkinter)
├── requirements.txt    # Zależności Python
├── run.sh              # Skrypt uruchomienia
└── com.financetracker.app.plist  # LaunchAgent (autostart)
```

---

## Kategorie domyślne

Jedzenie · Transport · Mieszkanie · Rozrywka · Zdrowie · Ubrania · Elektronika · Inne

Możesz dodawać własne kategorie w **Ustawienia**.

---

## Dane

Baza SQLite przechowywana w: `~/.finance_tracker/expenses.db`

Możesz ją otworzyć dowolnym narzędziem SQLite (np. [DB Browser for SQLite](https://sqlitebrowser.org/)).
