# ──────────────────────────────────────────────────────────
#  MAIN APPLICATION - Sidebar navigation
# ──────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import ttk, messagebox
from modules.config import C, section_title, separator, styled_btn
from modules.messaging import SecureMessaging
from modules.password_manager import PasswordManager
from modules.file_encryption import FileEncryptionTool
from modules.phishing import PhishingSimulator
from modules.cipher import CipherToolkit
from modules.admin import AdminPanel


class App:
    MENU = [
        ("🏠", "Home", None),
        ("💬", "Secure Messaging", None),
        ("🔑", "Password Manager", None),
        ("🗄️", "File Encryption", None),
        ("🎣", "Phishing Simulator", None),
        ("🔡", "Cipher Toolkit", None),
        ("👑", "Admin Panel", None),
    ]

    def __init__(self, root):
        self.root = root
        self.username = None
        self.password = None
        self.caption = None
        self.root.title("Security Toolkit")
        self.root.geometry("1050x700")
        self.root.configure(bg=C["bg"])
        self.root.resizable(True, True)
        
        # ttk style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=C["card"], borderwidth=0)
        style.configure("TNotebook.Tab", background=C["card2"], foreground=C["muted"],
                        font=("Consolas", 10), padding=[10, 5])
        style.map("TNotebook.Tab",
                  background=[("selected", C["card"])],
                  foreground=[("selected", C["accent"])])
        style.configure("TCombobox", fieldbackground=C["entry"],
                        background=C["card2"], foreground=C["entry_fg"],
                        selectbackground=C["accent"])
        style.configure("Vertical.TScrollbar",
                        troughcolor=C["card"], background=C["card2"])
        
        from modules.auth import LoginGate
        LoginGate(root, self._on_login)

    def _on_login(self, username, password, caption=""):
        self.username = username
        self.password = password
        self.caption = caption
        self._build_main()

    def _build_main(self):
        # Sidebar
        self.sidebar = tk.Frame(self.root, bg=C["sidebar"], width=210)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo = tk.Frame(self.sidebar, bg=C["sidebar"])
        logo.pack(fill="x", pady=20, padx=14)
        tk.Label(logo, text="🔐", font=("Consolas", 30),
                 bg=C["sidebar"], fg=C["accent"]).pack()
        tk.Label(logo, text="SECURITY\nTOOLKIT",
                 font=("Consolas", 13, "bold"),
                 bg=C["sidebar"], fg=C["text"]).pack()
        tk.Frame(self.sidebar, bg=C["border"], height=1).pack(fill="x", padx=12)

        self.btn_refs = []
        for icon, name, _ in self.MENU:
            b = tk.Button(
                self.sidebar,
                text=f"  {icon}  {name}",
                command=lambda n=name: self._nav(n),
                bg=C["sidebar"], fg=C["muted"],
                relief="flat", bd=0,
                font=("Consolas", 10), anchor="w",
                padx=10, pady=8, width=24,
                activebackground=C["card"],
                activeforeground=C["accent"],
                cursor="hand2",
            )
            b.pack(fill="x", pady=1)
            self.btn_refs.append((name, b))

        tk.Frame(self.sidebar, bg=C["border"], height=1).pack(fill="x", padx=12, side="bottom", pady=6)
        styled_btn(self.sidebar, "⏻ Logout", self._logout,
                   color=C["danger"], width=18).pack(side="bottom", pady=6, padx=10)
        
        info_text = f"👤  {self.username}"
        if self.caption:
            info_text += f"\n📝  {self.caption}"
        tk.Label(self.sidebar, text=info_text,
                 font=("Consolas", 9), bg=C["sidebar"], fg=C["muted"], justify="left").pack(side="bottom")
        tk.Label(self.sidebar, text=f"data → toolkit_data/",
                 font=("Consolas", 7), bg=C["sidebar"], fg=C["border"]).pack(side="bottom")

        self.content = tk.Frame(self.root, bg=C["card"])
        self.content.pack(side="right", fill="both", expand=True)

        self._nav("Home")

    def _nav(self, name):
        self._active = name
        for n, b in self.btn_refs:
            if n == name:
                b.config(bg=C["accent"], fg="white")
            else:
                b.config(bg=C["sidebar"], fg=C["muted"])
        
        for w in self.content.winfo_children():
            w.destroy()
        
        if name == "Home":
            self._home()
        elif name == "Secure Messaging":
            SecureMessaging(self.content, self.username, self.password)
        elif name == "Password Manager":
            PasswordManager(self.content)
        elif name == "File Encryption":
            FileEncryptionTool(self.content)
        elif name == "Phishing Simulator":
            PhishingSimulator(self.content, self.username)
        elif name == "Cipher Toolkit":
            CipherToolkit(self.content)
        elif name == "Admin Panel":
            AdminPanel(self.content, self.username)

    def _home(self):
        section_title(self.content, f"👋  Welcome,  {self.username}", C["accent"])
        if self.caption:
            tk.Label(self.content, text=f"  \"{self.caption}\"",
                     font=("Consolas", 10, "italic"), bg=C["card"], fg=C["gold"]).pack(anchor="w", padx=22)
        
        tk.Label(self.content, text="  Choose a tool from the sidebar to get started.",
                 font=("Consolas", 10), bg=C["card"], fg=C["muted"]).pack(anchor="w", padx=22)
        separator(self.content)

        cards = [
            ("💬", "Secure Messaging", C["accent2"],
             "AES-encrypted chat. Messages stored in messages.txt."),
            ("🔑", "Password Manager", C["gold"],
             "AES vault on disk. Credentials + notes + generator."),
            ("🗄️", "File Encryption", C["accent3"],
             "Encrypt any file with a password."),
            ("🎣", "Phishing Simulator", C["warning"],
             "URL analyser + quiz to learn phishing detection."),
            ("🔡", "Cipher Toolkit", C["accent"],
             "Caesar / Beaufort / Vigenère ciphers."),
            ("👑", "Admin Panel", C["danger"],
             "View all users and their data (Admin only)."),
        ]
        grid = tk.Frame(self.content, bg=C["card"])
        grid.pack(padx=20, pady=10, fill="both", expand=True)
        
        for i, (icon, title, col, desc) in enumerate(cards):
            card = tk.Frame(grid, bg=C["card2"],
                            highlightthickness=1,
                            highlightbackground=C["border"],
                            cursor="hand2")
            card.grid(row=i//2, column=i%2, padx=8, pady=8, sticky="ew")
            grid.columnconfigure(0, weight=1)
            grid.columnconfigure(1, weight=1)
            tk.Frame(card, bg=col, height=3).pack(fill="x")
            inner = tk.Frame(card, bg=C["card2"])
            inner.pack(padx=12, pady=10, fill="x")
            tk.Label(inner, text=f"{icon}  {title}",
                     font=("Consolas", 11, "bold"),
                     bg=C["card2"], fg=col).pack(anchor="w")
            tk.Label(inner, text=desc, font=("Consolas", 9),
                     bg=C["card2"], fg=C["muted"],
                     wraplength=360, justify="left").pack(anchor="w", pady=4)
            card.bind("<Button-1>", lambda e, n=title: self._nav(n))
            for ch in card.winfo_children():
                ch.bind("<Button-1>", lambda e, n=title: self._nav(n))

        tk.Label(self.content, text="⚠️  Educational use only.",
                 font=("Consolas", 8), bg=C["card"], fg=C["danger"]).pack(pady=8)

    def _logout(self):
        if messagebox.askyesno("Logout", f"Log out {self.username}?"):
            for w in self.root.winfo_children():
                w.destroy()
            self.username = None
            self.password = None
            from modules.auth import LoginGate
            LoginGate(self.root, self._on_login)