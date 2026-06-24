import tkinter as tk
from tkinter import scrolledtext
import os

# Colour palette
C = {
    "bg": "#0e0e1a",
    "panel": "#13131f",
    "card": "#1a1a2e",
    "card2": "#1f1f35",
    "sidebar": "#0b0b16",
    "accent": "#6c63ff",
    "accent2": "#00d4aa",
    "accent3": "#ff6b6b",
    "gold": "#ffd700",
    "text": "#e0e0f0",
    "muted": "#7070a0",
    "border": "#2a2a45",
    "success": "#00ff88",
    "warning": "#ff9f43",
    "danger": "#ff4757",
    "entry": "#0d0d1a",
    "entry_fg": "#c8c8ff",
}


# Data directory
DATA_DIR = "toolkit_data"
os.makedirs(DATA_DIR, exist_ok=True)

def dp(filename):
    return os.path.join(DATA_DIR, filename)

# Shared widget helpers
def label(parent, text, font_size=10, bold=False, color=None, **kw):
    f = ("Consolas", font_size, "bold" if bold else "normal")
    return tk.Label(parent, text=text, font=f,
                    bg=kw.pop("bg", C["card"]),
                    fg=color or C["text"], **kw)

def styled_entry(parent, width=30, show="", **kw):
    return tk.Entry(parent, width=width, show=show,
                    bg=C["entry"], fg=C["entry_fg"],
                    insertbackground=C["accent"],
                    relief="flat", bd=0,
                    highlightthickness=1,
                    highlightbackground=C["border"],
                    highlightcolor=C["accent"],
                    font=("Consolas", 11), **kw)

def styled_btn(parent, text, command, color=None, fg="white", width=14, **kw):
    bg = color or C["accent"]
    b = tk.Button(parent, text=text, command=command,
                  bg=bg, fg=fg, relief="flat", bd=0,
                  activebackground=C["card2"],
                  activeforeground=C["accent"],
                  font=("Consolas", 10, "bold"),
                  cursor="hand2", width=width,
                  padx=8, pady=6, **kw)
    b.bind("<Enter>", lambda e: b.config(bg=C["card2"]))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b

def section_title(parent, text, color=None):
    f = tk.Frame(parent, bg=C["card"])
    f.pack(fill="x", padx=18, pady=(14, 4))
    tk.Frame(f, bg=color or C["accent"], width=4).pack(side="left", fill="y")
    tk.Label(f, text=f"  {text}", font=("Consolas", 13, "bold"),
             bg=C["card"], fg=color or C["accent"]).pack(side="left", pady=4)

def separator(parent):
    tk.Frame(parent, bg=C["border"], height=1).pack(fill="x", padx=16, pady=6)

def scrolled_out(parent, height=10, fg=None):
    return scrolledtext.ScrolledText(
        parent, width=62, height=height,
        bg=C["entry"], fg=fg or C["accent2"],
        font=("Consolas", 9), state="disabled",
        relief="flat", bd=0,
        highlightthickness=1,
        highlightbackground=C["border"])