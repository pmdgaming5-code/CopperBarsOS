#!/usr/bin/env python3
"""Copper Windows Compatibility Center."""
import os
import pathlib
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog

BG = "#0e1116"
PANEL2 = "#11161d"
TEXT = "#edf2f7"
MUTED = "#9aa5b1"
ACCENT = "#e38b24"
BASE = pathlib.Path.home() / ".local" / "share" / "copperbars" / "wine"


def wine_available():
    return shutil.which("wine") is not None


def run(cmd, env=None, timeout=180):
    return subprocess.run(cmd, text=True, capture_output=True, env=env, timeout=timeout)


def prefix_for(name):
    safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in name).strip(".") or "default"
    return BASE / safe


def init_prefix(prefix):
    env = os.environ.copy()
    env["WINEPREFIX"] = str(prefix)
    env["WINEARCH"] = "win64"
    prefix.mkdir(parents=True, exist_ok=True)
    result = run(["wineboot", "-u"], env=env)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Wine prefix oluşturulamadı.")
    return env


class WindowsCenter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Windows Uyumluluğu — CopperBarsOS")
        self.geometry("980x680")
        self.minsize(760, 520)
        self.configure(bg=BG)
        BASE.mkdir(parents=True, exist_ok=True)

        tk.Label(self, text="Windows Uyumluluğu", bg=BG, fg=ACCENT,
                 font=("DejaVu Sans", 25, "bold")).pack(pady=(22, 3))
        tk.Label(self, text="Wine + DXVK + 32/64-bit Windows uygulama desteği",
                 bg=BG, fg=MUTED).pack(pady=(0, 14))

        actions = tk.Frame(self, bg=BG)
        actions.pack(fill=tk.X, padx=24, pady=8)
        self.button(actions, "EXE Aç", self.choose_exe).pack(side=tk.LEFT)
        self.button(actions, "Prefix Oluştur", self.new_prefix).pack(side=tk.LEFT, padx=10)
        self.button(actions, "Winetricks", self.open_winetricks).pack(side=tk.LEFT)
        self.button(actions, "Yenile", self.refresh).pack(side=tk.RIGHT)

        self.list_box = scrolledtext.ScrolledText(self, bg=PANEL2, fg=TEXT, relief=tk.FLAT,
                                                  font=("DejaVu Sans", 10), wrap=tk.WORD)
        self.list_box.pack(fill=tk.BOTH, expand=True, padx=24, pady=12)
        self.list_box.configure(state=tk.DISABLED)
        self.status = tk.Label(self, bg=BG, fg=MUTED, anchor="w")
        self.status.pack(fill=tk.X, padx=24, pady=(0, 14))
        self.refresh()

    def button(self, parent, text, command):
        return tk.Button(parent, text=text, command=command, bg=ACCENT, fg="#101318",
                         relief=tk.FLAT, padx=16, pady=9, cursor="hand2")

    def write(self, text):
        self.list_box.configure(state=tk.NORMAL)
        self.list_box.delete("1.0", tk.END)
        self.list_box.insert(tk.END, text)
        self.list_box.configure(state=tk.DISABLED)

    def refresh(self):
        if not wine_available():
            self.write("Wine kurulu değil. Copper Store üzerinden Wine Windows Uyumluluğu paketini kurun.")
            return
        prefixes = sorted(p for p in BASE.iterdir() if p.is_dir())
        lines = [
            "CopperBarsOS Windows Uyumluluk Katmanı",
            "",
            "Wine: kullanılabilir",
            "32/64-bit desteği: Wine multiarch kurulumu tanımlı",
            "Direct3D 8/9/10/11: DXVK",
            "Direct3D 12: vkd3d kitaplıkları",
            f"Prefix sayısı: {len(prefixes)}",
            "",
        ]
        for prefix in prefixes:
            lines.append(f"• {prefix.name}  →  {prefix}")
        if not prefixes:
            lines.append("Henüz prefix yok. 'Prefix Oluştur' ile izole bir Windows ortamı oluşturabilirsin.")
        self.write("\n".join(lines))
        self.status.configure(text="Hazır")

    def new_prefix(self):
        name = simpledialog.askstring("Wine Prefix", "Prefix adı:", initialvalue="WindowsApp", parent=self)
        if not name:
            return
        prefix = prefix_for(name)
        try:
            init_prefix(prefix)
            messagebox.showinfo("Wine", f"Prefix oluşturuldu:\n{prefix}")
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Wine", str(exc))

    def choose_exe(self):
        path = filedialog.askopenfilename(title="Windows uygulaması seç",
                                          filetypes=[("Windows EXE", "*.exe"), ("Tüm dosyalar", "*")])
        if path:
            threading.Thread(target=self.launch_exe, args=(path,), daemon=True).start()

    def launch_exe(self, path):
        try:
            if not wine_available():
                raise RuntimeError("Wine kurulu değil. Copper Store'dan Wine paketini kur.")
            app_name = pathlib.Path(path).stem
            env = init_prefix(prefix_for(app_name))
            result = run(["wine", path], env=env, timeout=7200)
            if result.returncode != 0:
                raise RuntimeError(result.stderr.strip() or f"Windows uygulaması çıkış kodu: {result.returncode}")
            self.after(0, lambda: self.status.configure(text=f"Çalıştırıldı: {pathlib.Path(path).name}"))
        except subprocess.TimeoutExpired:
            self.after(0, lambda: self.status.configure(text="Uygulama çalışmaya devam ediyor."))
        except Exception as exc:
            self.after(0, lambda: messagebox.showerror("Windows Uyumluluğu", str(exc)))

    def open_winetricks(self):
        if shutil.which("winetricks") is None:
            messagebox.showerror("Winetricks", "Winetricks kurulu değil.")
            return
        subprocess.Popen(["winetricks"])


if __name__ == "__main__":
    WindowsCenter().mainloop()
