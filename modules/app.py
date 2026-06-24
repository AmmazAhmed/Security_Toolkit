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