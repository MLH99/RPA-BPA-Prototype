import tkinter as tk
from tkinter import ttk, messagebox

# ============================================================
# BFUS – GUI-klon (Modern, mörk + vit) – uppdaterad enligt ändringar
# - Vänsterkolumn: övre navigering + nedre mörk knappsektion
# - "Övergripande uppgifter" med specificerade fält
# - Flikar: Allmänt, Avtal, Aktörshistorik, Installation, Nyckelhantering, AMM
# - Söktjänst öppnar extra fönster (Toplevel)
# - Generiska värden
# ============================================================

APP_TITLE = "BFUS – Prototyp"

def apply_modern_style(root: tk.Tk):
    style = ttk.Style(root)
    for theme in ("vista", "xpnative", "aqua", "clam"):
        try:
            style.theme_use(theme)
            break
        except tk.TclError:
            continue

    DARK = "#0f172a"     # slate-900
    DARK2 = "#111827"    # gray-900
    BORDER = "#e5e7eb"   # gray-200
    TEXT = "#111827"
    MUTED = "#6b7280"
    WHITE = "#ffffff"
    BTN = "#111827"
    BTN_HOVER = "#1f2937"
    SIDELITE = "#f3f4f6"

    root.configure(bg=WHITE)

    style.configure(".", font=("Segoe UI", 10), background=WHITE, foreground=TEXT)
    style.configure("TFrame", background=WHITE)
    style.configure("TLabel", background=WHITE, foreground=TEXT)
    style.configure("TLabelframe", background=WHITE)
    style.configure("TLabelframe.Label", background=WHITE, foreground=TEXT, font=("Segoe UI", 10, "bold"))

    style.configure("TEntry", padding=7)
    style.configure("TCombobox", padding=6)

    style.configure("TNotebook", background=WHITE, borderwidth=0)
    style.configure("TNotebook.Tab", padding=(14, 8), background=WHITE, foreground=TEXT)
    style.map("TNotebook.Tab",
              background=[("selected", SIDELITE)],
              foreground=[("selected", TEXT)])

    style.configure("Treeview",
                    background=WHITE,
                    fieldbackground=WHITE,
                    foreground=TEXT,
                    rowheight=28,
                    bordercolor=BORDER,
                    lightcolor=BORDER,
                    darkcolor=BORDER)
    style.configure("Treeview.Heading",
                    background=SIDELITE,
                    foreground=TEXT,
                    relief="flat",
                    font=("Segoe UI", 10, "bold"))
    style.map("Treeview",
              background=[("selected", "#dbeafe")],
              foreground=[("selected", TEXT)])

    style.configure("Secondary.TButton", padding=(12, 8))
    style.configure("Ghost.TButton", padding=(12, 8))

    return {
        "DARK": DARK, "DARK2": DARK2,
        "BORDER": BORDER, "TEXT": TEXT, "MUTED": MUTED,
        "WHITE": WHITE, "BTN": BTN, "BTN_HOVER": BTN_HOVER,
        "SIDELITE": SIDELITE
    }

def make_labeled_entry(parent, text, width=26):
    row = ttk.Frame(parent)
    ttk.Label(row, text=text, width=18).pack(side="left")
    e = ttk.Entry(row, width=width)
    e.pack(side="left", fill="x", expand=True)
    return row, e

def make_labeled_combo(parent, text, values, width=24):
    row = ttk.Frame(parent)
    ttk.Label(row, text=text, width=18).pack(side="left")
    cb = ttk.Combobox(row, values=values, width=width, state="readonly")
    if values:
        cb.current(0)
    cb.pack(side="left", fill="x", expand=True)
    return row, cb

class SearchServiceWindow(tk.Toplevel):
    def __init__(self, master, palette):
        super().__init__(master)
        self.palette = palette
        self.title("Sök tjänst")
        self.geometry("920x670")
        self.minsize(860, 620)
        self.configure(bg=palette["WHITE"])

        top = tk.Frame(self, bg=palette["DARK"], height=48)
        top.pack(fill="x")
        top.pack_propagate(False)

        tk.Label(top, text="Sök tjänst", bg=palette["DARK"], fg="white",
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=14)

        tk.Button(top, text="×", bg=palette["DARK"], fg="white", bd=0,
                  activebackground=palette["DARK2"], activeforeground="white",
                  padx=12, pady=6, command=self.destroy).pack(side="right", padx=10, pady=8)

        wrap = ttk.Frame(self)
        wrap.pack(fill="both", expand=True, padx=14, pady=14)

        nb = ttk.Notebook(wrap)
        nb.pack(fill="both", expand=True)

        tab_standard = ttk.Frame(nb)
        tab_extra = ttk.Frame(nb)
        nb.add(tab_standard, text="Standard")
        nb.add(tab_extra, text="Tjänst Extra")

        form = ttk.Frame(tab_standard, padding=(10, 10))
        form.pack(fill="x")

        left_col = ttk.Frame(form)
        right_col = ttk.Frame(form)
        left_col.pack(side="left", fill="x", expand=True, padx=(0, 18))
        right_col.pack(side="left", fill="x", expand=True)

        lf = ttk.LabelFrame(left_col, text="Sökvillkor", padding=10)
        lf.pack(fill="x")

        rows = []
        r, e_tjanstnr = make_labeled_entry(lf, "Tjänstenummer:")
        rows.append((r, e_tjanstnr, ""))
        r, e_anl_id = make_labeled_entry(lf, "Anläggnings-id:")
        rows.append((r, e_anl_id, "0000000000000000"))
        r, cb_ny = make_labeled_combo(lf, "Nyhet:", ["", "Ny anläggning", "Ändring", "Avslut"])
        rows.append((r, cb_ny, ""))
        r, cb_aff = make_labeled_combo(lf, "Affärsenhet:", ["", "Region A", "Region B", "Region C"])
        rows.append((r, cb_aff, ""))
        r, e_bes = make_labeled_entry(lf, "Beskrivning:")
        rows.append((r, e_bes, ""))
        r, cb_status = make_labeled_combo(lf, "Tjänstestatus:", ["", "Aktiv", "Planerad", "Avslutad"])
        rows.append((r, cb_status, ""))

        for row, w, default in rows:
            row.pack(fill="x", pady=4)
            try:
                w.set(default)
            except Exception:
                if default:
                    w.insert(0, default)

        prod_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(lf, text="I produktion", variable=prod_var).pack(anchor="w", pady=(8, 0))

        rf = ttk.LabelFrame(right_col, text="Plats / Tjänsteställe", padding=10)
        rf.pack(fill="x")

        right_fields = []
        r, e_tjstst = make_labeled_entry(rf, "Tjänstställenr:")
        right_fields.append((r, e_tjstst, ""))
        r, e_ansl = make_labeled_entry(rf, "Anslutningsnr:")
        right_fields.append((r, e_ansl, ""))
        r, e_gata = make_labeled_entry(rf, "Gata:")
        right_fields.append((r, e_gata, ""))
        r, e_post = make_labeled_entry(rf, "Postnr/Ort:")
        right_fields.append((r, e_post, ""))

        for row, w, default in right_fields:
            row.pack(fill="x", pady=4)
            if default:
                w.insert(0, default)

        action_row = ttk.Frame(tab_standard, padding=(10, 0, 10, 10))
        action_row.pack(fill="x")
        ttk.Button(action_row, text="Sök", command=self.run_search, style="Secondary.TButton").pack(side="right")

        grid_frame = ttk.Frame(tab_standard, padding=(10, 0, 10, 10))
        grid_frame.pack(fill="both", expand=True)

        cols = ("Nyhet", "Tjänst", "Beskrivning", "Anläggnings-id", "Affärsenhet", "Tjänstestatus", "Status börjar")
        self.tree = ttk.Treeview(grid_frame, columns=cols, show="headings", height=3)
        for c in cols:
            self.tree.heading(c, text=c)
            w = 170 if c == "Beskrivning" else 130
            if c == "Anläggnings-id":
                w = 170
            self.tree.column(c, width=w, anchor="w")
        self.tree.pack(side="left", fill="both", expand=True)

        ysb = ttk.Scrollbar(grid_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=ysb.set)
        ysb.pack(side="right", fill="y")

        bottom = ttk.Frame(wrap)
        bottom.pack(fill="x", pady=(10, 0))

        self.status_lbl = ttk.Label(bottom, text="Antal rader: 0 • Markerade: 0")
        self.status_lbl.pack(side="left")

        ttk.Button(bottom, text="Töm sökvillkor", command=self.clear_fields, style="Ghost.TButton").pack(side="right", padx=(8, 0))
        ttk.Button(bottom, text="Avbryt", command=self.destroy, style="Ghost.TButton").pack(side="right", padx=(8, 0))
        ttk.Button(bottom, text="OK", command=self.ok, style="Secondary.TButton").pack(side="right", padx=(8, 0))

        self.tree.bind("<<TreeviewSelect>>", self.update_counts)

        ttk.Label(tab_extra, text="(Simulerad vy) Extra sökfält kan läggas här.", padding=14).pack(anchor="w")

    def clear_fields(self):
        for widget in self._walk_widgets(self):
            if isinstance(widget, ttk.Entry):
                widget.delete(0, "end")
            elif isinstance(widget, ttk.Combobox):
                try:
                    widget.set("")
                except Exception:
                    pass
        self.run_search(clear_only=True)

    def _walk_widgets(self, parent):
        for w in parent.winfo_children():
            yield w
            yield from self._walk_widgets(w)

    def run_search(self, clear_only=False):
        for i in self.tree.get_children():
            self.tree.delete(i)

        if clear_only:
            self.status_lbl.config(text="Antal rader: 0 • Markerade: 0")
            return

        rows = [
            ("Ny anläggning", "Tjänst", "Exempelrad A", "0000000000000001", "Region A", "Aktiv", "2025-01-10"),
            ("Ändring", "Tjänst", "Exempelrad B", "0000000000000002", "Region B", "Planerad", "2025-02-01"),
            ("", "Tjänst", "Exempelrad C", "0000000000000003", "Region C", "Avslutad", "2024-12-15"),
        ]
        for r in rows:
            self.tree.insert("", "end", values=r)

        self.status_lbl.config(text=f"Antal rader: {len(rows)} • Markerade: 0")

    def update_counts(self, *_):
        total = len(self.tree.get_children())
        marked = len(self.tree.selection())
        self.status_lbl.config(text=f"Antal rader: {total} • Markerade: {marked}")

    def ok(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sök tjänst", "Välj en rad först (simulerat).")
            return
        values = self.tree.item(sel[0], "values")
        self.master.vars["anlaggnings_id"].set(values[3])
        self.master.vars["affarsenhet"].set(values[4])
        self.master.vars["tjanstestatus"].set(values[5])
        self.destroy()



class AgreementWizard(tk.Toplevel):
    """
    Skapa nätavtal / avtal (simulerad wizard) enligt nulägesmodellen.
    RPA-vänlig: tydliga labels och knappar med stabil text.
    """
    def __init__(self, master, palette, initial=None):
        super().__init__(master)
        self.palette = palette
        self.title("Skapa avtal")
        self.geometry("980x720")
        self.minsize(920, 660)
        self.configure(bg=palette["WHITE"])

        self.data = initial or {}

        top = tk.Frame(self, bg=palette["DARK"], height=48)
        top.pack(fill="x")
        top.pack_propagate(False)
        tk.Label(top, text="Skapa avtal", bg=palette["DARK"], fg="white",
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=14)
        tk.Button(top, text="×", bg=palette["DARK"], fg="white", bd=0,
                  activebackground=palette["DARK2"], activeforeground="white",
                  padx=12, pady=6, command=self.destroy).pack(side="right", padx=10, pady=8)

        wrap = ttk.Frame(self)
        wrap.pack(fill="both", expand=True, padx=14, pady=14)

        # Bottom nav fixed
        nav = ttk.Frame(wrap)
        nav.pack(side="bottom", fill="x", pady=(10, 0))

        self.btn_back = ttk.Button(nav, text="Tillbaka", command=self.back, style="Ghost.TButton")
        self.btn_back.pack(side="left")
        self.btn_next = ttk.Button(nav, text="Nästa", command=self.next, style="Secondary.TButton")
        self.btn_next.pack(side="right", padx=(8, 0))
        self.btn_save = ttk.Button(nav, text="Spara avtal", command=self.save, style="Secondary.TButton")
        self.btn_save.pack(side="right", padx=(8, 0))

        self.nb = ttk.Notebook(wrap)
        self.nb.pack(side="top", fill="both", expand=True)

        self.tab_grund = ttk.Frame(self.nb)
        self.tab_produkt = ttk.Frame(self.nb)
        self.tab_pris = ttk.Frame(self.nb)
        self.tab_fakt = ttk.Frame(self.nb)

        self.nb.add(self.tab_grund, text="Grund")
        self.nb.add(self.tab_produkt, text="Produkt")
        self.nb.add(self.tab_pris, text="Prisparametrar")
        self.nb.add(self.tab_fakt, text="Fakturavillkor")

        self._build_grund()
        self._build_produkt()
        self._build_pris()
        self._build_fakturavillkor()

        self._sync_buttons()

    # ---- UI builders

    def _build_grund(self):
        frame = ttk.Frame(self.tab_grund, padding=12)
        frame.pack(fill="x")

        lf = ttk.LabelFrame(frame, text="Skapa nätavtal", padding=10)
        lf.pack(fill="x")

        # Avtalsägande företag + avtalsmål
        r = ttk.Frame(lf); r.pack(fill="x", pady=5)
        ttk.Label(r, text="Avtalsägande företag:", width=22).pack(side="left")
        self.cb_company = ttk.Combobox(r, state="readonly", width=28,
                                      values=["Exempelbolag A", "Exempelbolag B", "Exempelbolag C"])
        self.cb_company.current(0)
        self.cb_company.pack(side="left", fill="x", expand=True)

        r = ttk.Frame(lf); r.pack(fill="x", pady=5)
        ttk.Label(r, text="Avtalsmål:", width=22).pack(side="left")
        self.cb_goal = ttk.Combobox(r, state="readonly", width=28,
                                   values=["Nätavtal", "Tillfälligt avtal", "Övrigt"])
        self.cb_goal.current(0)
        self.cb_goal.pack(side="left", fill="x", expand=True)

        # Kundnummer
        r = ttk.Frame(lf); r.pack(fill="x", pady=5)
        ttk.Label(r, text="Kundnummer:", width=22).pack(side="left")
        self.e_kundnr = ttk.Entry(r, width=30)
        self.e_kundnr.pack(side="left", fill="x", expand=True)
        if self.data.get("kundnummer"):
            self.e_kundnr.insert(0, self.data["kundnummer"])

        # Faktiskt startdatum + kalenderknapp (simulerad)
        r = ttk.Frame(lf); r.pack(fill="x", pady=5)
        ttk.Label(r, text="Faktiskt startdatum:", width=22).pack(side="left")
        self.e_start = ttk.Entry(r, width=20)
        self.e_start.pack(side="left")
        ttk.Button(r, text="Kalender", command=self.open_calendar, style="Secondary.TButton").pack(side="left", padx=(8,0))

        # Förbrukartyp
        r = ttk.Frame(lf); r.pack(fill="x", pady=5)
        ttk.Label(r, text="Förbrukartyp:", width=22).pack(side="left")
        self.cb_forbruk = ttk.Combobox(r, state="readonly", width=28,
                                      values=["Hushåll", "Fastighet", "Industri", "Övrigt"])
        self.cb_forbruk.current(0)
        self.cb_forbruk.pack(side="left", fill="x", expand=True)

        ttk.Label(self.tab_grund, text="Tips: Robot väljer värden och trycker Nästa.", padding=12).pack(anchor="w")

    def _build_produkt(self):
        frame = ttk.Frame(self.tab_produkt, padding=12)
        frame.pack(fill="both", expand=True)

        lf = ttk.LabelFrame(frame, text="Sök produkt", padding=10)
        lf.pack(fill="x")

        # knappar "Sök produkt" och "Sök"
        btnrow = ttk.Frame(lf); btnrow.pack(fill="x", pady=(0,8))
        ttk.Button(btnrow, text="Sök produkt", command=self.show_product_search, style="Secondary.TButton").pack(side="left")
        ttk.Button(btnrow, text="Sök", command=self.run_product_search, style="Secondary.TButton").pack(side="left", padx=(8,0))

        # produkt-meny
        r = ttk.Frame(lf); r.pack(fill="x", pady=5)
        ttk.Label(r, text="Produkt:", width=22).pack(side="left")
        self.cb_product = ttk.Combobox(r, state="readonly", width=28, values=[""])
        self.cb_product.set("")
        self.cb_product.pack(side="left", fill="x", expand=True)

        lf2 = ttk.LabelFrame(frame, text="Debitering", padding=10)
        lf2.pack(fill="x", pady=(10,0))

        r = ttk.Frame(lf2); r.pack(fill="x", pady=5)
        ttk.Label(r, text="Debiteringssätt:", width=22).pack(side="left")
        self.cb_deb_satt = ttk.Combobox(r, state="readonly", width=28,
                                      values=["Månadsvis", "Kvartalsvis", "Årsvis"])
        self.cb_deb_satt.current(0)
        self.cb_deb_satt.pack(side="left", fill="x", expand=True)

        r = ttk.Frame(lf2); r.pack(fill="x", pady=5)
        ttk.Label(r, text="Debiteringsformel:", width=22).pack(side="left")
        self.cb_deb_formel = ttk.Combobox(r, state="readonly", width=28,
                                         values=["Formel A", "Formel B", "Formel C"])
        self.cb_deb_formel.current(0)
        self.cb_deb_formel.pack(side="left", fill="x", expand=True)

    def _build_pris(self):
        frame = ttk.Frame(self.tab_pris, padding=12)
        frame.pack(fill="x")

        lf = ttk.LabelFrame(frame, text="Prisparametrar", padding=10)
        lf.pack(fill="x")

        r = ttk.Frame(lf); r.pack(fill="x", pady=5)
        ttk.Label(r, text="Prisparameter 1:", width=22).pack(side="left")
        self.cb_pp1 = ttk.Combobox(r, state="readonly", width=28,
                                  values=["PP1-A", "PP1-B", "PP1-C"])
        self.cb_pp1.current(0)
        self.cb_pp1.pack(side="left", fill="x", expand=True)

        r = ttk.Frame(lf); r.pack(fill="x", pady=5)
        ttk.Label(r, text="Prisparameter 2:", width=22).pack(side="left")
        self.cb_pp2 = ttk.Combobox(r, state="readonly", width=28,
                                  values=["PP2-A", "PP2-B", "PP2-C"])
        self.cb_pp2.current(0)
        self.cb_pp2.pack(side="left", fill="x", expand=True)

    def _build_fakturavillkor(self):
        frame = ttk.Frame(self.tab_fakt, padding=12)
        frame.pack(fill="x")

        lf = ttk.LabelFrame(frame, text="Fakturavillkor", padding=10)
        lf.pack(fill="x")

        r = ttk.Frame(lf); r.pack(fill="x", pady=5)
        ttk.Label(r, text="Kundreferens:", width=22).pack(side="left")
        self.e_kundref = ttk.Entry(r, width=34)
        self.e_kundref.pack(side="left", fill="x", expand=True)

        ttk.Label(self.tab_fakt, text="Här klistrar roboten in tjänstenummer från Lime.", padding=12).pack(anchor="w")

    # ---- actions

    def open_calendar(self):
        win = tk.Toplevel(self)
        win.title("Välj startdatum")
        win.geometry("320x280")
        win.configure(bg=self.palette["WHITE"])
        ttk.Label(win, text="Välj faktiskt startdatum", padding=10).pack(anchor="w")

        lb = tk.Listbox(win, height=8)
        lb.pack(fill="both", expand=True, padx=10, pady=10)

        # några demo-datum
        today = tk.StringVar()
        dates = []
        import datetime as _dt
        base = _dt.date.today()
        for i in range(0, 10):
            dates.append((base + _dt.timedelta(days=i)).isoformat())
        for d in dates:
            lb.insert("end", d)

        def choose():
            sel = lb.curselection()
            if not sel:
                return
            val = lb.get(sel[0])
            self.e_start.delete(0, "end")
            self.e_start.insert(0, val)
            win.destroy()

        ttk.Button(win, text="OK", command=choose, style="Secondary.TButton").pack(pady=(0,10))

    def show_product_search(self):
        # inget extra behövs; knappen finns för att matcha nulägesmodellen
        pass

    def run_product_search(self):
        # fyll produktlista (simulerat)
        products = ["Produkt 1", "Produkt 2", "Produkt 3"]
        self.cb_product.configure(values=products)
        self.cb_product.current(0)

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
        messagebox.showinfo("Skapa avtal", "Avtal sparat (simulerat).")
        self.destroy()

class BFUSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.palette = apply_modern_style(self)
        self.title(APP_TITLE)
        self.geometry("1280x800")
        self.minsize(1160, 700)

        self.vars = {
            "tjanstenr": tk.StringVar(value=""),
            "beskrivning": tk.StringVar(value=""),
            "tjanstestalle": tk.StringVar(value=""),
            "anslutningsnr": tk.StringVar(value=""),
            "affarsenhet": tk.StringVar(value="Region A"),
            "tjanstestatus": tk.StringVar(value="Aktiv"),
            "anlaggnings_id": tk.StringVar(value="0000000000000000"),
            "distrikt": tk.StringVar(value="D1"),
            "avlasningsbok": tk.StringVar(value="AB-01"),
            "natomrade": tk.StringVar(value="N1"),
            "elomrade": tk.StringVar(value="EL-1"),
            "saking": tk.StringVar(value="—"),
            "antal_faser": tk.StringVar(value="3"),
            "spanning": tk.StringVar(value="400V"),
        }

        top = tk.Frame(self, bg=self.palette["DARK"], height=54)
        top.pack(fill="x")
        top.pack_propagate(False)

        tk.Label(top, text="BFUS", bg=self.palette["DARK"], fg="white",
                 font=("Segoe UI", 13, "bold")).pack(side="left", padx=14)

        def topbtn(text, cmd):
            b = tk.Button(top, text=text, command=cmd,
                          bg=self.palette["BTN"], fg="white", bd=0,
                          activebackground=self.palette["BTN_HOVER"], activeforeground="white",
                          padx=14, pady=8, font=("Segoe UI", 10, "bold"))
            b.pack(side="left", padx=6, pady=10)
            return b

        topbtn("Söktjänst", self.open_search)
        topbtn("Skapa avtal", self.open_agreement)
        topbtn("Spara", self.save)
        topbtn("Avsluta", self.quit)

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True)

        sidebar = ttk.Frame(body, width=280)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        sh = tk.Frame(sidebar, bg=self.palette["SIDELITE"], height=48)
        sh.pack(fill="x")
        sh.pack_propagate(False)
        tk.Label(sh, text="Navigation", bg=self.palette["SIDELITE"], fg=self.palette["TEXT"],
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=12)

        nav = ttk.Treeview(sidebar, show="tree", height=16)
        nav.pack(fill="x", padx=10, pady=(10, 8))
        root_id = nav.insert("", "end", text="Tjänster")
        node = nav.insert(root_id, "end", text="Ärende")
        nav.insert(node, "end", text="Skapa / Redigera")
        nav.insert(root_id, "end", text="Kundinfo")
        nav.insert("", "end", text="Rapporter")
        nav.item(root_id, open=True)
        nav.item(node, open=True)

        side_bottom = tk.Frame(sidebar, bg=self.palette["DARK2"])
        side_bottom.pack(fill="both", expand=True)
        side_bottom.pack_propagate(False)

        tk.Label(side_bottom, text="Moduler", bg=self.palette["DARK2"], fg="white",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=12, pady=(12, 8))

        def sidebtn(text):
            b = tk.Button(
                side_bottom,
                text=text,
                bg=self.palette["DARK2"],
                fg="white",
                bd=0,
                relief="flat",
                activebackground=self.palette["DARK"],
                activeforeground="white",
                padx=14,
                pady=10,
                font=("Segoe UI", 10, "bold"),
                anchor="w"
            )
            b.pack(fill="x", padx=10, pady=4)
            return b

        sidebtn("Administration")
        sidebtn("Avtal")
        sidebtn("Analys")
        sidebtn("Debitering")

        content = ttk.Frame(body)
        content.pack(side="left", fill="both", expand=True)

        head = ttk.Frame(content, padding=(14, 14, 14, 8))
        head.pack(fill="x")
        ttk.Label(head, text="BFUS", font=("Segoe UI", 12, "bold")).pack(side="left")
        ttk.Label(head, text="• Övergripande vy", foreground=self.palette["MUTED"]).pack(side="left", padx=(8, 0))

        card = ttk.LabelFrame(content, text="Övergripande uppgifter", padding=12)
        card.pack(fill="x", padx=14, pady=(0, 12))

        grid = ttk.Frame(card)
        grid.pack(fill="x")

        c1 = ttk.Frame(grid)
        c2 = ttk.Frame(grid)
        c3 = ttk.Frame(grid)
        c1.pack(side="left", fill="x", expand=True, padx=(0, 18))
        c2.pack(side="left", fill="x", expand=True, padx=(0, 18))
        c3.pack(side="left", fill="x", expand=True)

        r, e = make_labeled_entry(c1, "Tjänstenummer:")
        e.configure(textvariable=self.vars["tjanstenr"])
        r.pack(fill="x", pady=5)

        r, e = make_labeled_entry(c1, "Beskrivning:", width=30)
        e.configure(textvariable=self.vars["beskrivning"])
        r.pack(fill="x", pady=5)

        r, e = make_labeled_entry(c1, "Tjänstställenr:")
        e.configure(textvariable=self.vars["tjanstestalle"])
        r.pack(fill="x", pady=5)

        r, e = make_labeled_entry(c1, "Anslutningsnr:")
        e.configure(textvariable=self.vars["anslutningsnr"])
        r.pack(fill="x", pady=5)

        r = ttk.Frame(c2)
        ttk.Label(r, text="Affärsenhet:", width=18).pack(side="left")
        cb_aff = ttk.Combobox(r, values=["Region A", "Region B", "Region C"], state="readonly", width=24,
                              textvariable=self.vars["affarsenhet"])
        cb_aff.pack(side="left", fill="x", expand=True)
        r.pack(fill="x", pady=5)

        r = ttk.Frame(c2)
        ttk.Label(r, text="Tjänstestatus:", width=18).pack(side="left")
        cb_stat = ttk.Combobox(r, values=["Aktiv", "Planerad", "Avslutad"], state="readonly", width=24,
                               textvariable=self.vars["tjanstestatus"])
        cb_stat.pack(side="left", fill="x", expand=True)
        r.pack(fill="x", pady=5)

        r, e = make_labeled_entry(c2, "Anläggnings-id:")
        e.configure(textvariable=self.vars["anlaggnings_id"])
        r.pack(fill="x", pady=5)

        r, e = make_labeled_entry(c2, "Distrikt:")
        e.configure(textvariable=self.vars["distrikt"])
        r.pack(fill="x", pady=5)

        r, e = make_labeled_entry(c2, "Avläsningsbok:")
        e.configure(textvariable=self.vars["avlasningsbok"])
        r.pack(fill="x", pady=5)

        r, e = make_labeled_entry(c3, "Nätområde:")
        e.configure(textvariable=self.vars["natomrade"])
        r.pack(fill="x", pady=5)

        r, e = make_labeled_entry(c3, "Elområde:")
        e.configure(textvariable=self.vars["elomrade"])
        r.pack(fill="x", pady=5)

        r = ttk.Frame(c3)
        ttk.Label(r, text="Säkring:", width=18).pack(side="left")
        cb_sak = ttk.Combobox(r, values=["—", "16A", "20A", "25A", "35A", "50A"], state="readonly", width=24,
                              textvariable=self.vars["saking"])
        cb_sak.pack(side="left", fill="x", expand=True)
        r.pack(fill="x", pady=5)

        r, e = make_labeled_entry(c3, "Antal faser:")
        e.configure(textvariable=self.vars["antal_faser"])
        r.pack(fill="x", pady=5)

        r, e = make_labeled_entry(c3, "Spänning:")
        e.configure(textvariable=self.vars["spanning"])
        r.pack(fill="x", pady=5)

        nb = ttk.Notebook(content)
        nb.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        tabs = {}
        for name in ["Allmänt", "Avtal", "Aktörshistorik", "Installation", "Nyckelhantering", "AMM"]:
            frame = ttk.Frame(nb)
            nb.add(frame, text=name)
            tabs[name] = frame

        table_wrap = ttk.Frame(tabs["Allmänt"], padding=10)
        table_wrap.pack(fill="both", expand=True)

        cols = ("ID", "Typ", "Status", "Start", "Slut", "Notering")
        tree = ttk.Treeview(table_wrap, columns=cols, show="headings", height=12)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=120 if c != "Notering" else 300, anchor="w")
        tree.pack(side="left", fill="both", expand=True)

        ysb = ttk.Scrollbar(table_wrap, orient="vertical", command=tree.yview)
        tree.configure(yscroll=ysb.set)
        ysb.pack(side="right", fill="y")

        for row in [
            ("1001", "Händelse", "Klar", "2025-01-10", "", "Exempelnotering"),
            ("1002", "Händelse", "Pågår", "2025-01-12", "", "Exempelnotering"),
        ]:
            tree.insert("", "end", values=row)

        ttk.Label(tabs["Avtal"], text="(Simulerad vy) Avtalsinformation.", padding=14).pack(anchor="w")
        ttk.Label(tabs["Aktörshistorik"], text="(Simulerad vy) Historik för aktörer.", padding=14).pack(anchor="w")
        ttk.Label(tabs["Installation"], text="(Simulerad vy) Installationsinformation.", padding=14).pack(anchor="w")
        ttk.Label(tabs["Nyckelhantering"], text="(Simulerad vy) Nyckelhantering.", padding=14).pack(anchor="w")
        ttk.Label(tabs["AMM"], text="(Simulerad vy) AMM-data.", padding=14).pack(anchor="w")

        status = tk.Frame(self, bg=self.palette["SIDELITE"], height=36)
        status.pack(fill="x")
        status.pack_propagate(False)
        tk.Label(status, text="Redo", bg=self.palette["SIDELITE"], fg=self.palette["MUTED"]).pack(side="left", padx=12)
        tk.Label(status, text="F1 = Hjälp", bg=self.palette["SIDELITE"], fg=self.palette["MUTED"]).pack(side="right", padx=12)

    def open_search(self):
        SearchServiceWindow(self, self.palette)

    def open_agreement(self):
        # Öppnar wizard för "Skapa avtal" (simulerad)
        initial = {"kundnummer": "K-000001"}
        AgreementWizard(self, self.palette, initial=initial)

    def save(self):
        messagebox.showinfo("BFUS", "Sparat (simulerat).")

if __name__ == "__main__":
    BFUSApp().mainloop()
