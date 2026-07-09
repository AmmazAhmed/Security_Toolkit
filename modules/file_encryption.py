# ──────────────────────────────────────────────────────────
#  FILE ENCRYPTION MODULE
# ──────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from cryptography.fernet import Fernet
from modules.config import C, section_title, separator, scrolled_out, styled_entry, styled_btn
from modules.messaging import make_key

class FileEncryptionTool:
    def __init__(self, parent):
        self.parent = parent
        self.file = None
        self._build()

    def _build(self):
        for w in self.parent.winfo_children():
            w.destroy()
        section_title(self.parent, "🗄️  File Encryption", C["accent3"])
        tk.Label(self.parent, text="  Encrypt any file with a password.",
                 font=("Consolas", 9), bg=C["card"], fg=C["muted"]).pack(anchor="w", padx=22)
        separator(self.parent)

        ff = tk.Frame(self.parent, bg=C["card"])
        ff.pack(padx=16, pady=8)
        self.flbl = tk.Label(ff, text="No file selected", font=("Consolas", 9), bg=C["entry"], fg=C["muted"],
                             width=50, anchor="w", padx=8, pady=6, highlightthickness=1, highlightbackground=C["border"])
        self.flbl.grid(row=0, column=0, padx=(0, 8))
        styled_btn(ff, "📂 Browse", self._browse, color=C["card2"], width=10).grid(row=0, column=1)

        tk.Label(self.parent, text="Encryption Password:", font=("Consolas", 9), bg=C["card"], fg=C["muted"]).pack(anchor="w", padx=22)
        self.pw = styled_entry(self.parent, width=36, show="●")
        self.pw.pack(padx=22, pady=6, anchor="w")

        bf = tk.Frame(self.parent, bg=C["card"])
        bf.pack(padx=16, pady=10)
        styled_btn(bf, "🔒 ENCRYPT", self._enc, color=C["accent3"], width=16).pack(side="left", padx=6)
        styled_btn(bf, "🔓 DECRYPT", self._dec, color=C["accent2"], fg="black", width=16).pack(side="left", padx=6)

        self.log_box = scrolled_out(self.parent, height=12)
        self.log_box.pack(padx=16, pady=8)
        self._log("✅ Ready. Select a file, enter password, then Encrypt or Decrypt.")

    def _browse(self):
        p = filedialog.askopenfilename()
        if p:
            self.file = p
            self.flbl.config(text=os.path.basename(p), fg=C["text"])
            self._log(f"📄 Selected: {p}")

    def _log(self, m):
        self.log_box.config(state="normal")
        self.log_box.insert(tk.END, m + "\n")
        self.log_box.see(tk.END)
        self.log_box.config(state="disabled")

    def _enc(self):
        if not self.file:
            messagebox.showwarning("No File", "Browse a file first!")
            return
        pw = self.pw.get().strip()
        if not pw:
            messagebox.showwarning("No Password", "Enter a password!")
            return
        try:
            with open(self.file, "rb") as f:
                data = f.read()
            key, salt = make_key(pw)
            enc = Fernet(key).encrypt(data)
            ep = self.file + ".enc"
            sp = self.file + ".salt"
            with open(ep, "wb") as f:
                f.write(enc)
            with open(sp, "wb") as f:
                f.write(salt)
            self._log(f"\n✅ Encrypted → {os.path.basename(ep)}\n")
        except Exception as e:
            self._log(f"❌ Error: {e}")

    def _dec(self):
        if not self.file:
            messagebox.showwarning("No File", "Browse a .enc file first!")
            return
        if not self.file.endswith(".enc"):
            messagebox.showwarning("Wrong Type", "Select a .enc file!")
            return
        pw = self.pw.get().strip()
        sp = self.file.replace(".enc", ".salt")
        if not os.path.exists(sp):
            messagebox.showerror("Missing Salt", f"Salt file not found:\n{sp}")
            return
        try:
            with open(self.file, "rb") as f:
                enc = f.read()
            with open(sp, "rb") as f:
                salt = f.read()
            key, _ = make_key(pw, salt)
            dec = Fernet(key).decrypt(enc)
            out = self.file[:-4]
            if os.path.exists(out):
                out += "_decrypted"
            with open(out, "wb") as f:
                f.write(dec)
            self._log(f"\n✅ Decrypted → {os.path.basename(out)}\n")
        except Exception:
            self._log("❌ Decryption failed — wrong password or corrupted file.")