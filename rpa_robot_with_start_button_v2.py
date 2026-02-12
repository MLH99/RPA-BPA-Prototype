#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RPA demo-robot ("som en människa") – v2
- Fortsätter från tidigare del och går vidare enligt nulägesmodellen (bilderna du skickade).

Teknik:
- Desktop (Tkinter): PyAutoGUI + OpenCV template matching (PNG-bilder i templates/)
- Web (Elsmart): Selenium (Chrome) läser DOM

Kör:
  1) Starta lokal webserver i mappen med index.html:
       python -m http.server 8000
  2) Kör roboten:
       python rpa_robot_v2.py --run
"""

from __future__ import annotations

import argparse
import random
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

import cv2
import numpy as np
import pyautogui

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
import threading
import tkinter as tk
from tkinter import ttk


# -------------------------
# Paths
# -------------------------
ROOT = Path(__file__).resolve().parent
TEMPLATES_DIR = ROOT / "templates"

BFUS_SCRIPT = ROOT / "bfus_clone_v3.py"
LIME_SCRIPT = ROOT / "lime_crm_clone_v2.py"
ELSMART_URL = "http://localhost:8000/index.html"  # eller http://localhost:8000/


# -------------------------
# OpenCV templates du ska skapa (PNG)
# -------------------------
T = {
    # === LIME ===
    "lime_signature": "lime_signature_topbar.png",
    "lime_btn_open_elsmart": "lime_btn_open_elsmartarende.png",
    "lime_btn_pricka_av": "lime_btn_pricka_av.png",
    "lime_lbl_tjanstenummer": "lime_lbl_tjanstenummer.png",  # label "Tjänstenummer"
    "lime_lbl_kundnummer": "lime_lbl_kundnummer.png",        # label "Kundnummer"

    # === BFUS (huvud) ===
    "bfus_signature": "bfus_signature_header.png",
    "bfus_btn_soktjanst": "bfus_btn_soktjanst.png",
    "bfus_btn_spara": "bfus_btn_spara.png",
    "bfus_btn_skapa_avtal": "bfus_btn_skapa_avtal.png",

    # BFUS: övergripande uppgifter (ankare → offset till höger)
    "bfus_lbl_tjanstenummer": "bfus_lbl_tjanstenummer.png",
    "bfus_lbl_anlaggnings_id": "bfus_lbl_anlaggnings_id.png",
    "bfus_lbl_saking": "bfus_lbl_saking.png",

    # BFUS popup "Sök tjänst"
    "bfus_popup_signature": "bfus_popup_sok_tjanst_title.png",
    "bfus_popup_lbl_tjanstenummer": "bfus_popup_lbl_tjanstenummer.png",
    "bfus_popup_btn_sok": "bfus_popup_btn_sok.png",
    "bfus_popup_tree_header_nyhet": "bfus_popup_tree_header_nyhet.png",
    "bfus_popup_btn_ok": "bfus_popup_btn_ok.png",

    # === BFUS wizard "Skapa avtal" ===
    "avtal_signature": "bfus_avtal_signature_title.png",  # rubrik "Skapa avtal"
    "avtal_lbl_company": "bfus_avtal_lbl_avtalsagande_foretag.png",
    "avtal_lbl_goal": "bfus_avtal_lbl_avtalsmal.png",
    "avtal_lbl_kundnr": "bfus_avtal_lbl_kundnummer.png",
    "avtal_btn_kalender": "bfus_avtal_btn_kalender.png",
    "calendar_signature": "bfus_calendar_signature_title.png",  # rubrik "Välj startdatum"
    "calendar_first_date": "bfus_calendar_first_date.png",      # första datum-raden i listan
    "calendar_btn_ok": "bfus_calendar_btn_ok.png",

    "avtal_lbl_forbruk": "bfus_avtal_lbl_forbrukartyp.png",
    "avtal_btn_next": "bfus_avtal_btn_nasta.png",  # knappen "Nästa" i wizard

    "avtal_btn_sok_produkt": "bfus_avtal_btn_sok_produkt.png",
    "avtal_btn_sok": "bfus_avtal_btn_sok.png",
    "avtal_lbl_deb_satt": "bfus_avtal_lbl_debiteringssatt.png",
    "avtal_lbl_deb_formel": "bfus_avtal_lbl_debiteringsformel.png",

    "avtal_tab_pris": "bfus_avtal_tab_prisparametrar.png",
    "avtal_lbl_pp1": "bfus_avtal_lbl_prisparameter1.png",
    "avtal_lbl_pp2": "bfus_avtal_lbl_prisparameter2.png",

    "avtal_tab_fakt": "bfus_avtal_tab_fakturavillkor.png",
    "avtal_lbl_kundref": "bfus_avtal_lbl_kundreferens.png",
    "avtal_btn_spara": "bfus_avtal_btn_spara_avtal.png",

    # Generiska dialoger
    "msgbox_ok": "msgbox_ok_button.png",
    "msgbox_avtal_ok": "msgbox_avtal_saved_ok.png",
}


# -------------------------
# PyAutoGUI inställningar
# -------------------------
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.04


@dataclass
class Match:
    center: Tuple[int, int]
    score: float
    rect: Tuple[int, int, int, int]  # x,y,w,h


class RPAError(RuntimeError):
    pass


# -------------------------
# OpenCV helpers
# -------------------------

def _screenshot_bgr() -> np.ndarray:
    img = pyautogui.screenshot()
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def locate_template(template_file: Path, threshold: float = 0.80,
                    region: Optional[Tuple[int, int, int, int]] = None) -> Match:
    if not template_file.exists():
        raise RPAError(f"Template saknas: {template_file} (lägg PNG i templates/)")

    hay = _screenshot_bgr()
    rx = ry = 0
    if region is not None:
        rx, ry, rw, rh = region
        hay = hay[ry:ry+rh, rx:rx+rw]

    needle = cv2.imread(str(template_file), cv2.IMREAD_COLOR)
    if needle is None:
        raise RPAError(f"Kunde inte läsa template: {template_file}")

    res = cv2.matchTemplate(hay, needle, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    if max_val < threshold:
        raise RPAError(f"Hittade inte {template_file.name} (score={max_val:.3f} < {threshold})")

    th, tw = needle.shape[:2]
    x = max_loc[0] + rx
    y = max_loc[1] + ry
    cx = x + tw // 2
    cy = y + th // 2
    return Match(center=(cx, cy), score=float(max_val), rect=(x, y, tw, th))

def _human_move_and_click(x: int, y: int, duration: float = 0.25, jitter: int = 3):
    x += random.randint(-jitter, jitter)
    y += random.randint(-jitter, jitter)
    pyautogui.moveTo(x, y, duration=duration)
    pyautogui.click()

    
"""def _human_move_and_click(x: int, y: int, duration: float = 0.0, jitter: int = 0):
    pyautogui.moveTo(x, y, duration=duration)
    pyautogui.click()"""


def wait_for_signature(signature_template: str,
                       timeout: float = 5.0,
                       poll: float = 0.2,
                       threshold: float = 0.75):
    """
    Väntar tills en signatur dyker upp på skärmen.
    Används för popups (kalender, dialoger, wizards).
    """
    tpl = TEMPLATES_DIR / signature_template
    end_time = time.time() + timeout

    while time.time() < end_time:
        try:
            locate_template(tpl, threshold=threshold)
            return
        except Exception:
            time.sleep(poll)

    raise RPAError(f"Popup/signatur dök inte upp i tid: {signature_template}")



def click_template(name: str, threshold: float = 0.80, offset: Tuple[int, int] = (0, 0),
                   retries: int = 25, sleep: float = 0.25,
                   region: Optional[Tuple[int, int, int, int]] = None) -> Match:
    tpl = TEMPLATES_DIR / name
    last_err: Optional[Exception] = None
    for _ in range(retries):
        try:
            m = locate_template(tpl, threshold=threshold, region=region)
            x, y = m.center[0] + offset[0], m.center[1] + offset[1]
            _human_move_and_click(x, y)
            return m
        except Exception as e:
            last_err = e
            time.sleep(sleep)
    raise RPAError(f"Kunde inte klicka {name}. Senaste fel: {last_err}")

def type_text(text: str, clear_first: bool = True, per_char: float = 0.02):
    if clear_first:
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.05)
        pyautogui.press("backspace")
        time.sleep(0.05)
    for ch in text:
        pyautogui.write(ch)
        time.sleep(per_char + random.random() * 0.01)

        
"""def type_text(text: str, clear_first: bool = True):
    if clear_first:
        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("backspace")
    pyautogui.write(text, interval=0)  # max snabbhet"""



def copy_current_field() -> str:
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.05)
    pyautogui.hotkey("ctrl", "c")
    time.sleep(0.05)
    # pyperclip är valfritt; vi använder clipboard via pyautogui/OS → paste senare.
    return ""


def alt_tab_until_signature(signature_template: str, max_tries: int = 8, threshold: float = 0.75):
    """Växlar fönster tills signaturen syns."""
    tpl = TEMPLATES_DIR / signature_template
    for i in range(max_tries):
        try:
            locate_template(tpl, threshold=threshold)
            return
        except Exception:
            pyautogui.hotkey("alt", "tab")
            time.sleep(0.8)
    raise RPAError(f"Kunde inte hitta {signature_template} via Alt+Tab efter {max_tries} försök.")


# -------------------------
# Selenium: läs Elsmart
# -------------------------

def read_elsmart() -> Dict[str, str]:
    opts = ChromeOptions()
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1400,900")

    driver = webdriver.Chrome(options=opts)
    driver.get(ELSMART_URL)
    time.sleep(0.8)

    # Robust: läs alla kv__row till dict
    kv = {}
    for row in driver.find_elements(By.CSS_SELECTOR, "div.kv__row"):
        try:
            dt = row.find_element(By.TAG_NAME, "dt").text.strip()
            dd = row.find_element(By.TAG_NAME, "dd").text.strip()
            if dt:
                kv[dt] = dd
        except Exception:
            pass

    def get(label: str, default: str = "") -> str:
        return kv.get(label, default)

    payload = {
        "ref_nr": get("Ref. nr."),
        "datum_mottaget": get("Datum mottaget"),
        "kommun": get("Kommun"),
        "matarnr": get("Mätarnr."),
        "anlaggnings_id": get("Anläggnings-id"),
        "teknisk_nr": get("Teknisk nr."),
        "saking": "16A",
    }

    driver.quit()
    return payload


# -------------------------
# Starta appar
# -------------------------

def start_app(script_path: Path) -> subprocess.Popen:
    if not script_path.exists():
        raise RPAError(f"Hittar inte: {script_path}")
    return subprocess.Popen([sys.executable, str(script_path)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# -------------------------
# Flöden i LIME/BFUS
# -------------------------

def lime_check_checklist_and_get_ids() -> Dict[str, str]:
    """Går till Lime, prickar av checklistan och hämtar tjänstenr + kundnr via copy (UI)."""
    alt_tab_until_signature(T["lime_signature"], max_tries=8, threshold=0.75)

    # Pricka av (simulerat)
    click_template(T["lime_btn_pricka_av"], threshold=0.75)

    # Kopiera kundnummer (klicka label → offset till entry)
    click_template(T["lime_lbl_kundnummer"], threshold=0.78, offset=(0, 32))
    pyautogui.hotkey("ctrl", "a"); time.sleep(0.05)
    pyautogui.hotkey("ctrl", "c"); time.sleep(0.05)

    # Vi paste: kundnummer i BFUS senare direkt (Ctrl+V)
    kundnr_clipboard_ready = True

    # Kopiera tjänstenummer till clipboard (för kundreferens i BFUS)
    click_template(T["lime_lbl_tjanstenummer"], threshold=0.78, offset=(0, 32))
    pyautogui.hotkey("ctrl", "a"); time.sleep(0.05)
    pyautogui.hotkey("ctrl", "c"); time.sleep(0.05)

    return {"tjanstenr_clipboard": "yes", "kundnr_clipboard": "yes"}


def bfus_fill_overgripande(payload: Dict[str, str], tjanstenr: str):
    """Den del ni redan har: fyll övergripande uppgifter + söktjänst + spara."""
    alt_tab_until_signature(T["bfus_signature"], max_tries=8, threshold=0.75)

    click_template(T["bfus_lbl_tjanstenummer"], threshold=0.78, offset=(240, 0))
    type_text(tjanstenr)

    click_template(T["bfus_lbl_anlaggnings_id"], threshold=0.78, offset=(240, 0))
    type_text(payload.get("anlaggnings_id", ""))

    click_template(T["bfus_lbl_saking"], threshold=0.78, offset=(240, 0))
    pyautogui.hotkey("alt", "down"); time.sleep(0.15)
    type_text(payload.get("saking", "16A"), clear_first=False)
    pyautogui.press("enter")

    click_template(T["bfus_btn_soktjanst"], threshold=0.78)
    alt_tab_until_signature(T["bfus_popup_signature"], max_tries=6, threshold=0.75)

    click_template(T["bfus_popup_lbl_tjanstenummer"], threshold=0.78, offset=(240, 0))
    type_text(tjanstenr)

    click_template(T["bfus_popup_btn_sok"], threshold=0.78)

    click_template(T["bfus_popup_tree_header_nyhet"], threshold=0.75, offset=(40, 60))
    pyautogui.press("down"); time.sleep(0.1)

    # OK i popup
    click_template(T["bfus_popup_btn_ok"], threshold=0.75)

    # Spara BFUS + OK på msgbox
    click_template(T["bfus_btn_spara"], threshold=0.78)
    click_template(T["msgbox_ok"], threshold=0.70)


def bfus_create_avtal_flow(payload: Dict[str, str]):
    """
    Fortsättning enligt nulägesmodellen:
    - Går till BFUS, väljer Skapa avtal
    - Väljer företag/avtalsmål, skriver kundnummer, väljer startdatum, förbrukartyp
    - Sök produkt, välj produkt, debiteringssätt/debiteringsformel
    - Prisparametrar
    - Fakturavillkor: klistra in tjänstenr som kundreferens
    """
    alt_tab_until_signature(T["bfus_signature"], max_tries=8, threshold=0.75)

    # Öppna wizard
    click_template(T["bfus_btn_skapa_avtal"], threshold=0.78)
    alt_tab_until_signature(T["avtal_signature"], max_tries=6, threshold=0.75)

    # Avtalsägande företag (klick label → offset till combobox)
    click_template(T["avtal_lbl_company"], threshold=0.75, offset=(260, 0))
    pyautogui.hotkey("alt", "down"); time.sleep(0.15)
    pyautogui.press("down"); pyautogui.press("enter")

    # Avtalsmål
    click_template(T["avtal_lbl_goal"], threshold=0.75, offset=(260, 0))
    pyautogui.hotkey("alt", "down"); time.sleep(0.15)
    pyautogui.press("down"); pyautogui.press("enter")

    # Kundnummer: klistra från Lime clipboard (vi kopierade kundnr sist – alt: kopiera igen)
    click_template(T["avtal_lbl_kundnr"], threshold=0.75, offset=(260, 0))
    pyautogui.hotkey("ctrl", "a"); time.sleep(0.05)
    pyautogui.hotkey("ctrl", "v")  # kundnummer från Lime

    # Kalender
    click_template(T["avtal_btn_kalender"], threshold=0.75)
    # Vänta tills kalender-popupen faktiskt syns
    wait_for_signature(T["calendar_signature"], timeout=5.0)
    click_template(T["calendar_first_date"], threshold=0.70)
    click_template(T["calendar_btn_ok"], threshold=0.70)

    # Förbrukartyp
    click_template(T["avtal_lbl_forbruk"], threshold=0.75, offset=(260, 0))
    pyautogui.hotkey("alt", "down"); time.sleep(0.15)
    pyautogui.press("down"); pyautogui.press("enter")

    # Nästa → Produkt
    click_template(T["avtal_btn_next"], threshold=0.75)

    # Produkt: sök produkt + sök
    click_template(T["avtal_btn_sok_produkt"], threshold=0.75)
    click_template(T["avtal_btn_sok"], threshold=0.75)

    # Debiteringssätt
    click_template(T["avtal_lbl_deb_satt"], threshold=0.75, offset=(260, 0))
    pyautogui.hotkey("alt", "down"); time.sleep(0.15)
    pyautogui.press("down"); pyautogui.press("enter")

    # Debiteringsformel
    click_template(T["avtal_lbl_deb_formel"], threshold=0.75, offset=(260, 0))
    pyautogui.hotkey("alt", "down"); time.sleep(0.15)
    pyautogui.press("down"); pyautogui.press("enter")

    # Nästa → Prisparametrar
    click_template(T["avtal_btn_next"], threshold=0.75)

    # Prisparameter 1/2
    click_template(T["avtal_lbl_pp1"], threshold=0.75, offset=(260, 0))
    pyautogui.hotkey("alt", "down"); time.sleep(0.15)
    pyautogui.press("down"); pyautogui.press("enter")

    click_template(T["avtal_lbl_pp2"], threshold=0.75, offset=(260, 0))
    pyautogui.hotkey("alt", "down"); time.sleep(0.15)
    pyautogui.press("down"); pyautogui.press("enter")

    # Nästa → Fakturavillkor
    click_template(T["avtal_btn_next"], threshold=0.75)

    # Kundreferens: klistra in tjänstenummer (vi kopierade det sist i Lime)
    click_template(T["avtal_lbl_kundref"], threshold=0.75, offset=(260, 0))
    pyautogui.hotkey("ctrl", "a"); time.sleep(0.05)
    pyautogui.hotkey("ctrl", "v")

    # Spara avtal
    click_template(T["avtal_btn_spara"], threshold=0.75)

    # OK i messagebox "Avtal sparat (simulerat)."
    click_template(T["msgbox_avtal_ok"], threshold=0.70)


# -------------------------
# CLI
# -------------------------

def wait_for_start_button():
    """Visar ett litet fönster med Start/Avbryt och blockerar tills du trycker Start."""
    evt = threading.Event()

    win = tk.Tk()
    win.title("RPA Controller")
    win.geometry("320x160")
    win.resizable(False, False)

    ttk.Label(win, text="RPA-roboten är redo.", font=("Segoe UI", 11, "bold")).pack(pady=(16, 6))
    ttk.Label(win, text="Tryck Start när dina fönster ligger rätt.", wraplength=280).pack(pady=(0, 14))

    btns = ttk.Frame(win)
    btns.pack()

    def start():
        evt.set()
        win.destroy()

    def cancel():
        win.destroy()

    ttk.Button(btns, text="Start", command=start).pack(side="left", padx=8)
    ttk.Button(btns, text="Avbryt", command=cancel).pack(side="left", padx=8)

    win.protocol("WM_DELETE_WINDOW", cancel)
    win.mainloop()

    if not evt.is_set():
        raise SystemExit("Avbrutet av användaren (Start trycktes inte).")

def print_templates():
    print("\nLägg följande PNG-bilder i:", TEMPLATES_DIR)
    for k, v in T.items():
        print(f"- {v}   (key: {k})")
    print("\nTips:")
    print("- Beskär tajt runt text/knapp.")
    print("- Ta bilder i samma upplösning/DPI som demon.")
    print("- Signaturer: ta bara rubriken (t.ex. 'BFUS', 'Skapa avtal').\n")


def run():
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

    # ✅ Vänta på att du trycker Start (bra för demo/presentation)
    wait_for_start_button()

    # Starta appar (kan kommenteras bort om du startar manuellt)
    lime_proc = start_app(LIME_SCRIPT)
    bfus_proc = start_app(BFUS_SCRIPT)
    time.sleep(2.0)

    # 1) Läs Elsmart
    payload = read_elsmart()
    print("Elsmart payload:", payload)

    # 2) (Din tidigare del) – här antar vi att du redan har en tjänstenr från Lime
    tjanstenr = "445323"
    bfus_fill_overgripande(payload, tjanstenr)

    # 3) Fortsättning enligt nya modellen:
    # Gå till Lime och prick av checklistan + kopiera kundnr + tjänstenr till clipboard
    lime_check_checklist_and_get_ids()

    # Gå till BFUS och skapa avtal (wizard)
    bfus_create_avtal_flow(payload)

    print("✅ Klar (hela flödet).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--print-templates", action="store_true")
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()

    if args.print_templates:
        print_templates()
        return
    if args.run:
        run()
        return
    ap.print_help()


if __name__ == "__main__":
    main()