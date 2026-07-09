# ──────────────────────────────────────────────────────────
#  PASSWORD MANAGER MODULE
# ──────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import random
import string
from cryptography.fernet import Fernet
from modules.config import C, dp, section_title, separator, scrolled_out, styled_entry, styled_btn, label
from modules.auth import _load_users, _save_users

class PasswordManager:
    def __init__(self, parent):
        self.parent = parent
        self.vault_file = dp("vault.enc")
        self.salt_file = dp("vault.salt")
        self.master_key = None
        self.vault = {"credentials": [], "notes": []}
        self._build_lock()

    def _save_vault(self):
        enc = Fernet(self.master_key).encrypt(json.dumps(self.vault).encode())
        with open(self.vault_file, "wb") as f:
            f.write(enc)

    def _build_lock(self):
        for w in self.parent.winfo_children():
            w.destroy()
        section_title(self.parent, "🔑  Password Manager", C["gold"])
        separator(self.parent)

        mid = tk.Frame(self.parent, bg=C["card"])
        mid.pack(pady=30)
        label(mid, "Master Password:", font_size=11, color=C["text"])
        self.mp = styled_entry(mid, width=30, show="●")
        self.mp.pack(pady=8)
        bf = tk.Frame(mid, bg=C["card"])
        bf.pack()
        styled_btn(bf, "🔓 Unlock", self._unlock, color=C["gold"], fg="black", width=12).pack(side="left", padx=6)
        styled_btn(bf, "🆕 New Vault", self._create, color=C["card2"], width=13).pack(side="left", padx=6)
        self.st = tk.Label(mid, text="", font=("Consolas", 9), bg=C["card"], fg=C["danger"])
        self.st.pack(pady=6)

    def _create(self):
        pw = self.mp.get().strip()
        if len(pw) < 6:
            self.st.config(text="✗ Min 6 chars required", fg=C["danger"])
            return
        from modules.messaging import make_key
        key, salt = make_key(pw)
        self.master_key = key
        with open(self.salt_file, "wb") as f:
            f.write(salt)
        self.vault = {"credentials": [], "notes": []}
        self._save_vault()
        self.st.config(text="✓ Vault created — now unlock it", fg=C["success"])

    def _unlock(self):
        pw = self.mp.get().strip()
        if not os.path.exists(self.vault_file):
            self.st.config(text="✗ No vault found — create one first", fg=C["danger"])
            return
        try:
            with open(self.salt_file, "rb") as f:
                salt = f.read()
            from modules.messaging import make_key
            key, _ = make_key(pw, salt)
            with open(self.vault_file, "rb") as f:
                enc = f.read()
            self.vault = json.loads(Fernet(key).decrypt(enc).decode())
            self.master_key = key
            self._build_vault()
        except Exception:
            self.st.config(text="✗ Wrong master password!", fg=C["danger"])

    def _build_vault(self):
        for w in self.parent.winfo_children():
            w.destroy()
        section_title(self.parent, "🔑  Password Vault  (Unlocked)", C["gold"])
        separator(self.parent)

        nb = ttk.Notebook(self.parent)
        nb.pack(fill="both", expand=True, padx=12, pady=6)

        ct = tk.Frame(nb, bg=C["card"])
        nb.add(ct, text="  🔑 Passwords  ")
        self._cred_tab(ct)

        nt = tk.Frame(nb, bg=C["card"])
        nb.add(nt, text="  📝 Notes  ")
        self._notes_tab(nt)

        gt = tk.Frame(nb, bg=C["card"])
        nb.add(gt, text="  ⚡ Generator  ")
        self._gen_tab(gt)

        styled_btn(self.parent, "🔒 Lock Vault", self._build_lock, color=C["danger"], width=18).pack(pady=8)

    def _cred_tab(self, f):
        box = tk.LabelFrame(f, text=" Add Credential ", bg=C["card"], fg=C["gold"],
                            font=("Consolas", 9, "bold"), bd=1, highlightbackground=C["border"])
        box.pack(fill="x", padx=14, pady=8)
        self._c = {}
        for i, (lbl, show) in enumerate([("Website", ""), ("Username", ""), ("Password", "●")]):
            tk.Label(box, text=lbl, font=("Consolas", 9), bg=C["card"], fg=C["muted"], width=10).grid(row=i, column=0, sticky="e", padx=6, pady=4)
            e = styled_entry(box, width=30, show=show)
            e.grid(row=i, column=1, padx=6, pady=4)
            self._c[lbl] = e
        styled_btn(box, "💾 Save", self._save_cred, color=C["gold"], fg="black", width=10).grid(row=3, column=1, sticky="e", pady=6)

        tk.Label(f, text="Saved credentials:", font=("Consolas", 9), bg=C["card"], fg=C["muted"]).pack(anchor="w", padx=14)
        self.clist = tk.Listbox(f, bg=C["entry"], fg=C["gold"], font=("Consolas", 10), height=8, width=62,
                                selectbackground=C["accent"], relief="flat", highlightthickness=1, highlightbackground=C["border"])
        self.clist.pack(padx=14, pady=4)

        bf = tk.Frame(f, bg=C["card"])
        bf.pack(pady=4)
        styled_btn(bf, "👁 View", self._view_cred, color=C["card2"], width=12).pack(side="left", padx=4)
        styled_btn(bf, "🗑 Delete", self._del_cred, color=C["danger"], width=12).pack(side="left", padx=4)
        self._refresh_creds()

    def _save_cred(self):
        s = self._c["Website"].get().strip()
        u = self._c["Username"].get().strip()
        p = self._c["Password"].get().strip()
        if not s or not u or not p:
            messagebox.showwarning("Missing", "Fill all fields!")
            return
        self.vault["credentials"].append({"site": s, "user": u, "pass": p})
        self._save_vault()
        self._refresh_creds()
        for e in self._c.values():
            e.delete(0, tk.END)

    def _refresh_creds(self):
        self.clist.delete(0, tk.END)
        for c in self.vault["credentials"]:
            self.clist.insert(tk.END, f"  {c['site']}  |  {c['user']}")

    def _view_cred(self):
        s = self.clist.curselection()
        if not s:
            messagebox.showinfo("Select", "Click a row first")
            return
        c = self.vault["credentials"][s[0]]
        messagebox.showinfo("Credential", f"Website  : {c['site']}\nUsername : {c['user']}\nPassword : {c['pass']}")

    def _del_cred(self):
        s = self.clist.curselection()
        if not s:
            return
        if messagebox.askyesno("Delete", "Remove this credential?"):
            self.vault["credentials"].pop(s[0])
            self._save_vault()
            self._refresh_creds()

    def _notes_tab(self, f):
        tk.Label(f, text="New secure note:", font=("Consolas", 9), bg=C["card"], fg=C["muted"]).pack(anchor="w", padx=14, pady=(8, 2))
        self.note_in = tk.Text(f, width=60, height=5, bg=C["entry"], fg=C["entry_fg"],
                               insertbackground=C["accent"], font=("Consolas", 10), relief="flat",
                               highlightthickness=1, highlightbackground=C["border"])
        self.note_in.pack(padx=14, pady=4)
        styled_btn(f, "💾 Save Note", self._save_note, color=C["gold"], fg="black", width=16).pack(pady=4)
        self.notes_out = scrolled_out(f, height=8, fg=C["muted"])
        self.notes_out.pack(padx=14)
        self._refresh_notes()

    def _save_note(self):
        n = self.note_in.get("1.0", tk.END).strip()
        if not n:
            return
        self.vault["notes"].append(n)
        self._save_vault()
        self.note_in.delete("1.0", tk.END)
        self._refresh_notes()

    def _refresh_notes(self):
        self.notes_out.config(state="normal")
        self.notes_out.delete("1.0", tk.END)
        for i, n in enumerate(self.vault["notes"], 1):
            self.notes_out.insert(tk.END, f"[{i}]  {n}\n{'─'*48}\n")
        self.notes_out.config(state="disabled")

    def _gen_tab(self, f):
        tk.Label(f, text="⚡  Strong Password Generator", font=("Consolas", 13, "bold"),
                 bg=C["card"], fg=C["gold"]).pack(pady=14)
        tk.Label(f, text="Length:", font=("Consolas", 10), bg=C["card"], fg=C["text"]).pack()
        self.glen = tk.IntVar(value=18)
        tk.Scale(f, from_=8, to=40, orient="horizontal", variable=self.glen, bg=C["card"],
                 fg=C["text"], troughcolor=C["card2"], highlightthickness=0, length=280).pack()
        self.sym = tk.BooleanVar(value=True)
        self.nums = tk.BooleanVar(value=True)
        for txt, var in [("Include Symbols  !@#$", self.sym), ("Include Numbers  0-9", self.nums)]:
            tk.Checkbutton(f, text=txt, variable=var, bg=C["card"], fg=C["text"],
                           selectcolor=C["card2"], activebackground=C["card"], font=("Consolas", 10)).pack()
        styled_btn(f, "🔀 Generate", self._gen, color=C["gold"], fg="black", width=18).pack(pady=10)
        self.gout = styled_entry(f, width=40)
        self.gout.pack()
        styled_btn(f, "📋 Copy", self._copy_gen, color=C["card2"], width=14).pack(pady=6)

    def _gen(self):
        ch = string.ascii_letters
        if self.nums.get():
            ch += string.digits
        if self.sym.get():
            ch += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        pw = "".join(random.choice(ch) for _ in range(self.glen.get()))
        self.gout.delete(0, tk.END)
        self.gout.insert(0, pw)

    def _copy_gen(self):
        pw = self.gout.get()
        if pw:
            self.parent.clipboard_clear()
            self.parent.clipboard_append(pw)
            messagebox.showinfo("Copied", "Password copied to clipboard!")

    def get_vault_data(self):
        """For admin access"""
        return self.vault