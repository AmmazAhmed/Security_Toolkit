import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import os
from modules.config import C, section_title, separator, scrolled_out, styled_entry, styled_btn

KEYS_TXT = os.path.join("toolkit_data", "cipher_keys.txt")
os.makedirs("toolkit_data", exist_ok=True)

def _load_ck():
    keys = {}
    if os.path.exists(KEYS_TXT):
        with open(KEYS_TXT, "r") as f:
            for line in f:
                line = line.strip()
                if "|" in line:
                    lbl, k = line.split("|", 1)
                    keys[lbl] = k
    return keys

def _save_ck(keys):
    with open(KEYS_TXT, "w") as f:
        for lbl, k in keys.items():
            f.write(f"{lbl}|{k}\n")

class CipherToolkit:
    CIPHERS = ["Caesar Cipher", "Beaufort Cipher  (brute-force decrypt)", "Random Key Cipher  (Vigenère)"]
    EF = {'E': 12.70, 'T': 9.06, 'A': 8.17, 'O': 7.51, 'I': 6.97, 'N': 6.75,
          'S': 6.33, 'H': 6.09, 'R': 5.99, 'D': 4.25, 'L': 4.03, 'C': 2.78,
          'U': 2.76, 'M': 2.41, 'W': 2.36, 'F': 2.23, 'G': 2.02, 'Y': 1.97,
          'P': 1.93, 'B': 1.29, 'V': 0.98, 'K': 0.77, 'J': 0.15, 'X': 0.15,
          'Q': 0.10, 'Z': 0.07}

    def __init__(self, parent):
        self.parent = parent
        self.keys = _load_ck()
        self._build()

    def _build(self):
        for w in self.parent.winfo_children():
            w.destroy()
        section_title(self.parent, "🔡  Cipher Toolkit", C["accent"])
        hdr = tk.Frame(self.parent, bg=C["card"])
        hdr.pack(fill="x", padx=16, pady=6)
        tk.Label(hdr, text="Select Cipher:", font=("Consolas", 11), bg=C["card"], fg=C["text"]).pack(side="left", padx=(0, 10))
        self.cv = tk.StringVar(value=self.CIPHERS[0])
        cb = ttk.Combobox(hdr, textvariable=self.cv, values=self.CIPHERS, state="readonly", width=42, font=("Consolas", 10))
        cb.pack(side="left")
        cb.bind("<<ComboboxSelected>>", lambda _: self._refresh())
        separator(self.parent)
        self.work = tk.Frame(self.parent, bg=C["card"])
        self.work.pack(fill="both", expand=True, padx=16, pady=4)
        self._refresh()

    def _refresh(self):
        for w in self.work.winfo_children():
            w.destroy()
        c = self.cv.get()
        if "Caesar" in c:
            self._caesar_ui(self.work)
        elif "Beaufort" in c:
            self._beaufort_ui(self.work)
        else:
            self._rk_ui(self.work)
