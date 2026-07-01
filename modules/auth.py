import tkinter as tk
from tkinter import messagebox
import hashlib
import os
import random
import string
from modules.config import C, DATA_DIR, dp, styled_entry, styled_btn

USERS_TXT = dp("users.txt")

def _load_users():
    """Load users from file with proper error handling"""
    users = {}
    if os.path.exists(USERS_TXT):
        try:
            with open(USERS_TXT, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and "|" in line:
                        parts = line.split("|")
                        if len(parts) >= 2:
                            u = parts[0]
                            h = parts[1]
                            caption = parts[2] if len(parts) > 2 else ""
                            users[u] = {"hash": h, "caption": caption}
        except Exception as e:
            print(f"Error loading users: {e}")
    return users

def _save_users(users):
    """Save users to file with proper persistence"""
    try:
        with open(USERS_TXT, "w") as f:
            for u, data in users.items():
                caption = data.get("caption", "")
                f.write(f"{u}|{data['hash']}|{caption}\n")
        return True
    except Exception as e:
        print(f"Error saving users: {e}")
        return False

def _hash(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def generate_captcha():
    """Generate random CAPTCHA with mixed case (uppercase + lowercase + numbers)"""
    # Mix of uppercase, lowercase, and numbers
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    # Remove confusing characters like 0, O, 1, l, I, etc.
    confusing = '0O1lI'
    chars = ''.join(c for c in chars if c not in confusing)
    # Generate 6 random characters
    captcha = ''.join(random.choice(chars) for _ in range(6))
    return captcha

class LoginGate:
    """Full-screen login / register screen with MIXED CASE CAPTCHA"""
    
    def __init__(self, root, on_login):
        self.root = root
        self.on_login = on_login
        self.users = _load_users()
        self.register_mode = False
        self.current_captcha = ""
        self._build()

    def _build(self):
        self.frame = tk.Frame(self.root, bg=C["bg"])
        self.frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # decorative left panel
        left = tk.Frame(self.frame, bg=C["sidebar"], width=340)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(left, text="🔐", font=("Consolas", 52),
                 bg=C["sidebar"], fg=C["accent"]).pack(pady=(80, 10))
        tk.Label(left, text="SECURITY\nTOOLKIT",
                 font=("Consolas", 22, "bold"),
                 bg=C["sidebar"], fg=C["text"]).pack()
        tk.Label(left, text="Educational",
                 font=("Consolas", 9),
                 bg=C["sidebar"], fg=C["muted"]).pack(pady=6)

        tk.Frame(left, bg=C["accent"], height=2).pack(fill="x", padx=30, pady=20)

        features = [
            ("💬", "Secure Messaging"),
            ("🔑", "Password Manager"),
            ("🗄️", "File Encryption"),
            ("🎣", "Phishing Simulator"),
            ("🔡", "Cipher Toolkit"),
        ]
        for icon, name in features:
            r = tk.Frame(left, bg=C["sidebar"])
            r.pack(fill="x", padx=30, pady=3)
            tk.Label(r, text=icon, font=("Consolas", 12),
                     bg=C["sidebar"], fg=C["accent"]).pack(side="left")
            tk.Label(r, text=f"  {name}", font=("Consolas", 10),
                     bg=C["sidebar"], fg=C["muted"]).pack(side="left")

        tk.Label(left, text=f"data → {DATA_DIR}/",
                 font=("Consolas", 8),
                 bg=C["sidebar"], fg=C["border"]).pack(side="bottom", pady=10)

        # right panel
        right = tk.Frame(self.frame, bg=C["bg"])
        right.pack(side="right", fill="both", expand=True)

        inner = tk.Frame(right, bg=C["card"], bd=0,
                         highlightthickness=1,
                         highlightbackground=C["border"])
        inner.place(relx=0.5, rely=0.5, anchor="center", width=440)

        self.title_label = tk.Label(inner, text="Welcome Back",
                                    font=("Consolas", 18, "bold"),
                                    bg=C["card"], fg=C["text"])
        self.title_label.pack(pady=(30, 4))
        
        self.sub_label = tk.Label(inner, text="Sign in to continue",
                                  font=("Consolas", 10),
                                  bg=C["card"], fg=C["muted"])
        self.sub_label.pack(pady=(0, 15))

        # username
        tk.Label(inner, text="USERNAME", font=("Consolas", 8, "bold"),
                 bg=C["card"], fg=C["muted"]).pack(anchor="w", padx=30)
        self.u_entry = styled_entry(inner, width=38)
        self.u_entry.pack(padx=30, pady=(2, 10))

        # password
        tk.Label(inner, text="PASSWORD", font=("Consolas", 8, "bold"),
                 bg=C["card"], fg=C["muted"]).pack(anchor="w", padx=30)
        self.p_entry = styled_entry(inner, width=38, show="●")
        self.p_entry.pack(padx=30, pady=(2, 10))

        # CAPTCHA SECTION - SIMPLIFIED with mixed case
        captcha_container = tk.Frame(inner, bg=C["card2"], bd=2, relief="solid", highlightbackground=C["border"])
        captcha_container.pack(fill="x", padx=30, pady=(5, 10))
        
        # CAPTCHA label
        captcha_header = tk.Frame(captcha_container, bg=C["card2"])
        captcha_header.pack(fill="x", padx=10, pady=(8, 0))
        
        tk.Label(captcha_header, text="🔒 VERIFICATION CODE", 
                 font=("Consolas", 9, "bold"),
                 bg=C["card2"], fg=C["warning"]).pack(side="left")
        
        # CAPTCHA display frame
        captcha_display_frame = tk.Frame(captcha_container, bg=C["entry"], bd=1, relief="sunken")
        captcha_display_frame.pack(fill="x", padx=10, pady=(8, 5))
        
        # CAPTCHA text display (shows mixed case)
        self.captcha_display = tk.Label(captcha_display_frame, 
                                         text="XXXXXX",
                                         font=("Courier New", 24, "bold"),
                                         bg=C["entry"], fg=C["accent2"],
                                         width=10, height=1,
                                         pady=10)
        self.captcha_display.pack(pady=5)
        
        # Button frame below CAPTCHA
        captcha_button_frame = tk.Frame(captcha_container, bg=C["card2"])
        captcha_button_frame.pack(fill="x", padx=10, pady=(5, 8))
        
        # Refresh button
        styled_btn(captcha_button_frame, "🔄 New Code", self._refresh_captcha,
                   color=C["accent"], width=14).pack(side="left", padx=5)
        
        # CAPTCHA entry field
        tk.Label(captcha_container, text="Enter the code exactly as shown:", 
                 font=("Consolas", 8), bg=C["card2"], fg=C["muted"]).pack(anchor="w", padx=10)
        
        self.captcha_entry = styled_entry(captcha_container, width=34, show="")
        self.captcha_entry.pack(fill="x", padx=10, pady=(5, 10))
        
        # buttons
        bf = tk.Frame(inner, bg=C["card"])
        bf.pack(padx=30, pady=(5, 10), fill="x")
        self.login_btn = styled_btn(bf, "LOGIN", self._login,
                                    color=C["accent"], width=13)
        self.login_btn.pack(side="left")
        self.toggle_btn = styled_btn(bf, "REGISTER", self._toggle_mode,
                                     color=C["card2"], width=13)
        self.toggle_btn.pack(side="right")

        self.status = tk.Label(inner, text="",
                               font=("Consolas", 9),
                               bg=C["card"], fg=C["danger"])
        self.status.pack(pady=(0, 15))

        # Bind Enter key
        self.p_entry.bind("<Return>", lambda e: self._login())
        self.captcha_entry.bind("<Return>", lambda e: self._login())
        
        # Generate initial CAPTCHA
        self._refresh_captcha()

    def _refresh_captcha(self):
        """Generate new random CAPTCHA with mixed case"""
        self.current_captcha = generate_captcha()
        self.captcha_display.config(text=self.current_captcha)
        self.captcha_entry.delete(0, tk.END)
        # Flash effect to show it refreshed
        original_bg = self.captcha_display.cget("bg")
        self.captcha_display.config(bg=C["accent"])
        self.root.after(200, lambda: self.captcha_display.config(bg=original_bg))
        # Clear status message
        self.status.config(text="")

    def _verify_captcha(self):
        """Check if entered CAPTCHA matches (exact match including case)"""
        entered = self.captcha_entry.get().strip()
        # Exact match comparison (case sensitive)
        if entered != self.current_captcha:
            self._err(f"CAPTCHA verification failed! Expected '{self.current_captcha}'")
            self._refresh_captcha()
            return False
        return True

    def _toggle_mode(self):
        """Toggle between login and register mode"""
        self.register_mode = not self.register_mode
        
        if self.register_mode:
            self.title_label.config(text="Create Account")
            self.sub_label.config(text="Register with verification")
            self.login_btn.config(text="REGISTER")
            self.toggle_btn.config(text="← BACK TO LOGIN")
        else:
            self.title_label.config(text="Welcome Back")
            self.sub_label.config(text="Sign in to continue")
            self.login_btn.config(text="LOGIN")
            self.toggle_btn.config(text="REGISTER")
        
        # Refresh CAPTCHA when toggling
        self._refresh_captcha()
        self.status.config(text="")
        self.u_entry.delete(0, tk.END)
        self.p_entry.delete(0, tk.END)

    def _login(self):
        u = self.u_entry.get().strip()
        p = self.p_entry.get().strip()
        
        # Verify CAPTCHA first
        if not self._verify_captcha():
            return
        
        if self.register_mode:
            self._register(u, p)
        else:
            if u not in self.users:
                self._err("User not found. Register first.")
                return
            if self.users[u]["hash"] != _hash(p):
                self._err("Incorrect password.")
                return
            self.frame.destroy()
            self.on_login(u, p, self.users[u].get("caption", ""))

    def _register(self, u, p):
        if not u or not p:
            self._err("Both username and password are required.")
            return
        if len(p) < 6:
            self._err("Password must be ≥ 6 characters.")
            return
        if u in self.users:
            self._err("Username already taken.")
            return
        
        # Save new user
        self.users[u] = {"hash": _hash(p), "caption": ""}
        if _save_users(self.users):
            self._ok(f"Account created for {u}! Please login.")
            self._toggle_mode()  # Switch back to login mode
            self.u_entry.delete(0, tk.END)
            self.p_entry.delete(0, tk.END)
            self._refresh_captcha()
        else:
            self._err("Failed to save user data. Check permissions.")

    def _err(self, msg):
        self.status.config(text=f"✗  {msg}", fg=C["danger"])

    def _ok(self, msg):
        self.status.config(text=f"✓  {msg}", fg=C["success"])