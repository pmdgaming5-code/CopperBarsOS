#!/usr/bin/env python3
"""CopperBars Diagnostics: read-only system health checker."""
import shutil
import subprocess
import tkinter as tk
from tkinter import scrolledtext

BG = "#0e1116"
PANEL = "#151a21"
TEXT = "#edf2f7"
MUTED = "#9aa5b1"
ACCENT = "#e38b24"


def command(*args):
    try:
        result = subprocess.run(args, text=True, capture_output=True, timeout=12)
        return (result.stdout or result.stderr).strip()
    except Exception as exc:
        return str(exc)


def check_service(name):
    return command("systemctl", "is-active", name) or "unknown"


def report():
    lines = [
        "CopperBars Diagnostics",
        "=" * 28,
        f"Copperium AI service: {check_service('copper-ai.service')}",
        f"First boot service: {check_service('copper-firstboot.service')}",
        f"Wine: {'OK' if shutil.which('wine') else 'MISSING'}",
        f"Wineboot: {'OK' if shutil.which('wineboot') else 'MISSING'}",
        f"Winetricks: {'OK' if shutil.which('winetricks') else 'MISSING'}",
        f"DXVK: {'OK' if shutil.which('wine') and shutil.which('vulkaninfo') else 'CHECK GPU'}",
        "",
        "Disk:",
        command("df", "-h", "/"),
        "",
        "Memory:",
        command("sh", "-c", "free -h"),
        "",
        "Graphics:",
        command("sh", "-c", "inxi -G 2>/dev/null || true"),
        "",
        "Network:",
        command("sh", "-c", "nmcli -t -f DEVICE,TYPE,STATE dev 2>/dev/null || true"),
    ]
    return "\n".join(lines)


class CopperBarsDiagnostics(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CopperBars Diagnostics — CopperBarsOS")
        self.geometry("900x680")
        self.minsize(680, 500)
        self.configure(bg=BG)
        tk.Label(self, text="CopperBars Diagnostics", bg=BG, fg=ACCENT,
                 font=("DejaVu Sans", 25, "bold")).pack(pady=(22, 3))
        tk.Label(self, text="Salt okunur sistem sağlık ve uyumluluk kontrolü",
                 bg=BG, fg=MUTED).pack(pady=(0, 14))
        self.out = scrolledtext.ScrolledText(self, bg=PANEL, fg=TEXT, relief=tk.FLAT,
                                             wrap=tk.WORD, font=("DejaVu Sans", 10))
        self.out.pack(fill=tk.BOTH, expand=True, padx=24, pady=10)
        self.out.insert(tk.END, report())
        self.out.configure(state=tk.DISABLED)
        tk.Button(self, text="Yeniden Tara", command=self.refresh, bg=ACCENT, fg="#101318",
                  relief=tk.FLAT, padx=18, pady=9).pack(anchor="e", padx=24, pady=(0, 18))

    def refresh(self):
        self.out.configure(state=tk.NORMAL)
        self.out.delete("1.0", tk.END)
        self.out.insert(tk.END, report())
        self.out.configure(state=tk.DISABLED)


if __name__ == "__main__":
    CopperBarsDiagnostics().mainloop()
