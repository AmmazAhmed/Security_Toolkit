# ──────────────────────────────────────────────────────────
#  SECURE MESSAGING MODULE
# ──────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import messagebox
import json
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import base64
from modules.config import C, dp, section_title, separator, scrolled_out, styled_entry, styled_btn

def make_key(password: str, salt: bytes = None):
    if salt is None:
        salt = os.urandom(16)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32,
                     salt=salt, iterations=100_000)
    return base64.urlsafe_b64encode(kdf.derive(password.encode())), salt

class SecureMessaging:
    def __init__(self, parent, username, password):
        self.parent = parent
        self.username = username
        self.password = password
        self.msgs_file = dp("messages.txt")
        self.messages = self._load()
        self._build()

    def _load(self):
        if os.path.exists(self.msgs_file):
            try:
                with open(self.msgs_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save(self):
        with open(self.msgs_file, "w") as f:
            json.dump(self.messages, f, indent=2)

    def _enc(self, text):
        key, salt = make_key(self.password)
        return Fernet(key).encrypt(text.encode()).decode(), salt.hex()

    def _dec(self, enc, salt_hex):
        try:
            key, _ = make_key(self.password, bytes.fromhex(salt_hex))
            return Fernet(key).decrypt(enc.encode()).decode()
        except Exception:
            return "[🔒 Cannot decrypt]"

    def _build(self):
        for w in self.parent.winfo_children():
            w.destroy()
        section_title(self.parent, "💬  Secure Messaging", C["accent2"])
        tk.Label(self.parent, text=f"  Logged in as: {self.username}",
                 font=("Consolas", 8), bg=C["card"], fg=C["muted"]).pack(anchor="w", padx=22)
        separator(self.parent)

        self.chat = scrolled_out(self.parent, height=16, fg=C["accent2"])
        self.chat.pack(padx=16, pady=4, fill="x")

        inp = tk.Frame(self.parent, bg=C["card"])
        inp.pack(padx=16, pady=6, fill="x")
        self.msg_e = styled_entry(inp, width=50)
        self.msg_e.pack(side="left", padx=(0, 8))
        styled_btn(inp, "Send 🔒", self._send, color=C["accent2"], fg="black", width=10).pack(side="left")

        bf = tk.Frame(self.parent, bg=C["card"])
        bf.pack(padx=16, pady=4)
        styled_btn(bf, "📜 History", self._view, color=C["card2"], width=13).pack(side="left", padx=4)
        styled_btn(bf, "🔓 Raw Data", self._raw, color=C["card2"], width=13).pack(side="left", padx=4)
        styled_btn(bf, "🗑 Clear All", self._clear, color=C["danger"], width=13).pack(side="left", padx=4)
        self._view()

    def _send(self):
        t = self.msg_e.get().strip()
        if not t:
            return
        enc, salt = self._enc(t)
        self.messages.append({"from": self.username, "enc": enc, "salt": salt})
        self._save()
        self.msg_e.delete(0, tk.END)
        self._view()

    def _view(self):
        self.chat.config(state="normal")
        self.chat.delete("1.0", tk.END)
        for m in self.messages:
            txt = self._dec(m["enc"], m["salt"])
            self.chat.insert(tk.END, f"  [{m['from']}]  {txt}\n")
        self.chat.config(state="disabled")
        self.chat.see(tk.END)

    def _raw(self):
        self.chat.config(state="normal")
        self.chat.delete("1.0", tk.END)
        self.chat.insert(tk.END, "── RAW ENCRYPTED RECORDS ──\n\n")
        for m in self.messages:
            self.chat.insert(tk.END, f"  from : {m['from']}\n  data : {m['enc'][:64]}…\n\n")
        self.chat.config(state="disabled")

    def _clear(self):
        if messagebox.askyesno("Clear", "Delete all messages?"):
            self.messages = []
            self._save()
            self._view()

    def get_messages(self):
        """For admin access"""
        result = []
        for m in self.messages:
            result.append({
                "from": m["from"],
                "decrypted": self._dec(m["enc"], m["salt"])
            })
        return result