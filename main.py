# ──────────────────────────────────────────────────────────
#  SECURITY TOOLKIT - MAIN ENTRY POINT
# ──────────────────────────────────────────────────────────
import tkinter as tk
import sys
import os

# Add the current directory to path so modules can be found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.app import App

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()