# ──────────────────────────────────────────────────────────
#  PHISHING SIMULATOR MODULE - Enhanced with timer and 6 questions
# ──────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import ttk, messagebox
import random
import threading
import json
import os
from modules.config import C, dp, section_title, separator, scrolled_out, styled_entry, styled_btn

class PhishingSimulator:
    SIGNS = [
        ("@", "URL contains '@' — real domain is after the @"),
        ("login", "Fake login pages often use 'login' keyword"),
        ("secure", "'Secure' keyword used to appear trustworthy"),
        ("verify", "Urges account verification — classic tactic"),
        ("update", "Update urgency — social engineering"),
        ("http://", "No HTTPS — connection is unencrypted"),
        (".xyz", ".xyz TLD — commonly used in phishing"),
        (".tk", ".tk — free domain, frequently abused"),
        (".top", ".top — cheap domain, common in phishing"),
        (".club", ".club — often used for fake promotions"),
        ("bit.ly", "URL shortener hides real destination"),
        ("tinyurl", "URL shortener hides real destination"),
        ("192.168", "IP address instead of domain — very suspicious"),
        ("-paypal", "Hyphenated brand — not the real domain"),
        ("-amazon", "Hyphenated brand — not the real domain"),
        ("paypa1", "Typosquatting: '1' instead of 'l'"),
        ("g00gle", "Typosquatting: '00' instead of 'oo'"),
        ("faceb00k", "Typosquatting: '00' instead of 'oo'"),
    ]

    BANK = [
        {"q": "Email: 'Verify your PayPal account'\nURL: http://paypal-secure-login.xyz/verify\n\nSafe?",
         "options": ["A) Yes — mentions PayPal", "B) No — phishing attempt"],
         "answer": "B", "explain": "Red flags: http, hyphenated brand, .xyz, verification urgency."},
        {"q": "URL: https://accounts.google.com/login\n\nSafe?",
         "options": ["A) Likely safe — real Google domain", "B) Dangerous"],
         "answer": "A", "explain": "HTTPS + real google.com domain = legitimate."},
        {"q": "URL: https://amaz0n.com/deals\n\nSafe?",
         "options": ["A) Yes — HTTPS present", "B) No — '0' instead of 'o' = typosquatting"],
         "answer": "B", "explain": "Typosquatting swaps characters. HTTPS alone is not enough."},
        {"q": "Link: https://bit.ly/free-iphone-2024\n\nClick?",
         "options": ["A) Yes — free iPhone!", "B) No — shortener hides real destination"],
         "answer": "B", "explain": "Always expand short URLs before clicking."},
        {"q": "Email from 'support@paypa1.com' asks for password.\nLegit?",
         "options": ["A) Yes — says PayPal", "B) No — 'paypa1' swaps 'l' for '1'"],
         "answer": "B", "explain": "Check every character in email addresses carefully."},
        {"q": "Attachment named 'invoice.pdf.exe'.\nOpen it?",
         "options": ["A) Yes — looks like a PDF", "B) No — double extension hides malware"],
         "answer": "B", "explain": "Real PDFs never end in .exe."},
        {"q": "Site has green padlock (HTTPS).\nSafe to enter password?",
         "options": ["A) Yes — HTTPS = safe", "B) No — HTTPS only encrypts, not identity"],
         "answer": "B", "explain": "Phishing sites can have valid SSL certificates."},
        {"q": "URL: https://google.com@evil.com/login\n\nWhere does it go?",
         "options": ["A) google.com", "B) evil.com — part after @ is real domain"],
         "answer": "B", "explain": "Text before '@' is treated as a username by browsers."},
        {"q": "Email offers a prize but asks for a small fee first.\nWhat is it?",
         "options": ["A) Real prize — pay it", "B) Advance-fee scam"],
         "answer": "B", "explain": "Legitimate prizes never ask for money."},
        {"q": "URL: http://www.microsoft.com.helpdesk-support.net/login\nReal domain?",
         "options": ["A) microsoft.com", "B) helpdesk-support.net"],
         "answer": "B", "explain": "The real domain is right before the first slash."},
        {"q": "SMS: 'Your bank account is locked. Click http://bank-secure-verify.xyz'\nWhat to do?",
         "options": ["A) Click to unlock", "B) Ignore and call bank directly"],
         "answer": "B", "explain": "Never click links in SMS. Call your bank directly."},
        {"q": "QR code on restaurant table says 'Scan for menu'\n\nSafe?",
         "options": ["A) Yes — just a menu", "B) Could be dangerous — QR codes can point anywhere"],
         "answer": "B", "explain": "Always check the URL before visiting QR code links."},
        {"q": "Email: 'Your Apple ID is compromised. Verify at https://appleid-secure-verify.com'\n\nSafe?",
         "options": ["A) Yes — Apple ID", "B) No — fake domain"],
         "answer": "B", "explain": "Real Apple uses apple.com. Hyphenated domains are suspicious."},
        {"q": "URL: https://www.paypal.com@192.168.1.1/login\n\nReal destination?",
         "options": ["A) paypal.com", "B) 192.168.1.1"],
         "answer": "B", "explain": "Everything before @ is ignored. The real destination is the IP."},
        {"q": "Job offer: 'Send us $50 for processing'\n\nWhat is this?",
         "options": ["A) Real job opportunity", "B) Advance-fee scam"],
         "answer": "B", "explain": "Legitimate employers never ask for money."},
        {"q": "Website asks for SSN and mother's maiden name\n\nSafe?",
         "options": ["A) Yes — they need to verify", "B) No — phishing for personal info"],
         "answer": "B", "explain": "Legitimate sites don't ask for SSN and mother's maiden name together."},
        {"q": "URL: https://www.google.com.phishing-site.net\n\nReal domain?",
         "options": ["A) google.com", "B) phishing-site.net"],
         "answer": "B", "explain": "google.com is a subdomain. The real domain is phishing-site.net."},
        {"q": "Email: 'Your Netflix subscription expires today. Renew at http://netflix-renewal.top'\n\nSafe?",
         "options": ["A) Yes — Netflix renewal", "B) No — fake domain"],
         "answer": "B", "explain": "Real Netflix uses netflix.com. .top domain is suspicious."},
        {"q": "Email: 'We found suspicious activity. Click here to check'\n\nWhat to do?",
         "options": ["A) Click to check", "B) Go directly to the official website"],
         "answer": "B", "explain": "Always type the official URL directly."},
        {"q": "URL: http://login-facebook.secure-verify.xyz\n\nSafe?",
         "options": ["A) Yes — says login-facebook", "B) No — fake domain"],
         "answer": "B", "explain": "Real Facebook uses facebook.com. This domain has multiple suspicious elements."},
    ]

    def __init__(self, parent, username):
        self.parent = parent
        self.username = username
        self.quiz_pool = list(self.BANK)
        self.quiz = []
        self.qi = self.score = 0
        self.attempts_file = dp("phishing_attempts.json")
        self.attempts = self._load_attempts()
        self.timer_running = False
        self.time_left = 30
        self.timer_id = None
        self._build()

    def _load_attempts(self):
        if os.path.exists(self.attempts_file):
            try:
                with open(self.attempts_file, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_attempts(self):
        try:
            with open(self.attempts_file, "w") as f:
                json.dump(self.attempts, f, indent=2)
        except Exception:
            pass

    def _get_user_attempts(self):
        if self.username not in self.attempts:
            self.attempts[self.username] = {"total": 0, "scores": []}
        return self.attempts[self.username]

    def _record_attempt(self, score, total):
        user_data = self._get_user_attempts()
        user_data["total"] += 1
        user_data["scores"].append({"score": score, "total": total})
        self._save_attempts()

    def _build(self):
        for w in self.parent.winfo_children():
            w.destroy()
        section_title(self.parent, "🛡️  Phishing Awareness", C["warning"])
        separator(self.parent)
        nb = ttk.Notebook(self.parent)
        nb.pack(fill="both", expand=True, padx=12, pady=6)

        ut = tk.Frame(nb, bg=C["card"])
        nb.add(ut, text="  🔍 URL Checker  ")
        self._url_tab(ut)

        et = tk.Frame(nb, bg=C["card"])
        nb.add(et, text="  📚 Awareness  ")
        self._awareness_tab(et)

        qt = tk.Frame(nb, bg=C["card"])
        nb.add(qt, text="  🧠 Quiz  ")
        self.quiz_frame = qt
        self._start_quiz(qt)

    def _url_tab(self, f):
        tk.Label(f, text="Paste a URL to check for phishing indicators:", font=("Consolas", 9), bg=C["card"], fg=C["muted"]).pack(pady=8)
        self.url_e = styled_entry(f, width=60)
        self.url_e.pack(pady=4)
        styled_btn(f, "🔍 Analyse", self._check, color=C["warning"], fg="black", width=18).pack(pady=6)
        self.url_out = scrolled_out(f, height=14)
        self.url_out.pack(padx=12)

    def _check(self):
        url = self.url_e.get().strip().lower()
        if not url:
            return
        self.url_out.config(state="normal")
        self.url_out.delete("1.0", tk.END)
        self.url_out.insert(tk.END, f"Analysing: {url}\n{'═'*55}\n\n")
        
        issues = []
        for s, e in self.SIGNS:
            if s in url:
                issues.append((s, e))
        
        # Check for brand typosquatting
        brands = ["paypal", "amazon", "google", "microsoft", "apple", "facebook"]
        for brand in brands:
            if brand in url:
                # Check if brand is not the main domain
                if f".{brand}." not in url and f"://{brand}." not in url:
                    if brand + "-" in url or "-" + brand in url:
                        issues.append((brand, f"'{brand}' appears as subdomain or with hyphens — suspicious"))
        
        if issues:
            self.url_out.insert(tk.END, "⚠️  WARNING — Issues Found:\n\n")
            for s, e in issues[:6]:  # Show top 6 issues
                self.url_out.insert(tk.END, f"  🔴 '{s}'\n     → {e}\n\n")
            if len(issues) > 6:
                self.url_out.insert(tk.END, f"  ... and {len(issues)-6} more issues\n\n")
            self.url_out.insert(tk.END, "\n⛔ RECOMMENDATION: Do NOT click this URL.\n")
        else:
            self.url_out.insert(tk.END, "✅  No obvious phishing signs found.\n\n")
        self.url_out.config(state="disabled")

    def _awareness_tab(self, f):
        """Concise awareness tab with key information"""
        cv = tk.Canvas(f, bg=C["card"], highlightthickness=0)
        sb = ttk.Scrollbar(f, orient="vertical", command=cv.yview)
        inner = tk.Frame(cv, bg=C["card"])
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)
        cv.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        
        awareness_items = [
            ("🛡️ What is Phishing?", 
             "Phishing is a cyberattack where criminals impersonate legitimate organizations to steal passwords, credit cards, and personal data."),
            ("⚠️ Common Red Flags", 
             "• Urgent/threatening language\n• Requests for personal info\n• Unexpected attachments/links\n• Misspelled domains (paypa1.com)\n• Suspicious sender addresses"),
            ("🛡️ How to Protect Yourself", 
             "• Check sender's email address\n• Hover over links to see real URL\n• Never share passwords/OTPs\n• Use 2-Factor Authentication\n• Report suspicious emails"),
            ("🔍 URL Analysis Tips", 
             "• Check for HTTPS (not foolproof)\n• Verify the domain name carefully\n• Watch for typosquatting\n• Be wary of URL shorteners\n• Real domain is before the first slash"),
            ("📊 Phishing Statistics", 
             "• 91% of cyberattacks start with phishing\n• 30% of phishing emails are opened\n• 12% of users click malicious links\n• Avg cost: $4.91 million per attack"),
            ("🚨 What to Do if Targeted", 
             "1. Don't click links/downloads\n2. Report to the impersonated company\n3. Forward to reportphishing@apwg.org\n4. Change passwords immediately\n5. Monitor financial accounts"),
        ]
        
        for title, content in awareness_items:
            card = tk.LabelFrame(inner, text=f" {title} ", bg=C["card2"], fg=C["gold"],
                                 font=("Consolas", 9, "bold"), bd=1)
            card.pack(fill="x", padx=10, pady=4)
            tk.Label(card, text=content, bg=C["card2"], fg=C["muted"], 
                     font=("Consolas", 8), justify="left", wraplength=550).pack(anchor="w", padx=8, pady=6)

    def _start_quiz(self, f):
        self._stop_timer()
        for w in f.winfo_children():
            w.destroy()
        
        user_data = self._get_user_attempts()
        stats_frame = tk.Frame(f, bg=C["card"])
        stats_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(stats_frame, text=f"👤 {self.username}", font=("Consolas", 10, "bold"),
                 bg=C["card"], fg=C["accent"]).pack(side="left", padx=10)
        tk.Label(stats_frame, text=f"Attempts: {user_data['total']}", font=("Consolas", 9),
                 bg=C["card"], fg=C["muted"]).pack(side="left", padx=10)
        if user_data["scores"]:
            last_score = user_data["scores"][-1]
            tk.Label(stats_frame, text=f"Last: {last_score['score']}/{last_score['total']}", 
                     font=("Consolas", 9), bg=C["card"], fg=C["gold"]).pack(side="left", padx=10)
            
            avg = sum(s["score"]/s["total"] for s in user_data["scores"]) / len(user_data["scores"])
            tk.Label(stats_frame, text=f"Avg: {avg*100:.1f}%", 
                     font=("Consolas", 9), bg=C["card"], fg=C["success"]).pack(side="left", padx=10)
        
        # Quiz info
        info_frame = tk.Frame(f, bg=C["card"])
        info_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(info_frame, text="⏱️ 30 seconds per question • 6 questions total", 
                 font=("Consolas", 9), bg=C["card"], fg=C["warning"]).pack()
        
        lbl = tk.Label(f, text="⏳ Loading quiz…", font=("Consolas", 12), bg=C["card"], fg=C["gold"])
        lbl.pack(pady=40)

        def go():
            pool = list(self.quiz_pool)
            random.shuffle(pool)
            self.quiz = pool[:6]  # 6 questions per quiz
            self.qi = 0
            self.score = 0
            f.after(0, self._show_q)
        threading.Thread(target=go, daemon=True).start()

    def _show_q(self):
        self._stop_timer()
        f = self.quiz_frame
        for w in f.winfo_children():
            w.destroy()
        
        user_data = self._get_user_attempts()
        stats_frame = tk.Frame(f, bg=C["card"])
        stats_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(stats_frame, text=f"👤 {self.username}", font=("Consolas", 9),
                 bg=C["card"], fg=C["accent"]).pack(side="left", padx=5)
        tk.Label(stats_frame, text=f"Attempts: {user_data['total']}", font=("Consolas", 9),
                 bg=C["card"], fg=C["muted"]).pack(side="left", padx=5)
        
        if self.qi >= len(self.quiz):
            self._result()
            return
        
        q = self.quiz[self.qi]
        q_frame = tk.Frame(f, bg=C["card"])
        q_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Question header with timer
        header_frame = tk.Frame(q_frame, bg=C["card"])
        header_frame.pack(fill="x", pady=6)
        
        tk.Label(header_frame, text=f"Question {self.qi+1} / {len(self.quiz)}", font=("Consolas", 10),
                 bg=C["card"], fg=C["muted"]).pack(side="left")
        
        self.timer_label = tk.Label(header_frame, text="⏱️ 30", font=("Consolas", 12, "bold"),
                                     bg=C["card"], fg=C["success"])
        self.timer_label.pack(side="right")
        
        tk.Label(q_frame, text=q["q"], font=("Consolas", 11), bg=C["card"], fg=C["text"],
                 wraplength=540, justify="left").pack(padx=16, pady=8)
        
        # Store buttons for disabling later
        self.option_buttons = []
        for opt in q["options"]:
            l = opt[0]
            btn = styled_btn(q_frame, opt, lambda l=l: self._ans(l), color=C["card2"], width=60)
            btn.pack(pady=4)
            self.option_buttons.append(btn)
        
        # Start timer
        self.time_left = 30
        self.timer_running = True
        self._update_timer()

    def _update_timer(self):
        if not self.timer_running:
            return
        
        self.timer_label.config(text=f"⏱️ {self.time_left}")
        
        if self.time_left <= 5:
            self.timer_label.config(fg=C["danger"])
        elif self.time_left <= 10:
            self.timer_label.config(fg=C["warning"])
        else:
            self.timer_label.config(fg=C["success"])
        
        if self.time_left <= 0:
            # Time's up - auto answer wrong
            self.timer_running = False
            self._time_up()
            return
        
        self.time_left -= 1
        self.timer_id = self.parent.after(1000, self._update_timer)

    def _stop_timer(self):
        self.timer_running = False
        if self.timer_id:
            self.parent.after_cancel(self.timer_id)
            self.timer_id = None

    def _time_up(self):
        q = self.quiz[self.qi]
        messagebox.showwarning("Time's Up!", f"⏰ Time ran out!\n\nThe correct answer was: {q['answer']}\n\n{q['explain']}")
        self.qi += 1
        self._show_q()

    def _ans(self, c):
        self._stop_timer()
        q = self.quiz[self.qi]
        ok = (c == q["answer"])
        if ok:
            self.score += 1
        r = "✅ Correct!" if ok else f"❌ Wrong!  Answer: {q['answer']}"
        messagebox.showinfo("Answer", f"{r}\n\n{q['explain']}")
        self.qi += 1
        self._show_q()

    def _result(self):
        self._stop_timer()
        f = self.quiz_frame
        for w in f.winfo_children():
            w.destroy()
        
        self._record_attempt(self.score, len(self.quiz))
        
        pct = int(self.score / len(self.quiz) * 100)
        g, col = (("🏆 EXCELLENT!", C["success"]) if pct >= 80 else
                  ("📚 Good — keep learning!", C["gold"]) if pct >= 60 else
                  ("💪 Keep practicing!", C["accent3"]))
        
        tk.Label(f, text="Quiz Complete!", font=("Consolas", 18, "bold"), bg=C["card"], fg=C["gold"]).pack(pady=20)
        tk.Label(f, text=f"Score: {self.score}/{len(self.quiz)}  ({pct}%)", font=("Consolas", 14),
                 bg=C["card"], fg=C["text"]).pack()
        tk.Label(f, text=g, font=("Consolas", 12), bg=C["card"], fg=col).pack(pady=10)
        
        user_data = self._get_user_attempts()
        stats_frame = tk.Frame(f, bg=C["card"])
        stats_frame.pack(pady=10)
        tk.Label(stats_frame, text=f"Total attempts: {user_data['total']}", font=("Consolas", 10),
                 bg=C["card"], fg=C["muted"]).pack()
        if user_data["scores"]:
            avg = sum(s["score"]/s["total"] for s in user_data["scores"]) / len(user_data["scores"])
            tk.Label(stats_frame, text=f"Average score: {avg*100:.1f}%", font=("Consolas", 10),
                     bg=C["card"], fg=C["success"]).pack()
        
        styled_btn(f, "🔄 Retry (new questions)", lambda: self._start_quiz(self.quiz_frame),
                   color=C["warning"], fg="black", width=26).pack(pady=14)