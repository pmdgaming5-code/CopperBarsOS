#!/usr/bin/env python3
"""CopperBars Center: central control panel for CopperBarsOS."""
import json
import os
import platform
import subprocess
import tkinter as tk
from tkinter import messagebox, scrolledtext
from urllib.request import urlopen

API = "http://127.0.0.1:8765/health"
BG = "#0e1116"
PANEL = "#171c24"
TEXT = "#edf2f7"
MUTED = "#9aa5b1"
ACCENT = "#e38b24"


def run(cmd):
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT, timeout=8).strip()
    except Exception as exc:
        return f"Komut çalıştırılamadı: {exc}"


class CopperBarsCenter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CopperBars Center — CopperBarsOS")
        self.geometry("1040x720")
        self.minsize(800, 560)
        self.configure(bg=BG)
        self.boxes = {}

        tk.Label(self, text="CopperBars Center", bg=BG, fg=ACCENT,
                 font=("DejaVu Sans", 27, "bold")).pack(pady=(22, 3))
        tk.Label(self, text="CopperBarsOS sistem ve AI merkezi", bg=BG, fg=MUTED,
                 font=("DejaVu Sans", 11)).pack(pady=(0, 16))

        body = tk.Frame(self, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, padx=22, pady=8)
        self.card(body, "Copperium AI", self.ai_status, 0, 0)
        self.card(body, "Sistem", self.system_info, 0, 1)
        self.card(body, "Donanım", self.hardware_info, 1, 0)
        self.card(body, "Ağ", self.network_info, 1, 1)

        buttons = tk.Frame(self, bg=BG)
        buttons.pack(fill=tk.X, padx=22, pady=14)
        self.button(buttons, "Copperium AI", self.open_ai).pack(side=tk.LEFT)
        self.button(buttons, "AI Modeli", self.model_setup).pack(side=tk.LEFT, padx=8)
        self.button(buttons, "Windows", self.windows_center).pack(side=tk.LEFT, padx=8)
        self.button(buttons, "Güncellemeler", self.updates).pack(side=tk.LEFT, padx=8)
        self.button(buttons, "Tanılama", self.diagnostics).pack(side=tk.LEFT, padx=8)
        self.button(buttons, "Kurulum", self.launch_installer).pack(side=tk.LEFT, padx=8)
        self.button(buttons, "Yenile", self.refresh).pack(side=tk.RIGHT)

        self.status = tk.Label(self, text="Hazır", bg=BG, fg=MUTED, anchor="w")
        self.status.pack(fill=tk.X, padx=24, pady=(0, 12))
        self.refresh()

    def card(self, parent, title, func, row, column):
        frame = tk.Frame(parent, bg=PANEL, highlightthickness=1, highlightbackground="#29313d")
        frame.grid(row=row, column=column, sticky="nsew", padx=8, pady=8)
        parent.grid_columnconfigure(column, weight=1)
        parent.grid_rowconfigure(row, weight=1)
        tk.Label(frame, text=title, bg=PANEL, fg=TEXT,
                 font=("DejaVu Sans", 14, "bold")).pack(anchor="w", padx=16, pady=(14, 8))
        out = scrolledtext.ScrolledText(frame, bg="#11161d", fg=TEXT, height=9,
                                        wrap=tk.WORD, relief=tk.FLAT, borderwidth=0,
                                        font=("DejaVu Sans", 10))
        out.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        func(out)
        out.configure(state=tk.DISABLED)
        self.boxes[title] = out

    def button(self, parent, text, command):
        return tk.Button(parent, text=text, command=command, bg=ACCENT, fg="#101318",
                         activebackground="#f0a244", activeforeground="#101318",
                         relief=tk.FLAT, padx=13, pady=9, cursor="hand2")

    @staticmethod
    def fill(box, text):
        box.configure(state=tk.NORMAL)
        box.delete("1.0", tk.END)
        box.insert(tk.END, text)
        box.configure(state=tk.DISABLED)

    def ai_status(self, box):
        try:
            with urlopen(API, timeout=3) as response:
                data = json.loads(response.read().decode("utf-8"))
            model = data.get("model") or "Seçilmemiş"
            models = data.get("models") or []
            backend = data.get("backend") or "none"
            reachable = "evet" if data.get("ollama_reachable") else "hayır"
            self.fill(box, f"Servis: ÇALIŞIYOR\nBackend: {backend}\nModel: {model}\nOllama: {reachable}\nGGUF: {len(models)}\n\n{', '.join(models) if models else 'Henüz GGUF modeli yok.'}")
        except Exception as exc:
            self.fill(box, f"Servis: BAĞLANILAMADI\n\n{exc}")

    def system_info(self, box):
        text = (
            f"İşletim sistemi: CopperBarsOS\n"
            f"Mimari: {platform.machine()}\n"
            f"Kernel: {platform.release()}\n"
            f"Python: {platform.python_version()}\n"
            f"Masaüstü: {os.environ.get('XDG_CURRENT_DESKTOP', 'XFCE')}\n"
            f"Disk kökü: {run(['sh', '-c', 'df -h / | tail -1'])}\n"
        )
        self.fill(box, text)

    def hardware_info(self, box):
        self.fill(box, run(["sh", "-c", "inxi -C -G -M 2>/dev/null || true"]))

    def network_info(self, box):
        self.fill(box, run(["sh", "-c", "nmcli -t -f DEVICE,TYPE,STATE dev 2>/dev/null || true"]))

    def refresh(self):
        self.ai_status(self.boxes["Copperium AI"])
        self.system_info(self.boxes["Sistem"])
        self.hardware_info(self.boxes["Donanım"])
        self.network_info(self.boxes["Ağ"])
        self.status.configure(text="Bilgiler yenilendi")

    def open_ai(self):
        subprocess.Popen(["/usr/bin/python3", "/opt/copperbars/copper_assistant.py"])

    def model_setup(self):
        subprocess.Popen(["/usr/bin/python3", "/opt/copperbars/copper_welcome.py"])

    def windows_center(self):
        subprocess.Popen(["/usr/bin/python3", "/opt/copperbars/copper_windows.py"])

    def updates(self):
        subprocess.Popen(["/usr/bin/python3", "/opt/copperbars/copper_updates.py"])

    def diagnostics(self):
        subprocess.Popen(["/usr/bin/python3", "/opt/copperbars/copper_diagnostics.py"])

    def launch_installer(self):
        try:
            subprocess.Popen(["pkexec", "calamares"])
        except Exception as exc:
            messagebox.showerror("CopperBars Kurulum", str(exc))


if __name__ == "__main__":
    CopperBarsCenter().mainloop()
