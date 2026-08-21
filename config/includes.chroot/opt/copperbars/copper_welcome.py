#!/usr/bin/env python3
"""CopperBarsOS first-run setup and local AI model selector."""
import os
import platform
import subprocess
import tkinter as tk
from tkinter import messagebox

BG = "#0e1116"
PANEL = "#171c24"
TEXT = "#edf2f7"
MUTED = "#9aa5b1"
ACCENT = "#e38b24"

MODELS = [
    ("qwen3:1.7b", "Qwen3 1.7B", "~1.4 GB", "Hafif ve düşük RAM'li bilgisayarlar için."),
    ("llama3.2:3b", "Llama 3.2 3B", "~2.0 GB", "Dengeli genel kullanım seçeneği."),
    ("qwen3:4b", "Qwen3 4B", "~2.5 GB", "Daha güçlü Türkçe ve genel kullanım."),
    ("gemma3:4b", "Gemma 3 4B", "~3.3 GB", "Metin + görsel destekli güçlü seçenek."),
]


def ram_gb():
    try:
        with open("/proc/meminfo", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("MemTotal:"):
                    return int(line.split()[1]) / 1024 / 1024
    except Exception:
        pass
    return 0.0


def save_model(name):
    command = ["pkexec", "/bin/sh", "-c", "printf '%s\\n' "$1" > /var/lib/copperbars/model.conf", "copper-model", name]
    result = subprocess.run(command, text=True, capture_output=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "Model ayarı kaydedilemedi.").strip())


def ollama_available():
    return subprocess.run(["sh", "-c", "command -v ollama >/dev/null 2>&1"], capture_output=True).returncode == 0


def pull_model(name):
    if not ollama_available():
        raise RuntimeError("Ollama bu kurulumda bulunamadı. Model seçimi yine kaydedildi; Copper Store üzerinden yerel AI altyapısını kurabilirsin.")
    result = subprocess.run(["ollama", "pull", name], text=True, timeout=3600)
    if result.returncode != 0:
        raise RuntimeError("Model indirilemedi.")


class Welcome(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CopperBarsOS — İlk Kurulum")
        self.geometry("900x650")
        self.minsize(720, 560)
        self.configure(bg=BG)
        self.selected = tk.StringVar(value="qwen3:1.7b")

        tk.Label(self, text="CopperBarsOS", bg=BG, fg=ACCENT,
                 font=("DejaVu Sans", 28, "bold")).pack(pady=(28, 4))
        tk.Label(self, text="Bilgisayarını birkaç adımda hazırla", bg=BG, fg=TEXT,
                 font=("DejaVu Sans", 15, "bold")).pack()
        tk.Label(self, text=f"Algılanan RAM: {ram_gb():.1f} GB • Mimari: {platform.machine()}", bg=BG, fg=MUTED).pack(pady=(5, 20))

        card = tk.Frame(self, bg=PANEL)
        card.pack(fill=tk.BOTH, expand=True, padx=34, pady=10)
        tk.Label(card, text="İlk Copper AI modelini seç", bg=PANEL, fg=TEXT,
                 font=("DejaVu Sans", 16, "bold")).pack(anchor="w", padx=22, pady=(20, 5))
        tk.Label(card, text="Model dosyaları Git'e gömülmez; seçtiğin model yerel olarak kullanılmak üzere ayarlanır.",
                 bg=PANEL, fg=MUTED, wraplength=780, justify="left").pack(anchor="w", padx=22, pady=(0, 12))

        for model_id, title, size, desc in MODELS:
            row = tk.Frame(card, bg="#11161d")
            row.pack(fill=tk.X, padx=20, pady=5)
            tk.Radiobutton(row, variable=self.selected, value=model_id, bg="#11161d", fg=TEXT,
                           selectcolor="#11161d", activebackground="#11161d", activeforeground=TEXT,
                           font=("DejaVu Sans", 11, "bold"), text=f"{title}  •  {size}").pack(anchor="w", padx=14, pady=(10, 0))
            tk.Label(row, text=desc, bg="#11161d", fg=MUTED).pack(anchor="w", padx=43, pady=(0, 10))

        buttons = tk.Frame(self, bg=BG)
        buttons.pack(fill=tk.X, padx=34, pady=20)
        tk.Button(buttons, text="Seçimi Kaydet", command=self.save_only, bg=ACCENT,
                  fg="#101318", relief=tk.FLAT, padx=18, pady=10).pack(side=tk.LEFT)
        tk.Button(buttons, text="Seç ve Modeli İndir", command=self.save_and_pull, bg="#555d68",
                  fg=TEXT, relief=tk.FLAT, padx=18, pady=10).pack(side=tk.LEFT, padx=10)
        tk.Button(buttons, text="Daha Sonra", command=self.destroy, bg=BG,
                  fg=MUTED, relief=tk.FLAT, padx=18, pady=10).pack(side=tk.RIGHT)

    def save_only(self):
        try:
            save_model(self.selected.get())
            messagebox.showinfo("CopperBarsOS", f"{self.selected.get()} seçildi. Copper yeniden başlatıldığında bu modeli kullanacak.")
            self.destroy()
        except Exception as exc:
            messagebox.showerror("CopperBarsOS", str(exc))

    def save_and_pull(self):
        try:
            save_model(self.selected.get())
            pull_model(self.selected.get())
            messagebox.showinfo("CopperBarsOS", "Model kuruldu ve Copper için seçildi.")
            self.destroy()
        except Exception as exc:
            messagebox.showerror("CopperBarsOS", str(exc))


if __name__ == "__main__":
    Welcome().mainloop()
