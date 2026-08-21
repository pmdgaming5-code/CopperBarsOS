#!/usr/bin/env python3
"""CopperBars Updates: safe graphical APT update manager."""
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

BG = "#0e1116"
PANEL = "#151a21"
TEXT = "#edf2f7"
MUTED = "#9aa5b1"
ACCENT = "#e38b24"


class CopperBarsUpdates(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CopperBars Updates — CopperBarsOS")
        self.geometry("900x620")
        self.minsize(680, 460)
        self.configure(bg=BG)
        tk.Label(self, text="CopperBars Updates", bg=BG, fg=ACCENT,
                 font=("DejaVu Sans", 25, "bold")).pack(pady=(22, 3))
        tk.Label(self, text="Sistem güncellemelerini kontrol et ve güvenli şekilde kur",
                 bg=BG, fg=MUTED).pack(pady=(0, 14))
        self.out = scrolledtext.ScrolledText(self, bg=PANEL, fg=TEXT, relief=tk.FLAT,
                                             wrap=tk.WORD, font=("DejaVu Sans", 10))
        self.out.pack(fill=tk.BOTH, expand=True, padx=24, pady=10)
        self.out.configure(state=tk.DISABLED)
        row = tk.Frame(self, bg=BG)
        row.pack(fill=tk.X, padx=24, pady=18)
        self.check_button = tk.Button(row, text="Güncellemeleri Kontrol Et", command=self.check,
                                      bg=ACCENT, fg="#101318", relief=tk.FLAT, padx=16, pady=9)
        self.check_button.pack(side=tk.LEFT)
        self.install_button = tk.Button(row, text="Güncellemeleri Kur", command=self.install,
                                        bg="#444b56", fg=TEXT, relief=tk.FLAT, padx=16, pady=9)
        self.install_button.pack(side=tk.LEFT, padx=10)
        self.check()

    def write(self, text):
        self.out.configure(state=tk.NORMAL)
        self.out.delete("1.0", tk.END)
        self.out.insert(tk.END, text)
        self.out.see(tk.END)
        self.out.configure(state=tk.DISABLED)

    def busy(self, yes):
        state = tk.DISABLED if yes else tk.NORMAL
        self.check_button.configure(state=state)
        self.install_button.configure(state=state)

    def check(self):
        self.busy(True)
        self.write("Paket listeleri güncelleniyor…\n")
        threading.Thread(target=self._check, daemon=True).start()

    def _check(self):
        try:
            update = subprocess.run(["pkexec", "apt-get", "update"], text=True,
                                    capture_output=True, timeout=900)
            if update.returncode != 0:
                raise RuntimeError((update.stderr or update.stdout or "APT güncellemesi başarısız.").strip())
            result = subprocess.run(["apt", "list", "--upgradable"], text=True,
                                    capture_output=True, timeout=60)
            text = result.stdout if result.returncode == 0 else result.stderr
            if text.count("/trixie") or text.count("/stable"):
                pass
            self.after(0, lambda: (self.write(text or "Güncelleme bulunamadı."), self.busy(False)))
        except Exception as exc:
            self.after(0, lambda: (self.write(f"Hata: {exc}"), self.busy(False)))

    def install(self):
        if not messagebox.askyesno("CopperBars Updates", "Mevcut paket güncellemeleri kurulsun mu?", parent=self):
            return
        self.busy(True)
        self.write("Güncellemeler kuruluyor…\n")
        threading.Thread(target=self._install, daemon=True).start()

    def _install(self):
        try:
            result = subprocess.run(["pkexec", "apt-get", "-y", "upgrade"], text=True,
                                    capture_output=True, timeout=1800)
            if result.returncode != 0:
                raise RuntimeError((result.stderr or result.stdout or "Güncelleme kurulumu başarısız.").strip())
            self.after(0, lambda: (self.write(result.stdout or "Güncellemeler tamamlandı."), self.busy(False),
                                  messagebox.showinfo("CopperBars Updates", "Güncellemeler tamamlandı.", parent=self)))
        except Exception as exc:
            self.after(0, lambda: (self.write(f"Hata: {exc}"), self.busy(False),
                                  messagebox.showerror("CopperBars Updates", str(exc), parent=self)))


if __name__ == "__main__":
    CopperBarsUpdates().mainloop()
