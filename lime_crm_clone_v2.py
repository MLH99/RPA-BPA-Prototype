import tkinter as tk
from tkinter import ttk, messagebox

# ----------------------
# Actions (simulated)
# ----------------------
def save_case():
    messagebox.showinfo("CRM", "Ärendet har sparats (simulerat).")

def duplicate_case():
    messagebox.showinfo("CRM", "Kopia skapad (simulerat).")

def open_elsmart():
    messagebox.showinfo("CRM", "Öppnar Elsmartärende (simulerat).")

# ----------------------
# Window
# ----------------------
root = tk.Tk()
root.title("CRM Ärendehantering")
root.geometry("1200x750")
root.minsize(1100, 680)

# ----------------------
# Colors
# ----------------------
C_TOPBAR = "#6b5bd2"          # purple-ish like screenshot
C_RIGHT_BG = "#eef3f9"
C_LEFT_BG = "#dfe8f5"
C_GREEN = "#41b34a"
C_BLUE = "#2f6fb3"
C_ORANGE = "#f39c34"
C_WHITE = "#ffffff"
C_TEXT_WHITE = "#ffffff"

# ----------------------
# Top bar
# ----------------------
top = tk.Frame(root, bg=C_TOPBAR, height=44)
top.pack(fill="x")
top.pack_propagate(False)

btn_style = dict(relief="flat", bd=0, padx=12, pady=6, font=("Segoe UI", 10, "bold"))

tk.Button(top, text="Spara och stäng", command=save_case, **btn_style).pack(side="left", padx=(10, 6), pady=6)
tk.Button(top, text="Spara", command=save_case, **btn_style).pack(side="left", padx=6, pady=6)
tk.Button(top, text="Skapa kopia", command=duplicate_case, **btn_style).pack(side="left", padx=6, pady=6)

# Simple nav icons placeholders (so RPA can click)
tk.Button(top, text="◀", **btn_style).pack(side="left", padx=(18, 6), pady=6)
tk.Button(top, text="▶", **btn_style).pack(side="left", padx=6, pady=6)

# ----------------------
# Main
# ----------------------
main = tk.Frame(root)
main.pack(fill="both", expand=True)

# ----------------------
# Left panel (like screenshot: green header + action buttons + checklist in white)
# ----------------------
left = tk.Frame(main, width=290, bg=C_LEFT_BG)
left.pack(side="left", fill="y")
left.pack_propagate(False)

# Header block
hdr = tk.Frame(left, bg="#95c93d", height=170)
hdr.pack(fill="x")
hdr.pack_propagate(False)

# Plus icon circle (approx)
canvas = tk.Canvas(hdr, width=80, height=80, bg="#95c93d", highlightthickness=0)
canvas.place(x=100, y=20)
canvas.create_oval(10, 10, 70, 70, fill="#7fbf2c", outline="#7fbf2c")
canvas.create_text(40, 40, text="+", fill="white", font=("Segoe UI", 26, "bold"))

# Case summary text (left)
info = tk.Frame(left, bg="#95c93d")
info.pack(fill="x")
# Generiska demo-värden (lätt att kopiera för RPA)
tk.Label(info, text="Tjänstenummer", bg="#95c93d", fg="white", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=12, pady=(8, 0))
tjanstenr_var = tk.StringVar(value="445323")
tjanstenr_entry = ttk.Entry(info, textvariable=tjanstenr_var, width=18, font=("Segoe UI", 14, "bold"))
tjanstenr_entry.pack(anchor="w", padx=12, pady=(2, 6))
# Kundnummer (för BFUS-avtal)
tk.Label(info, text="Kundnummer", bg="#95c93d", fg="white", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=12, pady=(2, 0))
kundnr_var = tk.StringVar(value="K-000001")
kundnr_entry = ttk.Entry(info, textvariable=kundnr_var, width=18, font=("Segoe UI", 12, "bold"))
kundnr_entry.pack(anchor="w", padx=12, pady=(2, 6))
# Kontakt (generisk)
tk.Label(info, text="Kontakt: Exempelperson\nTel: 000-000000\nexempel@organisation.se", bg="#95c93d", fg="white", justify="left", font=("Segoe UI", 10)).pack(anchor="w", padx=12, pady=(2, 10))

# Action buttons area
actions = tk.Frame(left, bg=C_LEFT_BG)
actions.pack(fill="x", padx=10, pady=12)

def padded_button(parent, text, bg, fg, command=None, white_outer=False):
    """
    white_outer=True => creates a white padding border like screenshot for the green action.
    """
    outer_bg = C_WHITE if white_outer else parent["bg"]
    outer = tk.Frame(parent, bg=outer_bg)
    outer.pack(fill="x", pady=10)  # ~10px vertical padding between buttons
    # inner padding to look like "white border"
    inner_pad = 6 if white_outer else 0
    inner = tk.Frame(outer, bg=outer_bg, padx=inner_pad, pady=inner_pad)
    inner.pack(fill="x")
    btn = tk.Button(
        inner,
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        activebackground=bg,
        activeforeground=fg,
        relief="flat",
        bd=0,
        padx=12,
        pady=10,            # >10px padding as requested
        font=("Segoe UI", 10, "bold"),
    )
    btn.pack(fill="x")
    return btn

# Requested changes
padded_button(actions, "✓ Pricka av", bg=C_GREEN, fg="white", white_outer=True, command=lambda: [v.set(True) for v in chk_vars])
padded_button(actions, "➕ Lägg till notering", bg=C_BLUE, fg="white")
padded_button(actions, "📞 Skicka SMS", bg=C_ORANGE, fg="white")
padded_button(actions, "📂 Öppna Elsmartärende", bg=C_BLUE, fg="white", command=open_elsmart)

# Checklist in white box with blue header text
check_wrap = tk.Frame(left, bg=C_LEFT_BG)
check_wrap.pack(fill="both", expand=True, padx=10, pady=(6, 10))

check_box = tk.Frame(check_wrap, bg=C_WHITE, bd=1, relief="solid")
check_box.pack(fill="both", expand=True)

tk.Label(check_box, text="Checklista", bg=C_WHITE, fg=C_BLUE, font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=10, pady=(10, 6))

chk_items = [
    "Mätaren monteras",
    "El Smart rapporteras",
    "AO i besiktningsprotokoll",
    "Notera i beskrivningsfält",
    "Uppdatera FiM",
]
chk_vars = []
for item in chk_items:
    v = tk.BooleanVar(value=False)
    chk_vars.append(v)
    tk.Checkbutton(
        check_box, text=item, variable=v,
        bg=C_WHITE, fg="#1b1b1b",
        activebackground=C_WHITE,
        selectcolor=C_WHITE,
        anchor="w"
    ).pack(fill="x", padx=10, pady=2)

# ----------------------
# Right panel
# ----------------------
right = tk.Frame(main, bg=C_RIGHT_BG)
right.pack(side="left", fill="both", expand=True)

# Form grid
form = tk.Frame(right, bg=C_RIGHT_BG)
form.pack(padx=15, pady=10, fill="x")

def label_widget(parent, txt):
    return tk.Label(parent, text=txt, bg=C_RIGHT_BG, fg="#1b1b1b", font=("Segoe UI", 9))

def entry_widget(parent, width=30):
    e = ttk.Entry(parent, width=width)
    return e

def combobox_widget(parent, values, width=28):
    cb = ttk.Combobox(parent, values=values, width=width, state="readonly")
    if values:
        cb.current(0)
    return cb

def add_field(row, col, label, widget):
    label_widget(form, label).grid(row=row, column=col*2, sticky="w", padx=6, pady=(4, 2))
    widget.grid(row=row, column=col*2+1, sticky="w", padx=6, pady=(2, 6))
    return widget

# Row 0
add_field(0, 0, "Ärendenr", entry_widget(form))
add_field(0, 1, "Registrerat av", entry_widget(form))

# Row 1 (Inkommit via must be a menu box w/ Elsmart selected)
incoming = combobox_widget(form, ["Elsmart", "E-post", "Telefon", "Portal"], width=28)
add_field(1, 0, "Inkommit via", incoming)
add_field(1, 1, "Ärendetyp", combobox_widget(form, ["Nyanslutning LSP (Process)", "Support", "Felanmälan"], width=28))

# Row 2
add_field(2, 0, "Ansvarig", combobox_widget(form, ["Exempel Handläggare", "Exempel Handläggare 2", "—"], width=28))
add_field(2, 1, "Prioritet", combobox_widget(form, ["Normal", "Hög", "Låg"], width=28))

# Row 3
add_field(3, 0, "Kund", entry_widget(form))
add_field(3, 1, "Kontaktperson", entry_widget(form))

# Row 4
add_field(4, 0, "E-post", entry_widget(form))
add_field(4, 1, "Mobilnr", entry_widget(form))

# Row 5
add_field(5, 0, "Fastighet", entry_widget(form))
add_field(5, 1, "Tjänst", entry_widget(form))

# Description area (left large + right "Viktig information" like screenshot)
mid = tk.Frame(right, bg=C_RIGHT_BG)
mid.pack(fill="both", expand=True, padx=15, pady=(0, 10))

desc_col = tk.Frame(mid, bg=C_RIGHT_BG)
desc_col.pack(side="left", fill="both", expand=True)

info_col = tk.Frame(mid, bg=C_RIGHT_BG, width=260)
info_col.pack(side="left", fill="y", padx=(12, 0))
info_col.pack_propagate(False)

tk.Label(desc_col, text="Beskrivning", bg=C_RIGHT_BG, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=6, pady=(2, 4))
desc_text = tk.Text(desc_col, height=14)
desc_text.pack(fill="both", expand=True, padx=6)

tk.Label(info_col, text="Viktig information", bg=C_RIGHT_BG, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=6, pady=(2, 4))
important = tk.Text(info_col, height=14)
important.pack(fill="both", expand=True, padx=6)

# Status bar bottom
status = tk.Frame(right, bg="#dde6f2", height=36)
status.pack(fill="x", side="bottom")
status.pack_propagate(False)

ttk.Label(status, text="Status: Påbörjat").pack(side="left", padx=12)
ttk.Label(status, text="Deadline: 2025-02-01").pack(side="right", padx=12)

root.mainloop()