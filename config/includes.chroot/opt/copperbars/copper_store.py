#!/usr/bin/env python3
"""Copper Store: curated software center for CopperBarsOS."""
import json
import os
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox

ROOT = "/opt/copperbars"
CATALOG = os.path.join(ROOT, "apps.json")
BG = "#0e1116"
PANEL = "#171c24"
PANEL2 = "#11161d"
TEXT = "#edf2f7"
MUTED = "#9aa5b1"
ACCENT = "#e38b24"


def load_catalog():
    with open(CATALOG, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError("Geçersiz Copper Store kataloğu")
    for app in data:
        if not isinstance(app, dict) or not app.get("id") or not app.get("name") or not app.get("package"):
            raise ValueError("Geçersiz uygulama kaydı")
    return data


def apt_installed(package):
    result = subprocess.run(["dpkg-query", "-W", "-f=${Status}", package], text=True, capture_output=True)
    return result.returncode == 0 and result.stdout.strip() == "install ok installed"


def run_privileged(action, package):
    if action not in {"install", "remove"}:
        raise ValueError("Geçersiz işlem")
    return subprocess.run(
        ["pkexec", "apt-get", "-y", "--no-install-recommends", action, package],
        text=True,
        capture_output=True,
        timeout=900,
    )


class CopperStore(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Copper Store — CopperBarsOS")
        self.geometry("1040x720")
        self.minsize(820, 560)
        self.configure(bg=BG)
        self.apps = load_catalog()
        self.filtered = list(self.apps)

        header = tk.Frame(self, bg=BG)
        header.pack(fill=tk.X, padx=24, pady=(22, 10))
        tk.Label(header, text="Copper Store", bg=BG, fg=ACCENT,
                 font=("DejaVu Sans", 27, "bold")).pack(anchor="w")
        tk.Label(header, text="Güvenilir ve seçilmiş Linux uygulamaları", bg=BG, fg=MUTED,
                 font=("DejaVu Sans", 11)).pack(anchor="w", pady=(2, 12))

        bar = tk.Frame(header, bg=BG)
        bar.pack(fill=tk.X)
        self.search = tk.Entry(bar, bg=PANEL2, fg=TEXT, insertbackground=TEXT,
                                relief=tk.FLAT, font=("DejaVu Sans", 11))
        self.search.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10)
        self.search.insert(0, "Uygulama ara...")
        self.search.bind("<KeyRelease>", lambda _e: self.refresh_list())

        self.category = tk.StringVar(value="Tümü")
        cats = ["Tümü"] + sorted({a["category"] for a in self.apps})
        tk.OptionMenu(bar, self.category, *cats, command=lambda _v: self.refresh_list()).pack(side=tk.LEFT, padx=(10, 0))

        self.list_frame = tk.Frame(self, bg=BG)
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=10)
        self.refresh_list()

        tk.Label(self, text="Uygulamalar sistemin APT altyapısından kurulur. Mağaza yalnızca doğrulanmış katalog paketlerini çağırır.",
                 bg=BG, fg=MUTED, anchor="w").pack(fill=tk.X, padx=24, pady=(0, 14))

    def refresh_list(self):
        query = self.search.get().strip().lower()
        if query == "uygulama ara...":
            query = ""
        category = self.category.get()
        self.filtered = [
            a for a in self.apps
            if (category == "Tümü" or a["category"] == category)
            and (not query or query in (a["name"] + " " + a["description"] + " " + a["category"]).lower())
        ]
        for child in self.list_frame.winfo_children():
            child.destroy()
        canvas = tk.Canvas(self.list_frame, bg=BG, highlightthickness=0)
        scroll = tk.Scrollbar(self.list_frame, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg=BG)
        content.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        for app in self.filtered:
            self.render_app(content, app)

    def render_app(self, parent, app):
        card = tk.Frame(parent, bg=PANEL, highlightthickness=1, highlightbackground="#29313d")
        card.pack(fill=tk.X, pady=6)
        left = tk.Frame(card, bg=PANEL)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=16, pady=14)
        tk.Label(left, text=app["name"], bg=PANEL, fg=TEXT,
                 font=("DejaVu Sans", 14, "bold")).pack(anchor="w")
        tk.Label(left, text=f"{app['category']} • {app['package']}", bg=PANEL, fg=ACCENT,
                 font=("DejaVu Sans", 9, "bold")).pack(anchor="w", pady=(2, 5))
        tk.Label(left, text=app["description"], bg=PANEL, fg=MUTED,
                 wraplength=650, justify="left", anchor="w").pack(anchor="w")

        installed = apt_installed(app["package"])
        button = tk.Button(card, text="Kaldır" if installed else "Kur",
                           command=lambda a=app, i=installed: self.change(a, i),
                           bg="#555d68" if installed else ACCENT,
                           fg=TEXT if installed else "#101318", relief=tk.FLAT,
                           padx=18, pady=9)
        button.pack(side=tk.RIGHT, padx=18)

    def change(self, app, installed):
        self.config(cursor="watch")
        self.update_idletasks()
        def worker():
            try:
                result = run_privileged("remove" if installed else "install", app["package"])
                if result.returncode != 0:
                    raise RuntimeError((result.stderr or result.stdout or "APT işlemi başarısız.").strip())
                self.after(0, lambda: (self.config(cursor=""), self.refresh_list()))
            except Exception as exc:
                self.after(0, lambda: (self.config(cursor=""), messagebox.showerror("Copper Store", str(exc))))
        threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    CopperStore().mainloop()
