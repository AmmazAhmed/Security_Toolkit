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
    
    # Beaufort - 
    def _beaufort_ui(self, f):
        tk.Label(f, text="Brute-force decrypts by trying ALL possible keys (A-Z for each position up to length 6).\nWARNING: Long texts with key length 6 may take a few seconds.",
                 font=("Consolas", 9), bg=C["card"], fg=C["warning"]).pack(pady=6)
        
        # Key length selection
        len_frame = tk.Frame(f, bg=C["card"])
        len_frame.pack(pady=6)
        tk.Label(len_frame, text="Max Key Length:", font=("Consolas", 10), bg=C["card"], fg=C["text"]).pack(side="left", padx=6)
        self.max_keylen = tk.IntVar(value=4)
        len_spin = tk.Spinbox(len_frame, from_=1, to=6, width=5, textvariable=self.max_keylen,
                               font=("Consolas", 10), bg=C["entry"], fg=C["entry_fg"],
                               relief="flat", highlightthickness=1, highlightbackground=C["border"])
        len_spin.pack(side="left", padx=6)
        
        tk.Label(f, text="Cipher Text:", font=("Consolas", 9), bg=C["card"], fg=C["muted"]).pack(anchor="w")
        self.bin = tk.Text(f, width=56, height=6, bg=C["entry"], fg=C["entry_fg"], insertbackground=C["accent"],
                           font=("Consolas", 11), relief="flat", highlightthickness=1, highlightbackground=C["border"])
        self.bin.pack(pady=4)
        styled_btn(f, "🔓 Brute-Force", self._run_bf, color=C["accent"], width=18).pack(pady=6)
        self.bout = scrolled_out(f, height=14, fg=C["accent"])
        self.bout.pack()

    def _beaufort_decrypt(self, ciphertext, key):
        """Beaufort decryption with given key"""
        key = key.upper()
        result = []
        key_idx = 0
        for c in ciphertext:
            if c.isalpha():
                # Beaufort: P = (K - C) mod 26
                c_val = ord(c.upper()) - ord('A')
                k_val = ord(key[key_idx % len(key)]) - ord('A')
                p_val = (k_val - c_val) % 26
                result_char = chr(p_val + ord('A'))
                if c.islower():
                    result_char = result_char.lower()
                result.append(result_char)
                key_idx += 1
            else:
                result.append(c)
        return ''.join(result)

    def _score_text(self, text):
        """Score text based on English letter frequency"""
        text = text.upper()
        letters = [c for c in text if c.isalpha()]
        if not letters:
            return 0
        # Count frequency of each letter
        freq = {}
        for c in letters:
            freq[c] = freq.get(c, 0) + 1
        # Calculate chi-square against English frequencies
        score = 0
        for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            expected = self.EF.get(c, 0) * len(letters) / 100
            actual = freq.get(c, 0)
            if expected > 0:
                score += ((actual - expected) ** 2) / expected
        return -score  # Negative so lower chi-square = higher score

    def _bruteforce_beaufort(self, ciphertext, max_keylen):
        """Try all possible keys up to max_keylen and return ranked results"""
        ciphertext_upper = ''.join(c for c in ciphertext if c.isalpha()).upper()
        if not ciphertext_upper:
            return []
        
        results = []
        total_combinations = 0
        
        # For each key length
        for kl in range(1, max_keylen + 1):
            # Generate all possible keys of this length (26^kl combinations)
            # For performance, limit to reasonable combinations
            max_combinations = 26 ** kl
            if max_combinations > 10000 and kl > 4:
                # For longer keys, use frequency analysis optimization
                self._update_status(f"Key length {kl}: Using frequency analysis (26^{kl} too large)...")
                key = self._guess_key_frequency(ciphertext_upper, kl)
                decrypted = self._beaufort_decrypt(ciphertext, key)
                score = self._score_text(decrypted)
                results.append((score, kl, key, decrypted))
            else:
                # Try every possible key
                self._update_status(f"Key length {kl}: Trying {max_combinations} combinations...")
                letters = string.ascii_uppercase
                
                # Recursive function to generate all keys
                def generate_keys(current, length):
                    if len(current) == length:
                        key = ''.join(current)
                        decrypted = self._beaufort_decrypt(ciphertext, key)
                        score = self._score_text(decrypted)
                        results.append((score, length, key, decrypted))
                    else:
                        for ch in letters:
                            generate_keys(current + [ch], length)
                
                generate_keys([], kl)
        
        # Sort by score (higher is better)
        results.sort(reverse=True)
        return results[:20]  # Return top 20

    def _guess_key_frequency(self, ciphertext, keylen):
        """Use frequency analysis to guess key for longer key lengths"""
        key = []
        for pos in range(keylen):
            # Get all letters at this position
            col = [ciphertext[i] for i in range(pos, len(ciphertext), keylen)]
            if not col:
                key.append('A')
                continue
            
            # Try each possible key character
            best_score = -float('inf')
            best_char = 'A'
            for kc in string.ascii_uppercase:
                # Decrypt column with this key character
                decrypted = []
                for c in col:
                    c_val = ord(c) - ord('A')
                    k_val = ord(kc) - ord('A')
                    p_val = (k_val - c_val) % 26
                    decrypted.append(chr(p_val + ord('A')))
                
                # Score the decrypted column
                decrypted_text = ''.join(decrypted)
                score = self._score_text(decrypted_text)
                
                if score > best_score:
                    best_score = score
                    best_char = kc
            
            key.append(best_char)
        
        return ''.join(key)

    def _update_status(self, message):
        """Update status in output box"""
        self.bout.config(state="normal")
        self.bout.insert(tk.END, f"  ... {message}\n")
        self.bout.see(tk.END)
        self.bout.config(state="disabled")
        self.bout.update()

    def _run_bf(self):
        ciphertext = self.bin.get("1.0", tk.END).strip()
        if not ciphertext:
            messagebox.showwarning("No Text", "Enter cipher text to decrypt!")
            return
        
        max_keylen = self.max_keylen.get()
        
        # Clear output
        self.bout.config(state="normal")
        self.bout.delete("1.0", tk.END)
        self.bout.insert(tk.END, f"🔓 BRUTE-FORCE DECRYPTION\n")
        self.bout.insert(tk.END, f"═" * 55 + "\n")
        self.bout.insert(tk.END, f"Ciphertext: {ciphertext[:100]}{'...' if len(ciphertext)>100 else ''}\n")
        self.bout.insert(tk.END, f"Max key length: {max_keylen}\n")
        self.bout.insert(tk.END, f"═" * 55 + "\n\n")
        self.bout.config(state="disabled")
        self.bout.update()
        
        try:
            # Run brute-force
            results = self._bruteforce_beaufort(ciphertext, max_keylen)
            
            # Display results
            self.bout.config(state="normal")
            self.bout.delete("1.0", tk.END)
            self.bout.insert(tk.END, f"🔓 BEAUFORT BRUTE-FORCE RESULTS\n")
            self.bout.insert(tk.END, f"═" * 55 + "\n\n")
            
            if not results:
                self.bout.insert(tk.END, "No results found.\n")
            else:
                self.bout.insert(tk.END, f"Top {min(10, len(results))} possible keys:\n\n")
                for i, (score, klen, key, plain) in enumerate(results[:10], 1):
                    self.bout.insert(tk.END, f"#{i}  Key length: {klen}  |  Key: '{key}'\n")
                    self.bout.insert(tk.END, f"    Score: {score:.2f}\n")
                    self.bout.insert(tk.END, f"    Decrypted: {plain[:120]}{'...' if len(plain)>120 else ''}\n")
                    self.bout.insert(tk.END, f"    {'─' * 50}\n\n")
            
            self.bout.insert(tk.END, "\n💡 Tip: Try each key in the 'Decrypt' tab to verify which is correct.\n")
            self.bout.config(state="disabled")
            
        except Exception as e:
            self.bout.config(state="normal")
            self.bout.insert(tk.END, f"❌ Error during brute-force: {str(e)}\n")
            self.bout.config(state="disabled")
            messagebox.showerror("Error", f"Brute-force failed: {str(e)}")


