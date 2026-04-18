#!/usr/bin/env python3
"""
Income Tracker - macOS Menu Bar App
4 kwartały rocznie · historia poprzednich · suma całkowita
"""

import rumps
import datetime
from database import Database, current_quarter, quarter_months, QUARTERS


class IncomeTrackerApp(rumps.App):
    def __init__(self):
        self.db = Database()
        self._check_quarter_reset()

        super().__init__(
            name="IncomeTracker",
            title=self._get_title(),
            quit_button=None
        )

        # ── Info (tylko odczyt) ───────────────────────────────────────────────
        self.mi_qlabel   = rumps.MenuItem("", callback=None)
        self.mi_received = rumps.MenuItem("", callback=None)
        self.mi_remain   = rumps.MenuItem("", callback=None)
        self.mi_bar      = rumps.MenuItem("", callback=None)
        self.mi_alltime  = rumps.MenuItem("", callback=None)

        # ── Akcje ─────────────────────────────────────────────────────────────
        self.mi_add      = rumps.MenuItem("➕  Dodaj przychód",       callback=self.add_income)
        self.mi_history  = rumps.MenuItem("📋  Ten kwartał",           callback=self.show_current)
        self.mi_prev     = rumps.MenuItem("🕐  Poprzednie kwartały",   callback=self.show_all_quarters)
        self.mi_total    = rumps.MenuItem("💹  Suma całkowita",        callback=self.show_total)
        self.mi_delete   = rumps.MenuItem("🗑   Usuń ostatni wpis",    callback=self.delete_last)
        self.mi_quit     = rumps.MenuItem("✖️   Zamknij",               callback=self._quit)

        self.menu = [
            self.mi_qlabel,
            self.mi_received,
            self.mi_remain,
            self.mi_bar,
            self.mi_alltime,
            None,
            self.mi_add,
            self.mi_history,
            self.mi_prev,
            self.mi_total,
            self.mi_delete,
            None,
            self.mi_quit,
        ]

        self._refresh_display()

    # ── Reset kwartalny ───────────────────────────────────────────────────────

    def _check_quarter_reset(self):
        today = datetime.date.today()
        cy, cq = current_quarter()
        key = f"{cy}-Q{cq}"
        last = self.db.get_setting("last_quarter")
        if last != key:
            self.db.set_setting("last_quarter", key)
            if last and last != "":
                limit = self.db.get_quarterly_limit()
                rumps.notification(
                    "🔄 Nowy kwartał!",
                    "Income Tracker",
                    f"Rozpoczął się Q{cq} {cy}. Limit: {limit:,.0f} zł"
                )

    # ── Pomocnicze ────────────────────────────────────────────────────────────

    def _get_title(self):
        cy, cq = current_quarter()
        total   = self.db.get_quarter_total(cy, cq)
        limit   = self.db.get_quarterly_limit()
        percent = total / limit * 100 if limit else 0
        icon = "🔴" if percent >= 100 else "🟠" if percent >= 80 else "🟡" if percent >= 50 else "🟢"
        return f"{icon} {total:,.0f} / {limit:,.0f} zł"

    def _refresh_display(self):
        cy, cq    = current_quarter()
        total     = self.db.get_quarter_total(cy, cq)
        limit     = self.db.get_quarterly_limit()
        remaining = limit - total
        percent   = total / limit * 100 if limit else 0
        alltime   = self.db.get_all_time_total()

        months = QUARTERS[cq]
        qlabel = f"Q{cq} {cy}  ({months[0]:02d}–{months[-1]:02d}.{cy})"
        filled = int(18 * min(percent, 100) / 100)
        bar    = "█" * filled + "░" * (18 - filled)

        self.mi_qlabel.title   = f"🗓   {qlabel}"
        self.mi_received.title = f"💵  Otrzymano:  {total:,.2f} zł"
        self.mi_remain.title   = f"💰  Pozostało: {remaining:,.2f} zł"
        self.mi_bar.title      = f"  {bar}  {percent:.0f}%"
        self.mi_alltime.title  = f"📈  Łącznie: {alltime:,.2f} zł"
        self.title             = self._get_title()

    # ── Dodaj przychód ────────────────────────────────────────────────────────

    def add_income(self, _):
        r1 = rumps.Window(
            message="Kwota przychodu (zł):",
            title="➕ Dodaj przychód",
            default_text="",
            ok="Dalej", cancel="Anuluj",
            dimensions=(220, 24)
        ).run()
        if not r1.clicked: return
        try:
            amount = float(r1.text.strip().replace(",", ".").replace(" ", ""))
            if amount <= 0: raise ValueError()
        except ValueError:
            rumps.alert("Błąd", "Podaj poprawną kwotę, np. 3600.00")
            return

        r2 = rumps.Window(
            message="Opis / źródło przychodu (opcjonalnie):",
            title="➕ Dodaj przychód",
            default_text="",
            ok="Zapisz", cancel="Anuluj",
            dimensions=(220, 24)
        ).run()
        if not r2.clicked: return

        self.db.add_income(amount, r2.text.strip())
        self._refresh_display()

        cy, cq  = current_quarter()
        total   = self.db.get_quarter_total(cy, cq)
        limit   = self.db.get_quarterly_limit()
        percent = total / limit * 100
        remain  = limit - total

        if percent >= 100:
            rumps.notification("⛔ Limit przekroczony!", "Income Tracker",
                f"Łącznie {total:,.2f} zł — limit {limit:,.0f} zł przekroczony!")
        elif percent >= 90:
            rumps.notification("🚨 90% limitu!", "Income Tracker",
                f"Pozostało tylko {remain:,.2f} zł do limitu")
        elif percent >= 75:
            rumps.notification("⚠️ 75% limitu", "Income Tracker",
                f"Pozostało {remain:,.2f} zł do limitu")
        else:
            rumps.notification("✅ Zapisano", "Income Tracker",
                f"+{amount:,.2f} zł\nRazem w Q{cq}: {total:,.2f} zł")

    # ── Ten kwartał ───────────────────────────────────────────────────────────

    def show_current(self, _):
        cy, cq  = current_quarter()
        entries = self.db.get_quarter_entries(cy, cq)
        limit   = self.db.get_quarterly_limit()

        if not entries:
            rumps.alert(f"Q{cq} {cy}", "Brak przychodów w tym kwartale.")
            return

        lines = []
        for e in entries[:20]:
            desc = f"  {e['description']}" if e.get("description") else ""
            lines.append(f"{e['date']}   {e['amount']:>9,.2f} zł{desc}")

        total   = sum(e["amount"] for e in entries)
        percent = total / limit * 100
        remain  = limit - total

        header = (
            f"Q{cq} {cy}  ·  {len(entries)} wpisów\n"
            f"Otrzymano: {total:,.2f} zł  /  {limit:,.0f} zł ({percent:.0f}%)\n"
            f"Pozostało: {remain:,.2f} zł\n"
            f"{'─'*42}"
        )
        rumps.alert(f"📋 Q{cq} {cy}", header + "\n" + "\n".join(lines))

    # ── Poprzednie kwartały ───────────────────────────────────────────────────

    def show_all_quarters(self, _):
        summaries = self.db.get_all_quarters_summary()
        if not summaries:
            rumps.alert("Historia", "Brak danych w bazie.")
            return

        limit = self.db.get_quarterly_limit()
        cy, cq = current_quarter()

        # Zbuduj listę wyboru
        options = []
        for s in summaries:
            marker = " ◀ bieżący" if (s["year"] == cy and s["q"] == cq) else ""
            bar_w  = int(12 * min(s["total"] / limit, 1.0))
            bar    = "█" * bar_w + "░" * (12 - bar_w)
            pct    = s["total"] / limit * 100
            options.append(
                f"Q{s['q']} {s['year']}  {bar}  {s['total']:>9,.2f} zł  ({pct:.0f}%){marker}"
            )

        # Pokaż przegląd wszystkich kwartałów
        alltime = self.db.get_all_time_total()
        footer  = f"\n{'─'*52}\nSUMA WSZYSTKICH: {alltime:,.2f} zł"
        overview = "\n".join(options) + footer
        rumps.alert("🕐 Wszystkie kwartały", overview)

        # Zapytaj czy chce szczegóły konkretnego
        r = rumps.Window(
            message=f"Wpisz numer kwartału (1–{len(summaries)}) aby zobaczyć szczegóły,\nlub zamknij:",
            title="🔍 Szczegóły kwartału",
            default_text="",
            ok="Pokaż", cancel="Zamknij",
            dimensions=(80, 24)
        ).run()
        if not r.clicked or not r.text.strip():
            return
        try:
            idx = int(r.text.strip()) - 1
            if not (0 <= idx < len(summaries)):
                raise ValueError()
        except ValueError:
            rumps.alert("Błąd", f"Podaj liczbę od 1 do {len(summaries)}")
            return

        s = summaries[idx]
        self._show_quarter_detail(s["year"], s["q"])

    def _show_quarter_detail(self, year: int, q: int):
        entries = self.db.get_quarter_entries(year, q)
        limit   = self.db.get_quarterly_limit()
        months  = QUARTERS[q]

        if not entries:
            rumps.alert(f"Q{q} {year}", "Brak wpisów w tym kwartale.")
            return

        lines = []
        for e in entries[:25]:
            desc = f"  {e['description']}" if e.get("description") else ""
            lines.append(f"{e['date']}   {e['amount']:>9,.2f} zł{desc}")

        total   = sum(e["amount"] for e in entries)
        percent = total / limit * 100

        header = (
            f"Q{q} {year}  ({months[0]:02d}–{months[-1]:02d}.{year})\n"
            f"{len(entries)} wpisów · Suma: {total:,.2f} zł ({percent:.0f}% limitu)\n"
            f"{'─'*42}"
        )
        rumps.alert(f"📋 Q{q} {year}", header + "\n" + "\n".join(lines))

    # ── Suma całkowita ────────────────────────────────────────────────────────

    def show_total(self, _):
        summaries = self.db.get_all_quarters_summary()
        alltime   = self.db.get_all_time_total()
        limit     = self.db.get_quarterly_limit()
        cy, cq    = current_quarter()

        if not summaries:
            rumps.alert("Suma całkowita", "Brak danych.")
            return

        # Grupuj po roku
        by_year: dict = {}
        for s in summaries:
            by_year.setdefault(s["year"], []).append(s)

        lines = []
        for year in sorted(by_year.keys()):
            qs = by_year[year]
            year_total = sum(s["total"] for s in qs)
            lines.append(f"\n── {year} ──────────────────────────────")
            for s in qs:
                marker = " ◀" if (s["year"] == cy and s["q"] == cq) else ""
                pct = s["total"] / limit * 100
                bar_w = int(10 * min(pct / 100, 1.0))
                bar = "█" * bar_w + "░" * (10 - bar_w)
                lines.append(
                    f"  Q{s['q']}  {bar}  {s['total']:>9,.2f} zł  ({pct:.0f}%){marker}"
                )
            lines.append(f"  ROK {year}:  {year_total:,.2f} zł")

        n_quarters = len([s for s in summaries if s["total"] > 0])
        avg = alltime / n_quarters if n_quarters else 0

        footer = (
            f"\n{'═'*40}\n"
            f"SUMA CAŁKOWITA:   {alltime:,.2f} zł\n"
            f"Kwartałów:        {n_quarters}\n"
            f"Średnia/kwartał:  {avg:,.2f} zł\n"
            f"Limit/kwartał:    {limit:,.0f} zł"
        )
        rumps.alert("💹 Suma całkowita przychodów", "\n".join(lines) + footer)

    # ── Usuń ostatni ─────────────────────────────────────────────────────────

    def delete_last(self, _):
        cy, cq  = current_quarter()
        entries = self.db.get_quarter_entries(cy, cq)
        if not entries:
            rumps.alert("Błąd", "Brak wpisów w bieżącym kwartale.")
            return
        last = entries[0]
        desc = f"\n{last['description']}" if last.get("description") else ""
        if rumps.alert(
            title="Usuń ostatni wpis",
            message=f"Usunąć?\n\n{last['date']}   {last['amount']:,.2f} zł{desc}",
            ok="Usuń", cancel="Anuluj"
        ) == 1:
            self.db.delete_expense(last["id"])
            self._refresh_display()
            rumps.notification("🗑 Usunięto", "Income Tracker",
                f"{last['amount']:,.2f} zł")

    def _quit(self, _):
        rumps.quit_application()


if __name__ == "__main__":
    IncomeTrackerApp().run()
