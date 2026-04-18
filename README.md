# 💰 Income Tracker — macOS Menu Bar App

A lightweight app for tracking quarterly income directly from the macOS menu bar. Built with Python and SQLite — all data stored locally on your machine.

## Features

- 🟢 **Menu bar indicator** — color-coded icon shows how much of your quarterly limit you've used
- ➕ **Quick income entry** — add amount and description in seconds
- 📋 **Current quarter view** — see all entries with running total
- 🕐 **Quarter history** — browse all previous quarters with per-entry details
- 💹 **All-time summary** — total earnings grouped by year and quarter, with average per quarter
- 🗑 **Delete last entry** — undo the most recent addition
- ⚠️ **Limit notifications** — alerts at 75%, 90%, and 100% of the quarterly limit
- 🔄 **Auto quarter reset** — automatically switches to the next quarter (Q1–Q4) with a notification
- 💾 **SQLite database** — stored locally at `~/.finance_tracker/expenses.db`

---

## Quarters

The year is divided into 4 fixed quarters:

| Quarter | Months |
|---------|--------|
| Q1 | January – March |
| Q2 | April – June |
| Q3 | July – September |
| Q4 | October – December |

The quarterly limit is **10,800 PLN**. The counter resets automatically at the start of each new quarter.

---

## Requirements

- macOS 10.14+
- Python 3.8+

---

## Installation

```bash
# 1. Clone or download the repository

# 2. Run the setup script (installs dependencies and launches the app)
chmod +x run.sh
./run.sh
```

The menu bar icon will appear as 🟢 with your current quarter total.

---

## Auto-start on Login

To launch the app automatically every time you log in:

```bash
# 1. Find your username
whoami

# 2. Find the path to the app folder
pwd

# 3. Edit com.financetracker.app.plist
#    Replace YOUR_USERNAME and /PATH/TO/FOLDER with the values above

# 4. Copy to LaunchAgents
cp com.financetracker.app.plist ~/Library/LaunchAgents/

# 5. Load the agent
launchctl load ~/Library/LaunchAgents/com.financetracker.app.plist
```

To disable auto-start:
```bash
launchctl unload ~/Library/LaunchAgents/com.financetracker.app.plist
```

---

## File Structure

```
income_tracker/
├── app.py                          # Main app — menu bar UI and logic
├── database.py                     # SQLite layer — read/write/query
├── requirements.txt                # Python dependencies (rumps)
├── run.sh                          # Setup and launch script
└── com.financetracker.app.plist    # LaunchAgent for auto-start
```

---

## Data

The SQLite database is stored at: `~/.finance_tracker/expenses.db`

You can open it with any SQLite viewer, e.g. [DB Browser for SQLite](https://sqlitebrowser.org/).

> **Note:** The database file is excluded from version control via `.gitignore` — your financial data never leaves your machine.
