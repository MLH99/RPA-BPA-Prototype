#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BPA-demo (Business Process Automation) – visuellt för presentation

Kör:
  python bpa_demo.py

Vad du får:
- 3 fönster: LIME (case), BFUS (service/avtal), ELSMART (data)
- 1 BPA-kontrollpanel som visar processlogg + progress + knappar:
    - Kör hela processen
    - Kör ett steg i taget
    - Återställ

BPA-princip i denna demo:
- Ingen bildmatchning, inga mus-klick.
- BPA-motorn anropar "API-metoder" (in-process) som uppdaterar respektive systems datamodell.
- UI uppdateras live så publiken ser resultatet och var i flödet processen är.
"""

from __future__ import annotations

import re
import time
import datetime as _dt
import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Callable, Generator, Tuple


ROOT = Path(__file__).resolve().parent
ELSMART_HTML = ROOT / "index.html"


# -----------------------------
# Utils: Elsmart "backend"
# -----------------------------
def parse_elsmart_html(path: Path) -> Dict[str, str]:
    """Parsar din index.html och returnerar dt->dd."""
    html = path.read_text(encoding="utf-8", errors="ignore")

    # Matcha rader av typen:
    # <div class="kv__row"><dt>Ref. nr.</dt><dd>E-0000-00</dd></div>
    rows = re.findall(r'<div\s+class="kv__row"\s*>.*?<dt>(.*?)</dt>\s*<dd>(.*?)</dd>.*?</div>',
                      html, flags=re.S | re.I)
    out = {}
    for dt, dd in rows:
        # Rensa HTML entities/min whitespace
        dt = re.sub(r"<.*?>", "", dt).strip()
        dd = re.sub(r"<.*?>", "", dd).strip()
        out[dt] = dd

    return out


# -----------------------------
# UI: LIME
# -----------------------------
class LimeWindow(tk.Toplevel):
    def __init__(self, master: tk.Tk):
        super().__init__(master)
        self.title("CRM Ärendehantering – BPA-demo")
        self.geometry("640x760")
        self.minsize(600, 700)

        self.case = {
            "case_id": "L-0001",
            "ref_nr": "E-0000-00",
            "tjanstenr": "445323",
            "kundnr": "K-000001",
            "status": "Nytt",
            "reason": "",
            "checklist_done": False,
        }

        # --- layout
        C_BG = "#111827"
        C_GREEN = "#95c93d"
        C_WHITE = "#ffffff"
        C_MUTED = "#6b7280"

        self.configure(bg=C_BG)

        top = tk.Frame(self, bg=C_BG, height=52)
        top.pack(fill="x")
        top.pack_propagate(False)
        tk.Label(top, text="LIME CRM", bg=C_BG, fg="white",
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=14)

        # left info
        info = tk.Frame(self, bg=C_GREEN)
        info.pack(fill="x")

        # RPA-friendly fields (Entry) -> BPA använder model men UI visar tydligt
        tk.Label(info, text="Tjänstenummer", bg=C_GREEN, fg="white",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=12, pady=(10, 0))
        self.var_tjanstenr = tk.StringVar(value=self.case["tjanstenr"])
        self.e_tjanstenr = ttk.Entry(info, textvariable=self.var_tjanstenr, width=20,
                                     font=("Segoe UI", 14, "bold"))
        self.e_tjanstenr.pack(anchor="w", padx=12, pady=(2, 6))

        tk.Label(info, text="Kundnummer", bg=C_GREEN, fg="white",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=12, pady=(2, 0))
        self.var_kundnr = tk.StringVar(value=self.case["kundnr"])
        self.e_kundnr = ttk.Entry(info, textvariable=self.var_kundnr, width=20,
                                  font=("Segoe UI", 12, "bold"))
        self.e_kundnr.pack(anchor="w", padx=12, pady=(2, 10))

        tk.Label(info, text="Kontakt: Exempelperson\nTel: 000-000000\nexempel@organisation.se",
                 bg=C_GREEN, fg="white", justify="left", font=("Segoe UI", 10)).pack(anchor="w", padx=12, pady=(0, 12))

        body = tk.Frame(self, bg=C_BG)
        body.pack(fill="both", expand=True, padx=14, pady=14)

        card = tk.Frame(body, bg=C_WHITE)
        card.pack(fill="both", expand=True)
        tk.Label(card, text="Ärende", bg=C_WHITE, fg="#111827",
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12, pady=(12, 2))
        ttk.Separator(card, orient="horizontal").pack(fill="x", padx=12, pady=(0, 10))

        grid = tk.Frame(card, bg=C_WHITE)
        grid.pack(fill="x", padx=12)

        def row(lbl: str, value: str):
            r = tk.Frame(grid, bg=C_WHITE)
            r.pack(fill="x", pady=4)
            tk.Label(r, text=lbl, width=18, anchor="w", bg=C_WHITE, fg="#111827").pack(side="left")
            tk.Label(r, text=value, anchor="w", bg=C_WHITE, fg="#111827").pack(side="left", fill="x", expand=True)
            return r

        row("Ärende-id:", self.case["case_id"])
        row("Elsmart ref:", self.case["ref_nr"])

        tk.Label(card, text="Checklista", bg=C_WHITE, fg="#111827",
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12, pady=(14, 2))
        ttk.Separator(card, orient="horizontal").pack(fill="x", padx=12, pady=(0, 10))

        self.chk_vars: List[tk.BooleanVar] = []
        for text in [
            "Kontrollera ärendetyp",
            "Kontrollera anläggnings-id",
            "Kontrollera kontaktuppgifter",
            "Skapa/uppdatera BFUS",
            "Skapa nätavtal",
        ]:
            v = tk.BooleanVar(value=False)
            self.chk_vars.append(v)
            ttk.Checkbutton(card, text=text, variable=v).pack(anchor="w", padx=14, pady=2)

        # status area
        status = tk.Frame(self, bg="#0f172a")
        status.pack(fill="x")
        tk.Label(status, text="Status:", bg="#0f172a", fg="white",
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=(12, 6), pady=10)
        self.var_status = tk.StringVar(value=self.case["status"])
        self.lbl_status = tk.Label(status, textvariable=self.var_status, bg="#0f172a", fg="white",
                                   font=("Segoe UI", 10))
        self.lbl_status.pack(side="left", pady=10)
        self.var_reason = tk.StringVar(value="")
        self.lbl_reason = tk.Label(status, textvariable=self.var_reason, bg="#0f172a", fg=C_MUTED,
                                   font=("Segoe UI", 10))
        self.lbl_reason.pack(side="left", padx=(10, 0), pady=10)

    # ---- "API" methods
    def api_get_case(self) -> Dict[str, str]:
        # Synka från UI -> model
        self.case["tjanstenr"] = self.var_tjanstenr.get().strip()
        self.case["kundnr"] = self.var_kundnr.get().strip()
        return dict(self.case)

    def api_set_status(self, status: str, reason: str = ""):
        self.case["status"] = status
        self.case["reason"] = reason
        self.var_status.set(status)
        self.var_reason.set(f"• {reason}" if reason else "")

    def api_set_check_item(self, index: int, done: bool = True):
        """Sätt en enskild checklistpunkt (0-baserat index)."""
        if 0 <= index < len(self.chk_vars):
            self.chk_vars[index].set(done)
        self.case["checklist_done"] = all(v.get() for v in self.chk_vars)

    def api_clear_checklist(self):
        for v in self.chk_vars:
            v.set(False)
        self.case["checklist_done"] = False

    def api_reset(self):
        # Reset to defaults
        self.case.update({
            "case_id": "L-0001",
            "ref_nr": "E-0000-00",
            "tjanstenr": "445323",
            "kundnr": "K-000001",
            "status": "Nytt",
            "reason": "",
            "checklist_done": False,
        })
        self.var_tjanstenr.set(self.case["tjanstenr"])
        self.var_kundnr.set(self.case["kundnr"])
        self.api_clear_checklist()
        self.api_set_status("Nytt", "")


# -----------------------------
# UI: ELSMART (visualisering)
# -----------------------------
class ElsmartWindow(tk.Toplevel):
    def __init__(self, master: tk.Tk):
        super().__init__(master)
        self.title("Elsmart – BPA-demo (data)")
        self.geometry("520x520")
        self.minsize(480, 480)

        self.data: Dict[str, str] = {}

        top = tk.Frame(self, bg="#0f172a", height=48)
        top.pack(fill="x")
        top.pack_propagate(False)
        tk.Label(top, text="Elsmart (data)", bg="#0f172a", fg="white",
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=14)

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(body, columns=("k", "v"), show="headings", height=16)
        self.tree.heading("k", text="Fält")
        self.tree.heading("v", text="Värde")
        self.tree.column("k", width=180, anchor="w")
        self.tree.column("v", width=300, anchor="w")
        self.tree.pack(fill="both", expand=True)

        self.status = ttk.Label(self, text="Redo")
        self.status.pack(anchor="w", padx=12, pady=(0, 10))

        self.api_refresh()

    def api_refresh(self):
        try:
            self.data = parse_elsmart_html(ELSMART_HTML)
        except Exception as e:
            self.status.config(text=f"Fel: {e}")
            return

        for i in self.tree.get_children():
            self.tree.delete(i)

        for k in ["Ref. nr.", "Datum mottaget", "Kommun", "Mätarnr.", "Anläggnings-id", "Teknisk nr."]:
            self.tree.insert("", "end", values=(k, self.data.get(k, "")))

        self.status.config(text=f"Uppdaterad: {_dt.datetime.now().strftime('%H:%M:%S')}")

    def api_get_payload(self) -> Dict[str, str]:
        self.api_refresh()
        # Lägg till en "saking" som finns i BFUS combobox (demo)
        payload = dict(self.data)
        payload["Säkring"] = "16A"
        return payload


# -----------------------------
# UI: BFUS
# -----------------------------
class BFUSWindow(tk.Toplevel):
    def __init__(self, master: tk.Tk):
        super().__init__(master)
        self.title("BFUS – Prototyp (BPA)")
        self.geometry("1040x740")
        self.minsize(980, 700)

        # datamodeller
        self.service: Dict[str, str] = {
            "tjanstenr": "",
            "anlaggnings_id": "",
            "saking": "—",
        }
        self.agreement: Dict[str, str] = {
            "kundnr": "",
            "startdatum": "",
            "company": "Exempelbolag A",
            "goal": "Nätavtal",
            "forbruk": "Hushåll",
            "produkt": "",
            "deb_satt": "Månadsvis",
            "deb_formel": "Formel A",
            "pp1": "PP1-A",
            "pp2": "PP2-A",
            "kundref": "",
            "agreement_id": "",
        }

        self._build_ui()

    def _build_ui(self):
        # styling
        style = ttk.Style(self)
        for theme in ("vista", "xpnative", "aqua", "clam"):
            try:
                style.theme_use(theme)
                break
            except tk.TclError:
                continue

        palette = {
            "DARK": "#0f172a",
            "DARK2": "#111827",
            "WHITE": "#ffffff",
            "SIDELITE": "#f3f4f6",
            "TEXT": "#111827",
            "MUTED": "#6b7280",
        }
        self.palette = palette
        self.configure(bg=palette["WHITE"])

        top = tk.Frame(self, bg=palette["DARK"], height=54)
        top.pack(fill="x")
        top.pack_propagate(False)
        tk.Label(top, text="BFUS", bg=palette["DARK"], fg="white",
                 font=("Segoe UI", 13, "bold")).pack(side="left", padx=14)

        self.btn_save = tk.Button(top, text="Spara", bg=palette["DARK2"], fg="white", bd=0,
                                  padx=14, pady=8, font=("Segoe UI", 10, "bold"),
                                  command=self._save_service)
        self.btn_save.pack(side="left", padx=6, pady=10)

        self.btn_avtal = tk.Button(top, text="Skapa avtal", bg=palette["DARK2"], fg="white", bd=0,
                                   padx=14, pady=8, font=("Segoe UI", 10, "bold"),
                                   command=self._open_agreement)
        self.btn_avtal.pack(side="left", padx=6, pady=10)

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True)

        content = ttk.Frame(body)
        content.pack(side="left", fill="both", expand=True)

        head = ttk.Frame(content, padding=(14, 14, 14, 8))
        head.pack(fill="x")
        ttk.Label(head, text="Övergripande uppgifter", font=("Segoe UI", 12, "bold")).pack(side="left")
        self.lbl_updated = ttk.Label(head, text="• Väntar", foreground=palette["MUTED"])
        self.lbl_updated.pack(side="left", padx=(8, 0))

        card = ttk.LabelFrame(content, text="Service", padding=12)
        card.pack(fill="x", padx=14, pady=(0, 12))

        grid = ttk.Frame(card)
        grid.pack(fill="x")

        # Vars
        self.var_tjanstenr = tk.StringVar(value="")
        self.var_anl = tk.StringVar(value="")
        self.var_saking = tk.StringVar(value="—")

        # rows
        def labeled_entry(parent, label, var):
            r = ttk.Frame(parent)
            ttk.Label(r, text=label, width=18).pack(side="left")
            e = ttk.Entry(r, textvariable=var, width=30)
            e.pack(side="left", fill="x", expand=True)
            # "changed marker"
            m = ttk.Label(r, text="", width=10)
            m.pack(side="left", padx=(10, 0))
            return r, e, m

        r, self.e_tjanstenr, self.m_tjanstenr = labeled_entry(grid, "Tjänstenummer:", self.var_tjanstenr)
        r.pack(fill="x", pady=5)

        r, self.e_anl, self.m_anl = labeled_entry(grid, "Anläggnings-id:", self.var_anl)
        r.pack(fill="x", pady=5)

        r = ttk.Frame(grid); r.pack(fill="x", pady=5)
        ttk.Label(r, text="Säkring:", width=18).pack(side="left")
        self.cb_saking = ttk.Combobox(r, state="readonly", width=28,
                                      values=["—", "16A", "20A", "25A", "35A", "50A"],
                                      textvariable=self.var_saking)
        self.cb_saking.pack(side="left", fill="x", expand=True)
        self.m_sak = ttk.Label(r, text="", width=10)
        self.m_sak.pack(side="left", padx=(10, 0))

        # Agreement summary
        summ = ttk.LabelFrame(content, text="Avtal (sammanfattning)", padding=12)
        summ.pack(fill="x", padx=14, pady=(0, 12))

        self.var_agreement_summary = tk.StringVar(value="Inget avtal skapat än.")
        ttk.Label(summ, textvariable=self.var_agreement_summary).pack(anchor="w")

        # status bar
        status = tk.Frame(self, bg=palette["SIDELITE"], height=36)
        status.pack(fill="x")
        status.pack_propagate(False)
        self.var_status = tk.StringVar(value="Redo")
        tk.Label(status, textvariable=self.var_status, bg=palette["SIDELITE"], fg=palette["MUTED"]).pack(side="left", padx=12)

        self.agreement_win: Optional[AgreementWizard] = None

    # ---- internal UI actions
    def _save_service(self):
        messagebox.showinfo("BFUS", "Sparat (simulerat).")

    def _open_agreement(self):
        if self.agreement_win and self.agreement_win.winfo_exists():
            self.agreement_win.lift()
            return
        self.agreement_win = AgreementWizard(self, self.palette, self.agreement)

    # ---- BPA "API" methods
    def api_update_overview(self, tjanstenr: str, anlaggnings_id: str, saking: str):
        self.service.update({
            "tjanstenr": tjanstenr,
            "anlaggnings_id": anlaggnings_id,
            "saking": saking,
        })

        # Update UI + visual markers
        self.var_tjanstenr.set(tjanstenr)
        self.m_tjanstenr.config(text="✔")
        self.var_anl.set(anlaggnings_id)
        self.m_anl.config(text="✔")
        self.var_saking.set(saking)
        self.m_sak.config(text="✔")

        self.lbl_updated.config(text=f"• Uppdaterad {_dt.datetime.now().strftime('%H:%M:%S')}")
        self.var_status.set("Service uppdaterad")

    def api_create_agreement(self, data: Dict[str, str]) -> str:
        """
        Skapar avtal i modellen och uppdaterar wizard/UI.
        data keys: kundnr, startdatum, kundref, produkt, deb_satt, deb_formel, pp1, pp2, company, goal, forbruk
        """
        self.agreement.update(data)
        # skapa "id" för demo
        if not self.agreement.get("agreement_id"):
            self.agreement["agreement_id"] = f"A-{int(time.time())%10000:04d}"

        # uppdatera wizard om den är öppen
        if self.agreement_win and self.agreement_win.winfo_exists():
            self.agreement_win.api_load_from_model(self.agreement)

        # uppdatera summary
        self.var_agreement_summary.set(
            f"Avtal-id: {self.agreement['agreement_id']} • Kundnr: {self.agreement.get('kundnr','')} • "
            f"Produkt: {self.agreement.get('produkt','')} • Kundref: {self.agreement.get('kundref','')}"
        )
        self.var_status.set("Avtal skapat")
        return self.agreement["agreement_id"]

    def api_reset(self):
        self.service.update({"tjanstenr": "", "anlaggnings_id": "", "saking": "—"})
        self.var_tjanstenr.set(""); self.var_anl.set(""); self.var_saking.set("—")
        self.m_tjanstenr.config(text=""); self.m_anl.config(text=""); self.m_sak.config(text="")
        self.var_agreement_summary.set("Inget avtal skapat än.")
        self.var_status.set("Redo")

        self.agreement.update({
            "kundnr": "",
            "startdatum": "",
            "company": "Exempelbolag A",
            "goal": "Nätavtal",
            "forbruk": "Hushåll",
            "produkt": "",
            "deb_satt": "Månadsvis",
            "deb_formel": "Formel A",
            "pp1": "PP1-A",
            "pp2": "PP2-A",
            "kundref": "",
            "agreement_id": "",
        })
        if self.agreement_win and self.agreement_win.winfo_exists():
            self.agreement_win.destroy()
            self.agreement_win = None


class AgreementWizard(tk.Toplevel):
    def __init__(self, master: BFUSWindow, palette: Dict[str, str], model: Dict[str, str]):
        super().__init__(master)
        self.palette = palette
        self.model = model
        self.title("Skapa avtal")
        self.geometry("980x720")
        self.minsize(920, 660)
        self.configure(bg=palette["WHITE"])

        top = tk.Frame(self, bg=palette["DARK"], height=48)
        top.pack(fill="x")
        top.pack_propagate(False)
        tk.Label(top, text="Skapa avtal", bg=palette["DARK"], fg="white",
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=14)

        wrap = ttk.Frame(self)
        wrap.pack(fill="both", expand=True, padx=14, pady=14)

        nav = ttk.Frame(wrap)
        nav.pack(side="bottom", fill="x", pady=(10, 0))
        self.btn_back = ttk.Button(nav, text="Tillbaka", command=self.back)
        self.btn_back.pack(side="left")
        self.btn_next = ttk.Button(nav, text="Nästa", command=self.next)
        self.btn_next.pack(side="right", padx=(8, 0))
        self.btn_save = ttk.Button(nav, text="Spara avtal", command=self.save)
        self.btn_save.pack(side="right", padx=(8, 0))

        self.nb = ttk.Notebook(wrap)
        self.nb.pack(side="top", fill="both", expand=True)

        self.tab_grund = ttk.Frame(self.nb)
        self.tab_prod = ttk.Frame(self.nb)
        self.tab_pris = ttk.Frame(self.nb)
        self.tab_fakt = ttk.Frame(self.nb)

        self.nb.add(self.tab_grund, text="Grund")
        self.nb.add(self.tab_prod, text="Produkt")
        self.nb.add(self.tab_pris, text="Prisparametrar")
        self.nb.add(self.tab_fakt, text="Fakturavillkor")

        # Vars
        self.v_company = tk.StringVar()
        self.v_goal = tk.StringVar()
        self.v_kundnr = tk.StringVar()
        self.v_start = tk.StringVar()
        self.v_forbruk = tk.StringVar()
        self.v_produkt = tk.StringVar()
        self.v_deb_satt = tk.StringVar()
        self.v_deb_formel = tk.StringVar()
        self.v_pp1 = tk.StringVar()
        self.v_pp2 = tk.StringVar()
        self.v_kundref = tk.StringVar()

        self._build_tabs()
        self.api_load_from_model(self.model)
        self._sync_buttons()

    def _build_tabs(self):
        # Grund
        f = ttk.Frame(self.tab_grund, padding=12); f.pack(fill="x")
        lf = ttk.LabelFrame(f, text="Skapa nätavtal", padding=10); lf.pack(fill="x")

        def row(lbl, widget):
            r = ttk.Frame(lf); r.pack(fill="x", pady=5)
            ttk.Label(r, text=lbl, width=22).pack(side="left")
            widget.pack(side="left", fill="x", expand=True)
            return r

        row("Avtalsägande företag:", ttk.Combobox(lf, state="readonly", width=28,
                                                values=["Exempelbolag A","Exempelbolag B","Exempelbolag C"],
                                                textvariable=self.v_company))
        row("Avtalsmål:", ttk.Combobox(lf, state="readonly", width=28,
                                      values=["Nätavtal","Tillfälligt avtal","Övrigt"],
                                      textvariable=self.v_goal))

        row("Kundnummer:", ttk.Entry(lf, width=30, textvariable=self.v_kundnr))

        # Startdatum + kalender
        r = ttk.Frame(lf); r.pack(fill="x", pady=5)
        ttk.Label(r, text="Faktiskt startdatum:", width=22).pack(side="left")
        ttk.Entry(r, width=20, textvariable=self.v_start).pack(side="left")
        ttk.Button(r, text="Kalender", command=self.open_calendar).pack(side="left", padx=(8,0))

        row("Förbrukartyp:", ttk.Combobox(lf, state="readonly", width=28,
                                         values=["Hushåll","Fastighet","Industri","Övrigt"],
                                         textvariable=self.v_forbruk))

        # Produkt
        f = ttk.Frame(self.tab_prod, padding=12); f.pack(fill="both", expand=True)
        lf = ttk.LabelFrame(f, text="Sök produkt", padding=10); lf.pack(fill="x")
        btnrow = ttk.Frame(lf); btnrow.pack(fill="x", pady=(0,8))
        ttk.Button(btnrow, text="Sök produkt", command=self._noop).pack(side="left")
        ttk.Button(btnrow, text="Sök", command=self._fill_products).pack(side="left", padx=(8,0))

        r = ttk.Frame(lf); r.pack(fill="x", pady=5)
        ttk.Label(r, text="Produkt:", width=22).pack(side="left")
        self.cb_prod = ttk.Combobox(r, state="readonly", width=28, values=[""], textvariable=self.v_produkt)
        self.cb_prod.pack(side="left", fill="x", expand=True)

        lf2 = ttk.LabelFrame(f, text="Debitering", padding=10); lf2.pack(fill="x", pady=(10,0))
        r = ttk.Frame(lf2); r.pack(fill="x", pady=5)
        ttk.Label(r, text="Debiteringssätt:", width=22).pack(side="left")
        ttk.Combobox(r, state="readonly", width=28,
                    values=["Månadsvis","Kvartalsvis","Årsvis"],
                    textvariable=self.v_deb_satt).pack(side="left", fill="x", expand=True)

        r = ttk.Frame(lf2); r.pack(fill="x", pady=5)
        ttk.Label(r, text="Debiteringsformel:", width=22).pack(side="left")
        ttk.Combobox(r, state="readonly", width=28,
                    values=["Formel A","Formel B","Formel C"],
                    textvariable=self.v_deb_formel).pack(side="left", fill="x", expand=True)

        # Prisparametrar
        f = ttk.Frame(self.tab_pris, padding=12); f.pack(fill="x")
        lf = ttk.LabelFrame(f, text="Prisparametrar", padding=10); lf.pack(fill="x")
        r = ttk.Frame(lf); r.pack(fill="x", pady=5)
        ttk.Label(r, text="Prisparameter 1:", width=22).pack(side="left")
        ttk.Combobox(r, state="readonly", width=28, values=["PP1-A","PP1-B","PP1-C"], textvariable=self.v_pp1)\
            .pack(side="left", fill="x", expand=True)
        r = ttk.Frame(lf); r.pack(fill="x", pady=5)
        ttk.Label(r, text="Prisparameter 2:", width=22).pack(side="left")
        ttk.Combobox(r, state="readonly", width=28, values=["PP2-A","PP2-B","PP2-C"], textvariable=self.v_pp2)\
            .pack(side="left", fill="x", expand=True)

        # Faktura
        f = ttk.Frame(self.tab_fakt, padding=12); f.pack(fill="x")
        lf = ttk.LabelFrame(f, text="Fakturavillkor", padding=10); lf.pack(fill="x")
        r = ttk.Frame(lf); r.pack(fill="x", pady=5)
        ttk.Label(r, text="Kundreferens:", width=22).pack(side="left")
        ttk.Entry(r, width=34, textvariable=self.v_kundref).pack(side="left", fill="x", expand=True)

    def _noop(self):
        pass

    def _fill_products(self):
        products = ["Produkt 1", "Produkt 2", "Produkt 3"]
        self.cb_prod.configure(values=products)
        if not self.v_produkt.get():
            self.v_produkt.set(products[0])

    def open_calendar(self):
        win = tk.Toplevel(self)
        win.title("Välj startdatum")
        win.geometry("320x280")
        ttk.Label(win, text="Välj faktiskt startdatum", padding=10).pack(anchor="w")

        lb = tk.Listbox(win, height=8)
        lb.pack(fill="both", expand=True, padx=10, pady=10)

        base = _dt.date.today()
        for i in range(0, 10):
            lb.insert("end", (base + _dt.timedelta(days=i)).isoformat())

        def choose():
            sel = lb.curselection()
            if not sel:
                return
            self.v_start.set(lb.get(sel[0]))
            win.destroy()

        ttk.Button(win, text="OK", command=choose).pack(pady=(0,10))

    def api_load_from_model(self, m: Dict[str, str]):
        self.v_company.set(m.get("company","Exempelbolag A"))
        self.v_goal.set(m.get("goal","Nätavtal"))
        self.v_kundnr.set(m.get("kundnr",""))
        self.v_start.set(m.get("startdatum",""))
        self.v_forbruk.set(m.get("forbruk","Hushåll"))
        self.v_produkt.set(m.get("produkt",""))
        self.v_deb_satt.set(m.get("deb_satt","Månadsvis"))
        self.v_deb_formel.set(m.get("deb_formel","Formel A"))
        self.v_pp1.set(m.get("pp1","PP1-A"))
        self.v_pp2.set(m.get("pp2","PP2-A"))
        self.v_kundref.set(m.get("kundref",""))

    def _sync_buttons(self):
        idx = self.nb.index(self.nb.select())
        self.btn_back.configure(state="normal" if idx > 0 else "disabled")
        self.btn_next.configure(state="normal" if idx < 3 else "disabled")
        self.btn_save.configure(state="normal" if idx == 3 else "disabled")

    def next(self):
        idx = self.nb.index(self.nb.select())
        if idx < 3:
            self.nb.select(idx + 1)
        self._sync_buttons()

    def back(self):
        idx = self.nb.index(self.nb.select())
        if idx > 0:
            self.nb.select(idx - 1)
        self._sync_buttons()

    def save(self):
        # Synka till modell
        self.model.update({
            "company": self.v_company.get(),
            "goal": self.v_goal.get(),
            "kundnr": self.v_kundnr.get(),
            "startdatum": self.v_start.get(),
            "forbruk": self.v_forbruk.get(),
            "produkt": self.v_produkt.get(),
            "deb_satt": self.v_deb_satt.get(),
            "deb_formel": self.v_deb_formel.get(),
            "pp1": self.v_pp1.get(),
            "pp2": self.v_pp2.get(),
            "kundref": self.v_kundref.get(),
        })
        messagebox.showinfo("Skapa avtal", "Avtal sparat (simulerat).")
        self.destroy()


# -----------------------------
# BPA engine + controller (visual)
# -----------------------------
@dataclass
class Step:
    name: str
    action: Callable[[], None]


class BPAEngine:
    def __init__(self, lime: LimeWindow, elsmart: ElsmartWindow, bfus: BFUSWindow, log: Callable[[str], None]):
        self.lime = lime
        self.elsmart = elsmart
        self.bfus = bfus
        self.log = log
        self._steps: List[Step] = []
        self.reset()

    def reset(self):
        self._steps = [
            Step("Läs ärende från LIME", self.step_read_lime),
            Step("Hämta data från ELSMART", self.step_read_elsmart),
            Step("Validera data", self.step_validate),
            Step("Uppdatera BFUS (övergripande uppgifter)", self.step_update_bfus),
            Step("Skapa avtal i BFUS", self.step_create_agreement),
            Step("Sätt LIME-status = Klart", self.step_complete),
        ]
        self.ctx: Dict[str, str] = {}
        self.validated_ok = False

    def steps(self) -> List[Step]:
        return self._steps

    # ---- Steps
    def step_read_lime(self):
        case = self.lime.api_get_case()
        self.ctx.update({
            "case_id": case["case_id"],
            "ref_nr": case["ref_nr"],
            "tjanstenr": case["tjanstenr"],
            "kundnr": case["kundnr"],
        })
        self.lime.api_set_check_item(0, True)  # Kontrollera ärendetyp
        self.log(f"LIME: case={case['case_id']} tjanstenr={case['tjanstenr']} kundnr={case['kundnr']}")

    def step_read_elsmart(self):
        payload = self.elsmart.api_get_payload()
        self.ctx.update({
            "ref_nr": payload.get("Ref. nr.", self.ctx.get("ref_nr","")),
            "anlaggnings_id": payload.get("Anläggnings-id", ""),
            "saking": payload.get("Säkring", "16A"),
        })
        self.lime.api_set_check_item(1, True)  # Kontrollera anläggnings-id
        self.log(f"ELSMART: anläggnings-id={self.ctx['anlaggnings_id']} säkring={self.ctx['saking']}")

    def step_validate(self):
        # En enkel demo-regel: anläggnings-id måste vara 16 siffror
        anl = self.ctx.get("anlaggnings_id","")
        ok = bool(re.fullmatch(r"\d{16}", anl))
        self.validated_ok = ok
        if ok:
            self.log("VALIDERING: OK")
        else:
            self.log("VALIDERING: FEL – saknar/ogiltigt anläggnings-id")
            self.lime.api_set_status("Parkerad", "Ogiltigt anläggnings-id")

    def step_update_bfus(self):
        if not self.validated_ok:
            self.log("BFUS: hoppar över uppdatering (validering ej OK)")
            return
        self.bfus.api_update_overview(
            tjanstenr=self.ctx["tjanstenr"],
            anlaggnings_id=self.ctx["anlaggnings_id"],
            saking=self.ctx["saking"],
        )
        self.lime.api_set_check_item(3, True)  # Skapa/uppdatera BFUS
        self.log("BFUS: service uppdaterad")

    def step_create_agreement(self):
        if not self.validated_ok:
            self.log("BFUS: hoppar över avtal (validering ej OK)")
            return

        # BPA sätter regler/val i en payload (i verkligheten skulle det komma från regler/tabeller)
        startdatum = _dt.date.today().isoformat()
        agreement_payload = {
            "company": "Exempelbolag A",
            "goal": "Nätavtal",
            "kundnr": self.ctx["kundnr"],
            "startdatum": startdatum,
            "forbruk": "Hushåll",
            "produkt": "Produkt 1",
            "deb_satt": "Månadsvis",
            "deb_formel": "Formel A",
            "pp1": "PP1-A",
            "pp2": "PP2-A",
            "kundref": self.ctx["tjanstenr"],
        }
        agreement_id = self.bfus.api_create_agreement(agreement_payload)
        self.lime.api_set_check_item(4, True)  # Skapa nätavtal
        self.log(f"BFUS: avtal skapat id={agreement_id}")

    def step_complete(self):
        if not self.validated_ok:
            self.log("LIME: ärende parkerat (ej klart)")
            return
        self.lime.api_set_check_item(2, True)  # Kontrollera kontaktuppgifter
        self.lime.api_set_status("Klart", "")
        self.log("LIME: status satt till Klart")


class BPAController(tk.Toplevel):
    def __init__(self, master: tk.Tk, engine: BPAEngine):
        super().__init__(master)
        self.engine = engine
        self.title("BPA Controller – Process Monitor")
        self.geometry("760x520")
        self.minsize(720, 480)

        top = tk.Frame(self, bg="#0f172a", height=48)
        top.pack(fill="x")
        top.pack_propagate(False)
        tk.Label(top, text="BPA Process Monitor", bg="#0f172a", fg="white",
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=14)

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        # controls
        ctrl = ttk.Frame(body)
        ctrl.pack(fill="x")

        ttk.Button(ctrl, text="Kör hela processen", command=self.run_all).pack(side="left")
        ttk.Button(ctrl, text="Kör nästa steg", command=self.run_next).pack(side="left", padx=(8,0))
        ttk.Button(ctrl, text="Återställ", command=self.reset_all).pack(side="left", padx=(8,0))

        self.pb = ttk.Progressbar(body, mode="determinate", maximum=len(self.engine.steps()))
        self.pb.pack(fill="x", pady=(12, 6))

        # current step
        self.var_step = tk.StringVar(value="Redo")
        ttk.Label(body, textvariable=self.var_step, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 8))

        # log view
        self.tree = ttk.Treeview(body, columns=("time", "msg"), show="headings", height=14)
        self.tree.heading("time", text="Tid")
        self.tree.heading("msg", text="Logg")
        self.tree.column("time", width=90, anchor="w")
        self.tree.column("msg", width=600, anchor="w")
        self.tree.pack(fill="both", expand=True)

        self._cursor = 0
        self._running = False

    def log(self, msg: str):
        ts = _dt.datetime.now().strftime("%H:%M:%S")
        self.tree.insert("", "end", values=(ts, msg))
        self.tree.yview_moveto(1)

    def reset_all(self):
        self._running = False
        self._cursor = 0
        self.pb["value"] = 0
        self.var_step.set("Redo")
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Reset UIs via engine-owned objects
        self.engine.lime.api_reset()
        self.engine.bfus.api_reset()
        self.engine.elsmart.api_refresh()
        self.engine.reset()
        self.log("RESET: allt återställt")

    def _run_step(self, step_index: int):
        steps = self.engine.steps()
        if step_index >= len(steps):
            self._running = False
            self.var_step.set("Klar ✅")
            return

        step = steps[step_index]
        self.var_step.set(f"Steg {step_index+1}/{len(steps)}: {step.name}")
        self.log(f"START: {step.name}")

        # Gör det visuellt: liten paus så publiken hinner se
        self.after(250, lambda: self._execute(step, step_index))

    def _execute(self, step: Step, idx: int):
        try:
            step.action()
        except Exception as e:
            self._running = False
            self.log(f"FEL: {e}")
            messagebox.showerror("BPA", f"Steg misslyckades: {step.name}\n\n{e}")
            return

        self.pb["value"] = idx + 1
        self.log(f"OK: {step.name}")

        self._cursor = idx + 1
        if self._running:
            self.after(450, self.run_next)

    def run_next(self):
        if self._cursor >= len(self.engine.steps()):
            self.var_step.set("Klar ✅")
            self._running = False
            return
        self._run_step(self._cursor)

    def run_all(self):
        if self._running:
            return
        self._running = True
        self.run_next()


# -----------------------------
# App bootstrap
# -----------------------------
def main():
    root = tk.Tk()
    root.withdraw()  # vi visar bara toplevel-fönster

    lime = LimeWindow(root)
    elsmart = ElsmartWindow(root)
    bfus = BFUSWindow(root)

    # positionera fönster för presentation
    lime.geometry("+30+30")
    elsmart.geometry("+720+30")
    bfus.geometry("+30+120")

    # engine + controller
    controller: Optional[BPAController] = None

    def make_controller():
        nonlocal controller
        engine = BPAEngine(lime, elsmart, bfus, log=lambda s: controller.log(s) if controller else None)
        controller = BPAController(root, engine)
        controller.geometry("+720+580")
        # koppla engine.log säkert efter controller skapats
        engine.log = controller.log
        controller.log("Redo – tryck 'Kör hela processen' eller 'Kör nästa steg'.")

    make_controller()

    root.mainloop()


if __name__ == "__main__":
    main()
