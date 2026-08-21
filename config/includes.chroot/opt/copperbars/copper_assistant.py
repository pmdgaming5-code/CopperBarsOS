#!/usr/bin/env python3
import json
import tkinter as tk
from tkinter import scrolledtext
from urllib.request import Request, urlopen

API = "http://127.0.0.1:8765/chat"

class CopperAssistant(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Copper — CopperBarsOS Assistant")
        self.geometry("900x620")
        self.minsize(640, 440)
        self.configure(bg="#101318")

        tk.Label(self, text="CopperBarsOS", fg="#f39c12", bg="#101318", font=("DejaVu Sans", 22, "bold")).pack(pady=(18, 2))
        tk.Label(self, text="Yerel AI Yardımcısı", fg="#c8ced8", bg="#101318", font=("DejaVu Sans", 11)).pack(pady=(0, 12))

        self.chat = scrolledtext.ScrolledText(self, wrap=tk.WORD, bg="#181c23", fg="#eef2f7", insertbackground="white", font=("DejaVu Sans", 11), borderwidth=0)
        self.chat.pack(fill=tk.BOTH, expand=True, padx=18, pady=8)
        self.chat.insert(tk.END, "Copper: Merhaba! Ben Copper. CopperBarsOS'u kullanmana yardımcı olabilirim.\n\n")
        self.chat.configure(state=tk.DISABLED)

        row = tk.Frame(self, bg="#101318")
        row.pack(fill=tk.X, padx=18, pady=18)
        self.entry = tk.Entry(row, bg="#181c23", fg="white", insertbackground="white", font=("DejaVu Sans", 11), relief=tk.FLAT)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10)
        self.entry.bind("<Return>", lambda _e: self.send())
        tk.Button(row, text="Gönder", command=self.send, bg="#f39c12", fg="#101318", relief=tk.FLAT, padx=18, pady=8).pack(side=tk.RIGHT, padx=(10, 0))
        self.entry.focus_set()

    def add(self, text):
        self.chat.configure(state=tk.NORMAL)
        self.chat.insert(tk.END, text + "\n\n")
        self.chat.see(tk.END)
        self.chat.configure(state=tk.DISABLED)

    def send(self):
        message = self.entry.get().strip()
        if not message:
            return
        self.entry.delete(0, tk.END)
        self.add("Sen: " + message)
        try:
            body = json.dumps({"message": message}).encode()
            req = Request(API, data=body, headers={"Content-Type": "application/json"}, method="POST")
            with urlopen(req, timeout=125) as response:
                answer = json.loads(response.read().decode()).get("answer", "Yanıt alınamadı.")
        except Exception as exc:
            answer = "Copper AI servisine bağlanamadım. Servis durumunu kontrol et. (" + str(exc) + ")"
        self.add("Copper: " + answer)

if __name__ == "__main__":
    CopperAssistant().mainloop()
