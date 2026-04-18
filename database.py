"""
Moduł bazy danych SQLite dla Income Tracker.
"""

import sqlite3
import datetime
from pathlib import Path

DB_PATH = Path.home() / ".finance_tracker" / "expenses.db"

# Cztery stałe kwartały w roku (każdy = 3 miesiące)
QUARTERS = {
    1: (1, 2, 3),
    2: (4, 5, 6),
    3: (7, 8, 9),
    4: (10, 11, 12),
}

def quarter_of_month(month: int) -> int:
    return (month - 1) // 3 + 1

def quarter_months(year: int, q: int):
    """Zwraca listę (year, month) dla danego kwartału."""
    return [(year, m) for m in QUARTERS[q]]

def current_quarter():
    today = datetime.date.today()
    return today.year, quarter_of_month(today.month)

def all_quarters_in_db_range(first_date: str, last_date: str):
    """Zwraca listę (year, q) od pierwszego do ostatniego kwartału w bazie."""
    if not first_date or not last_date:
        return []
    fy, fm = int(first_date[:4]), int(first_date[5:7])
    ly, lm = int(last_date[:4]), int(last_date[5:7])
    result = []
    y, q = fy, quarter_of_month(fm)
    ey, eq = ly, quarter_of_month(lm)
    while (y, q) <= (ey, eq):
        result.append((y, q))
        q += 1
        if q > 4:
            q = 1; y += 1
    return result


class Database:
    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                amount      REAL    NOT NULL,
                category    TEXT    NOT NULL DEFAULT 'Przychód',
                description TEXT,
                date        TEXT    NOT NULL,
                created_at  TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS settings (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            INSERT OR IGNORE INTO settings (key, value) VALUES ('quarterly_limit', '10800');
            INSERT OR IGNORE INTO settings (key, value) VALUES ('last_quarter', '');
        """)
        self.conn.commit()

    # ── Zapisy ───────────────────────────────────────────────────────────────

    def add_income(self, amount: float, description: str = "", date: str = None):
        if date is None:
            date = datetime.date.today().isoformat()
        self.conn.execute(
            "INSERT INTO expenses (amount, category, description, date, created_at) VALUES (?,?,?,?,?)",
            (amount, "Przychód", description, date, datetime.datetime.now().isoformat())
        )
        self.conn.commit()

    def delete_expense(self, expense_id: int):
        self.conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        self.conn.commit()

    # ── Odczyty miesięczne ───────────────────────────────────────────────────

    def get_monthly_total(self, year: int, month: int) -> float:
        prefix = f"{year}-{month:02d}"
        row = self.conn.execute(
            "SELECT COALESCE(SUM(amount),0) as t FROM expenses WHERE date LIKE ?",
            (f"{prefix}%",)
        ).fetchone()
        return row["t"]

    def get_expenses(self, year: int, month: int):
        prefix = f"{year}-{month:02d}"
        rows = self.conn.execute(
            "SELECT * FROM expenses WHERE date LIKE ? ORDER BY date DESC, created_at DESC",
            (f"{prefix}%",)
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Odczyty kwartalne ────────────────────────────────────────────────────

    def get_quarter_total(self, year: int, q: int) -> float:
        return sum(self.get_monthly_total(year, m) for m in QUARTERS[q])

    def get_quarter_entries(self, year: int, q: int):
        entries = []
        for m in QUARTERS[q]:
            entries.extend(self.get_expenses(year, m))
        entries.sort(key=lambda e: (e["date"], e["created_at"]), reverse=True)
        return entries

    # ── Suma całkowita (wszystkie lata) ──────────────────────────────────────

    def get_all_time_total(self) -> float:
        row = self.conn.execute(
            "SELECT COALESCE(SUM(amount),0) as t FROM expenses"
        ).fetchone()
        return row["t"]

    def get_all_quarters_summary(self):
        """Zwraca listę słowników {year, q, total, label} dla wszystkich kwartałów z danymi."""
        rows = self.conn.execute(
            "SELECT MIN(date) as first, MAX(date) as last FROM expenses"
        ).fetchone()
        if not rows["first"]:
            return []
        quarters = all_quarters_in_db_range(rows["first"], rows["last"])
        result = []
        for year, q in quarters:
            total = self.get_quarter_total(year, q)
            months = QUARTERS[q]
            result.append({
                "year": year, "q": q, "total": total,
                "label": f"Q{q} {year}  ({months[0]:02d}–{months[-1]:02d}.{year})",
                "months": months,
            })
        return result

    # ── Ustawienia ───────────────────────────────────────────────────────────

    def get_setting(self, key: str, default=None):
        row = self.conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default

    def set_setting(self, key: str, value: str):
        self.conn.execute("INSERT OR REPLACE INTO settings (key,value) VALUES (?,?)", (key, value))
        self.conn.commit()

    def get_quarterly_limit(self) -> float:
        return float(self.get_setting("quarterly_limit", "10800"))
