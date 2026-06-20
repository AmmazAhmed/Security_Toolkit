# ──────────────────────────────────────────────────────────
#  ADMIN PANEL MODULE - View all users and their data
# ──────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
from modules.config import C, section_title, separator, scrolled_out, styled_btn
from modules.auth import _load_users, USERS_TXT
from modules.messaging import SecureMessaging

ADMIN_USER = "admin"
ADMIN_PASS_HASH = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"  

class AdminPanel:
    def __init__(self, parent, current_user):
        self.parent = parent
        self.current_user = current_user
        self._check_admin()

    def _check_admin(self):
        if self.current_user != ADMIN_USER:
            for w in self.parent.winfo_children():
                w.destroy()
            section_title(self.parent, "👑  Admin Panel", C["danger"])
            tk.Label(self.parent, text="⛔  ACCESS DENIED", font=("Consolas", 20, "bold"),
                     bg=C["card"], fg=C["danger"]).pack(pady=50)
            tk.Label(self.parent, text="This area is for administrators only.",
                     font=("Consolas", 12), bg=C["card"], fg=C["muted"]).pack()
            return
        self._build()

    def _build(self):
        for w in self.parent.winfo_children():
            w.destroy()
        section_title(self.parent, "👑  Admin Panel", C["danger"])
        separator(self.parent)

        nb = ttk.Notebook(self.parent)
        nb.pack(fill="both", expand=True, padx=12, pady=6)

        # Users tab
        ut = tk.Frame(nb, bg=C["card"])
        nb.add(ut, text="  👥 Users  ")
        self._users_tab(ut)

        # Messages tab
        mt = tk.Frame(nb, bg=C["card"])
        nb.add(mt, text="  💬 All Messages  ")
        self._messages_tab(mt)

        # Passwords tab
        pt = tk.Frame(nb, bg=C["card"])
        nb.add(pt, text="  🔑 All Passwords  ")
        self._passwords_tab(pt)

    def _users_tab(self, f):
        """Display all registered users"""
        users = _load_users()
        
        # Create treeview
        columns = ("Username", "Caption", "Has Password")
        tree = ttk.Treeview(f, columns=columns, show="headings", height=15)
        tree.heading("Username", text="Username")
        tree.heading("Caption", text="Caption")
        tree.heading("Has Password", text="Has Password")
        tree.column("Username", width=150)
        tree.column("Caption", width=250)
        tree.column("Has Password", width=100)
        
        for username, data in users.items():
            tree.insert("", tk.END, values=(username, data.get("caption", ""), "✓" if data.get("hash") else "✗"))
        
        scrollbar = ttk.Scrollbar(f, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # Buttons
        btn_frame = tk.Frame(f, bg=C["card"])
        btn_frame.pack(fill="x", pady=10)
        styled_btn(btn_frame, "🗑 Delete User", lambda: self._delete_user(tree), 
                   color=C["danger"], width=15).pack(side="left", padx=10)
        styled_btn(btn_frame, "🔄 Refresh", lambda: self._refresh_users(f), 
                   color=C["card2"], width=15).pack(side="left", padx=10)

    def _delete_user(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select User", "Please select a user to delete.")
            return
        
        item = tree.item(selected[0])
        username = item["values"][0]
        
        if username == ADMIN_USER:
            messagebox.showerror("Cannot Delete", "Cannot delete the admin account!")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Delete user '{username}' and all their data?"):
            users = _load_users()
            if username in users:
                del users[username]
                from modules.auth import _save_users
                _save_users(users)
                messagebox.showinfo("Deleted", f"User '{username}' has been deleted.")
                self._refresh_users(tree.master)

    def _refresh_users(self, f):
        """Refresh the users tab"""
        for w in f.winfo_children():
            w.destroy()
        self._users_tab(f)

    def _messages_tab(self, f):
        """Display all messages from all users"""
        msgs_file = os.path.join("toolkit_data", "messages.txt")
        
        text_area = scrolled_out(f, height=20, fg=C["accent2"])
        text_area.pack(fill="both", expand=True, padx=10, pady=10)
        
        text_area.config(state="normal")
        text_area.delete("1.0", tk.END)
        
        if os.path.exists(msgs_file):
            try:
                with open(msgs_file, "r") as file:
                    messages = json.load(file)
                
                text_area.insert(tk.END, "═" * 60 + "\n")
                text_area.insert(tk.END, "ALL ENCRYPTED MESSAGES\n")
                text_area.insert(tk.END, "═" * 60 + "\n\n")
                
                for i, msg in enumerate(messages, 1):
                    text_area.insert(tk.END, f"[{i}] From: {msg.get('from', 'Unknown')}\n")
                    text_area.insert(tk.END, f"    Encrypted: {msg.get('enc', '')[:100]}...\n")
                    text_area.insert(tk.END, f"    Salt: {msg.get('salt', '')[:20]}...\n")
                    text_area.insert(tk.END, "─" * 40 + "\n\n")
            except Exception as e:
                text_area.insert(tk.END, f"Error reading messages: {e}\n")
        else:
            text_area.insert(tk.END, "No messages found.\n")
        
        text_area.config(state="disabled")

    def _passwords_tab(self, f):
        """Display passwords from vaults (requires decryption attempt)"""
        vault_file = os.path.join("toolkit_data", "vault.enc")
        salt_file = os.path.join("toolkit_data", "vault.salt")
        
        text_area = scrolled_out(f, height=20, fg=C["gold"])
        text_area.pack(fill="both", expand=True, padx=10, pady=10)
        
        text_area.config(state="normal")
        text_area.delete("1.0", tk.END)
        
        text_area.insert(tk.END, "═" * 60 + "\n")
        text_area.insert(tk.END, "ENCRYPTED VAULT DATA\n")
        text_area.insert(tk.END, "═" * 60 + "\n\n")
        
        if os.path.exists(vault_file):
            text_area.insert(tk.END, "Vault file exists but is encrypted.\n")
            text_area.insert(tk.END, "To view credentials, the vault must be unlocked\n")
            text_area.insert(tk.END, "by the user with their master password.\n\n")
            
            # Show file info
            import stat
            vault_size = os.path.getsize(vault_file)
            text_area.insert(tk.END, f"Vault size: {vault_size} bytes\n")
            text_area.insert(tk.END, f"Vault path: {vault_file}\n")
            
            if os.path.exists(salt_file):
                salt_size = os.path.getsize(salt_file)
                text_area.insert(tk.END, f"Salt size: {salt_size} bytes\n")
        else:
            text_area.insert(tk.END, "No vault file found.\n")
        
        text_area.config(state="disabled")
        
        # Add note about decryption
        note_frame = tk.Frame(f, bg=C["card"])
        note_frame.pack(fill="x", pady=5)
        tk.Label(note_frame, text="ℹ️ Passwords are stored encrypted. The vault requires the user's master password to decrypt.",
                 font=("Consolas", 9), bg=C["card"], fg=C["warning"]).pack()