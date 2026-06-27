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

    # Caesar
    def _caesar_ui(self, f):
        tk.Label(f, text="Shifts each letter by a fixed number (0-25).", font=("Consolas", 9), bg=C["card"], fg=C["muted"]).pack(pady=6)
        r1 = tk.Frame(f, bg=C["card"])
        r1.pack(pady=4)
        tk.Label(r1, text="Shift Key:", font=("Consolas", 10), bg=C["card"], fg=C["text"]).pack(side="left", padx=6)
        self.ck = styled_entry(r1, width=5)
        self.ck.insert(0, "3")
        self.ck.pack(side="left")
        self.cm = tk.StringVar(value="encrypt")
        r2 = tk.Frame(f, bg=C["card"])
        r2.pack(pady=4)
        for val, lbl in [("encrypt", "Encrypt →"), ("decrypt", "← Decrypt")]:
            tk.Radiobutton(r2, text=lbl, variable=self.cm, value=val, bg=C["card"], fg=C["text"],
                           selectcolor=C["card2"], activebackground=C["card"], font=("Consolas", 10)).pack(side="left", padx=12)
        tk.Label(f, text="Input Text:", font=("Consolas", 9), bg=C["card"], fg=C["muted"]).pack(anchor="w")
        self.cin = tk.Text(f, width=56, height=4, bg=C["entry"], fg=C["entry_fg"], insertbackground=C["accent"],
                           font=("Consolas", 11), relief="flat", highlightthickness=1, highlightbackground=C["border"])
        self.cin.pack(pady=4)
        styled_btn(f, "▶ Run Caesar", self._run_c, color=C["accent"], width=18).pack(pady=6)
        self.cout = scrolled_out(f, height=5, fg=C["accent"])
        self.cout.pack()

    def _run_c(self):
        try:
            sh = int(self.ck.get().strip())
            if not (0 <= sh <= 25):
                raise ValueError
        except ValueError:
            messagebox.showwarning("Key Error", "Shift must be 0-25")
            return
        t = self.cin.get("1.0", tk.END).strip()
        if not t:
            return
        d = sh if self.cm.get() == "encrypt" else -sh
        res = "".join(chr((ord(c) - (ord('A') if c.isupper() else ord('a')) + d) % 26 + (ord('A') if c.isupper() else ord('a'))) if c.isalpha() else c for c in t)
        self.cout.config(state="normal")
        self.cout.delete("1.0", tk.END)
        self.cout.insert(tk.END, f"[{self.cm.get().upper()} | shift={sh}]\n{res}")
        self.cout.config(state="disabled")



