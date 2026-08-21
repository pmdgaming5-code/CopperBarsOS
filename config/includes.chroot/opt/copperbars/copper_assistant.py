#!/usr/bin/env python3
"""Copperium AI native chat window for CopperBarsOS."""
import json
import pathlib
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from urllib.error import URLError
from urllib.request import Request, urlopen

CHAT_API = "http://127.0.0.1:8765/chat"
HEALTH_API = "http://127.0.0.1:8765/health"
HISTORY = pathlib.Path.home() / ".config" / "copperbars" / "copperium-history.json"
BG = "#0b0e13"
PANEL = "#151a21"
TEXT = "#eef2f7"
MUTED = "#9aa5b1"
ACCENT = "#e38b24"


class CopperiumAI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Copperium AI — CopperBarsOS")
        self.geometry("980x720")
        self.minsize(720, 520)
        self.configure(bg=BG)
        self.busy = False
        self.history = self.load_history()

        header = tk.Frame(self, bg=BG)
        header.pack(fill=tk.X, padx=24, pady=(22, 10))
        tk.Label(header, text="Copperium AI", fg=ACCENT, bg=BG,
                 font=("DejaVu Sans", 26, "bold")).pack(side=tk.LEFT)
        self.status = tk.Label(header, text="Yerel model kontrol ediliyor…", fg=MUTED, bg=BG,
                               font=("DejaVu Sans", 10))
        self.status.pack(side=tk.RIGHT, pady=(10, 0))

        toolbar = tk.Frame(self, bg=BG)
        toolbar.pack(fill=tk.X, padx=24)
        tk.Button(toolbar, text="Geçmişi Temizle", command=self.clear_history,
                  bg="#343b46", fg=TEXT, relief=tk.FLAT, padx=12, pady=6).pack(side=tk.RIGHT)

        self.chat = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, bg=PANEL, fg=TEXT, insertbackground="white",
            font=("DejaVu Sans", 11), relief=tk.FLAT, borderwidth=0,
            padx=14, pady=14,
        )
        self.chat.pack(fill=tk.BOTH, expand=True, padx=24, pady=8)
        self.chat.configure(state=tk.DISABLED)

        if self.history:
            for item in self.history[-80:]:
                self.add(item.get("speaker", "Copperium AI"), item.get("text", ""), save=False)
        else:
            self.add("Copperium AI", "Merhaba! Ben Copperium AI. CopperBarsOS'u kurmana, ayarlamana ve kullanmana yardımcı olabilirim.")
            self.add("Copperium AI", "Yerel model bağlı değilse bunu açıkça belirtirim ve olmayan yetenekleri varmış gibi göstermem.")

        row = tk.Frame(self, bg=BG)
        row.pack(fill=tk.X, padx=24, pady=(8, 22))
        self.entry = tk.Entry(row, bg=PANEL, fg=TEXT, insertbackground="white",
                              font=("DejaVu Sans", 11), relief=tk.FLAT)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=12)
        self.entry.bind("<Return>", lambda _event: self.send())
        self.send_button = tk.Button(
            row, text="Gönder", command=self.send, bg=ACCENT, fg="#101318",
            activebackground="#f2a44b", relief=tk.FLAT, padx=20, pady=9,
        )
        self.send_button.pack(side=tk.RIGHT, padx=(10, 0))
        self.entry.focus_set()
        self.after(250, self.check_health)

    def load_history(self):
        try:
            data = json.loads(HISTORY.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (OSError, ValueError):
            return []

    def save_history(self):
        try:
            HISTORY.parent.mkdir(parents=True, exist_ok=True)
            HISTORY.write_text(json.dumps(self.history[-200:], ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            pass

    def add(self, speaker, text, save=True):
        self.chat.configure(state=tk.NORMAL)
        self.chat.insert(tk.END, f"{speaker}: {text}\n\n")
        self.chat.see(tk.END)
        self.chat.configure(state=tk.DISABLED)
        if save:
            self.history.append({"speaker": speaker, "text": text})
            self.save_history()

    def clear_history(self):
        self.history = []
        self.chat.configure(state=tk.NORMAL)
        self.chat.delete("1.0", tk.END)
        self.chat.configure(state=tk.DISABLED)
        self.add("Copperium AI", "Yeni bir sohbet başlattık.")

    def check_health(self):
        def worker():
            try:
                with urlopen(HEALTH_API, timeout=4) as response:
                    data = json.loads(response.read().decode())
                model = data.get("model") or "model seçilmedi"
                reachable = data.get("ollama_reachable", False)
                status = f"Copperium AI • {model}"
                if model and not reachable:
                    status += " • model servisi bekleniyor"
            except Exception:
                status = "Copperium AI • servis bekleniyor"
            self.after(0, lambda: self.status.configure(text=status))
        threading.Thread(target=worker, daemon=True).start()

    def send(self):
        if self.busy:
            return
        message = self.entry.get().strip()
        if not message:
            return
        self.entry.delete(0, tk.END)
        self.add("Sen", message)
        self.busy = True
        self.send_button.configure(state=tk.DISABLED, text="Yanıtlanıyor…")
        threading.Thread(target=self._request, args=(message,), daemon=True).start()

    def _request(self, message):
        answer = None
        error = None
        try:
            body = json.dumps({"message": message}, ensure_ascii=False).encode("utf-8")
            req = Request(CHAT_API, data=body,
                          headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
            with urlopen(req, timeout=180) as response:
                data = json.loads(response.read().decode("utf-8"))
            answer = data.get("answer") or "Yanıt alınamadı."
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            error = f"Copperium AI servisine ulaşılamadı: {exc}"
        except Exception as exc:
            error = f"Beklenmeyen hata: {exc}"

        def finish():
            self.add("Copperium AI", answer if answer is not None else error)
            self.busy = False
            self.send_button.configure(state=tk.NORMAL, text="Gönder")
            self.entry.focus_set()
            self.check_health()
        self.after(0, finish)


if __name__ == "__main__":
    try:
        CopperiumAI().mainloop()
    except tk.TclError as exc:
        messagebox.showerror("CopperBarsOS", str(exc))
