"""
Sample Python Application - For PythonEXEBuilder Demo
Demonstrates: Tkinter UI, file I/O, internet access, drag & drop, local storage
Developed By SANTHOSH A
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import sys
import threading
import datetime

# ── Optional imports (graceful fallback) ────────────────────
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False

# ── Constants ────────────────────────────────────────────────
APP_NAME    = "Sample App"
DEVELOPER   = "SANTHOSH A"
DATA_FILE   = "local_storage.json"
BG_DARK     = "#1e1e2e"
BG_PANEL    = "#2a2a3e"
ACCENT      = "#00b4d8"
TEXT_LIGHT  = "#cdd6f4"
BTN_COLOR   = "#313244"


def load_local_data():
    """Load persisted user data from JSON file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"notes": "", "theme": "dark", "history": []}


def save_local_data(data: dict):
    """Save user data to JSON file (local storage)."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


class App:
    def __init__(self):
        self.data = load_local_data()

        # ── Root Window ─────────────────────────────────────
        if HAS_DND:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()

        self.root.title(f"{APP_NAME}  –  Developed By {DEVELOPER}")
        self.root.geometry("700x520")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(True, True)

        self._build_ui()
        self._load_state()

    # ── UI Construction ──────────────────────────────────────
    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=ACCENT, height=55)
        header.pack(fill="x")
        tk.Label(
            header, text=f"  {APP_NAME}",
            font=("Segoe UI", 16, "bold"),
            bg=ACCENT, fg="white"
        ).pack(side="left", pady=10)
        tk.Label(
            header, text=f"Developed By {DEVELOPER}  ",
            font=("Segoe UI", 9), bg=ACCENT, fg="white"
        ).pack(side="right", pady=10)

        # Main notebook
        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        # Apply dark style to notebook
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook",       background=BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab",   background=BTN_COLOR, foreground=TEXT_LIGHT,
                        padding=[12, 6])
        style.map("TNotebook.Tab",         background=[("selected", ACCENT)],
                  foreground=[("selected", "white")])

        self._tab_notes(nb)
        self._tab_files(nb)
        self._tab_internet(nb)
        self._tab_about(nb)

    # ── Notes Tab ───────────────────────────────────────────
    def _tab_notes(self, nb):
        frame = tk.Frame(nb, bg=BG_PANEL)
        nb.add(frame, text="  📝 Notes  ")

        tk.Label(frame, text="Local Notes (auto-saved):", bg=BG_PANEL,
                 fg=TEXT_LIGHT, font=("Segoe UI", 11)).pack(anchor="w", padx=10, pady=(10, 2))

        self.txt_notes = tk.Text(
            frame, bg="#181825", fg=TEXT_LIGHT,
            insertbackground=ACCENT, font=("Consolas", 11),
            relief="flat", padx=10, pady=8
        )
        self.txt_notes.pack(fill="both", expand=True, padx=10, pady=5)

        tk.Button(
            frame, text="💾  Save Notes", command=self._save_notes,
            bg=ACCENT, fg="white", relief="flat", cursor="hand2",
            font=("Segoe UI", 10), padx=12, pady=5
        ).pack(padx=10, pady=(0, 10))

    def _save_notes(self):
        self.data["notes"] = self.txt_notes.get("1.0", "end-1c")
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.data.setdefault("history", []).insert(0, f"Notes saved at {ts}")
        self.data["history"] = self.data["history"][:20]
        save_local_data(self.data)
        messagebox.showinfo("Saved", "Notes saved to local_storage.json ✔")

    # ── File I/O Tab ────────────────────────────────────────
    def _tab_files(self, nb):
        frame = tk.Frame(nb, bg=BG_PANEL)
        nb.add(frame, text="  📂 Files  ")

        # Drop zone
        drop_label = tk.Label(
            frame,
            text="⬇  Drop a file here (or click Browse)",
            bg="#11111b", fg="#888", font=("Segoe UI", 13),
            relief="groove", cursor="hand2"
        )
        drop_label.pack(fill="both", expand=True, padx=20, pady=20)

        if HAS_DND:
            drop_label.drop_target_register(DND_FILES)
            drop_label.dnd_bind("<<Drop>>", lambda e: self._on_drop(e, drop_label))

        self.file_info = tk.StringVar(value="No file selected")
        tk.Label(frame, textvariable=self.file_info, bg=BG_PANEL,
                 fg=TEXT_LIGHT).pack(pady=5)

        tk.Button(
            frame, text="📂  Browse File", command=lambda: self._browse_file(drop_label),
            bg=BTN_COLOR, fg=TEXT_LIGHT, relief="flat", cursor="hand2",
            font=("Segoe UI", 10), padx=12, pady=5
        ).pack(pady=(0, 15))

    def _on_drop(self, event, label):
        path = event.data.strip("{}")
        label.config(text=f"📄  {os.path.basename(path)}", fg=TEXT_LIGHT)
        self.file_info.set(f"Path: {path}  |  Size: {os.path.getsize(path):,} bytes")

    def _browse_file(self, label):
        path = filedialog.askopenfilename()
        if path:
            label.config(text=f"📄  {os.path.basename(path)}", fg=TEXT_LIGHT)
            self.file_info.set(f"Path: {path}  |  Size: {os.path.getsize(path):,} bytes")

    # ── Internet Tab ────────────────────────────────────────
    def _tab_internet(self, nb):
        frame = tk.Frame(nb, bg=BG_PANEL)
        nb.add(frame, text="  🌐 Internet  ")

        tk.Label(frame, text="Fetch a URL:", bg=BG_PANEL,
                 fg=TEXT_LIGHT, font=("Segoe UI", 11)).pack(anchor="w", padx=10, pady=(15, 2))

        row = tk.Frame(frame, bg=BG_PANEL)
        row.pack(fill="x", padx=10, pady=5)

        self.url_var = tk.StringVar(value="https://httpbin.org/json")
        tk.Entry(row, textvariable=self.url_var, bg="#181825", fg=TEXT_LIGHT,
                 insertbackground=ACCENT, relief="flat", font=("Consolas", 10)
                 ).pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=4)

        tk.Button(row, text="Fetch", command=self._fetch_url,
                  bg=ACCENT, fg="white", relief="flat", cursor="hand2",
                  font=("Segoe UI", 10), padx=10
                  ).pack(side="right")

        self.net_result = tk.Text(
            frame, bg="#181825", fg=TEXT_LIGHT, font=("Consolas", 10),
            relief="flat", state="disabled", padx=8, pady=6
        )
        self.net_result.pack(fill="both", expand=True, padx=10, pady=10)

        if not HAS_REQUESTS:
            self._append_net("⚠  'requests' library not installed. Run:  pip install requests")

    def _fetch_url(self):
        if not HAS_REQUESTS:
            messagebox.showwarning("Missing Library", "Install 'requests' first:\npip install requests")
            return
        url = self.url_var.get().strip()
        self._append_net(f"→ Fetching {url} …")
        threading.Thread(target=self._do_fetch, args=(url,), daemon=True).start()

    def _do_fetch(self, url):
        try:
            r = requests.get(url, timeout=10)
            self._append_net(f"✔  Status {r.status_code}\n{r.text[:1000]}")
        except Exception as e:
            self._append_net(f"✘  Error: {e}")

    def _append_net(self, text):
        self.net_result.config(state="normal")
        self.net_result.insert("end", text + "\n" + "─"*60 + "\n")
        self.net_result.see("end")
        self.net_result.config(state="disabled")

    # ── About Tab ───────────────────────────────────────────
    def _tab_about(self, nb):
        frame = tk.Frame(nb, bg=BG_PANEL)
        nb.add(frame, text="  ℹ About  ")

        about_text = f"""
  {APP_NAME}

  A demonstration application for PythonEXEBuilder.

  ┌─────────────────────────────────────────────────┐
  │   Features demonstrated:                        │
  │   • Dark-mode Tkinter UI                        │
  │   • Local JSON storage (auto-save)              │
  │   • File drag & drop                            │
  │   • Internet API fetch (requests)               │
  │   • Multi-tab notebook layout                   │
  └─────────────────────────────────────────────────┘

  Developed By  : {DEVELOPER}
  Build Tool    : PythonEXEBuilder v1.0.0
  Python        : {sys.version.split()[0]}
  Platform      : {sys.platform}
"""
        tk.Label(frame, text=about_text, bg=BG_PANEL, fg=TEXT_LIGHT,
                 font=("Consolas", 11), justify="left").pack(padx=20, pady=20, anchor="w")

    # ── State ────────────────────────────────────────────────
    def _load_state(self):
        if self.data.get("notes"):
            self.txt_notes.insert("1.0", self.data["notes"])

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    App().run()
