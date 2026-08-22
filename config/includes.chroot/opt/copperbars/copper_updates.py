#!/usr/bin/env python3
"""CopperBars Update Center: APT + GitHub Release updates."""
import hashlib
import json
import pathlib
import re
import subprocess
import tempfile
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BG = "#0e1116"
PANEL = "#151a21"
TEXT = "#edf2f7"
MUTED = "#9aa5b1"
ACCENT = "#e38b24"
REPO = "pmdgaming5-code/CopperBarsOS"
RELEASE_API = f"https://api.github.com/repos/{REPO}/releases/latest"
VERSION_FILE = pathlib.Path("/opt/copperbars/version")
INSTALL_HELPER = "/usr/local/bin/copperbars-release-updater"
MAX_RELEASE_BYTES = 1024 * 1024 * 1024


def parse_version(text: str):
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", text.strip())
    if not match:
        raise ValueError(f"Geçersiz sürüm: {text!r}")
    return tuple(int(x) for x in match.groups())


def local_version():
    try:
        return VERSION_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        return "0.0.0"


def github_release():
    request = Request(
        RELEASE_API,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "CopperBarsOS-Updater/1.0",
        },
    )
    with urlopen(request, timeout=15) as response:
        return json.load(response)


def choose_asset(release, suffix):
    for asset in release.get("assets", []):
        name = asset.get("name", "")
        if name.endswith(suffix):
            return asset
    return None


def download(url, destination):
    request = Request(url, headers={"User-Agent": "CopperBarsOS-Updater/1.0"})
    with urlopen(request, timeout=60) as response, open(destination, "wb") as out:
        total = 0
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_RELEASE_BYTES:
                raise RuntimeError("Güncelleme paketi izin verilen boyutu aşıyor.")
            out.write(chunk)
    return total


def verify_sha256(path, checksum_path):
    tokens = checksum_path.read_text(encoding="utf-8").strip().split()
    if not tokens:
        raise RuntimeError("Checksum dosyası boş.")
    expected = tokens[0].lower()
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    actual = digest.hexdigest().lower()
    if actual != expected:
        raise RuntimeError("SHA-256 doğrulaması başarısız. Dosya silindi ve kurulmadı.")
    return actual


class CopperBarsUpdates(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CopperBars Update — CopperBarsOS")
        self.geometry("980x700")
        self.minsize(720, 520)
        self.configure(bg=BG)
        self.busy_state = False
        self.release = None

        tk.Label(self, text="CopperBars Update", bg=BG, fg=ACCENT,
                 font=("DejaVu Sans", 26, "bold")).pack(pady=(22, 3))
        tk.Label(self, text="APT paketlerini ve GitHub sürümlerini güvenli biçimde yönet",
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
        self.install_button = tk.Button(row, text="OS Güncellemesini İndir ve Kur", command=self.install_release,
                                        bg="#555d68", fg=TEXT, relief=tk.FLAT, padx=16, pady=9)
        self.install_button.pack(side=tk.LEFT, padx=10)
        self.apt_button = tk.Button(row, text="Paket Güncellemelerini Kur", command=self.install_apt,
                                    bg="#303741", fg=TEXT, relief=tk.FLAT, padx=16, pady=9)
        self.apt_button.pack(side=tk.LEFT)

        self.status = tk.Label(self, text="Hazır", bg=BG, fg=MUTED, anchor="w")
        self.status.pack(fill=tk.X, padx=24, pady=(0, 12))
        self.check()

    def write(self, text):
        self.out.configure(state=tk.NORMAL)
        self.out.delete("1.0", tk.END)
        self.out.insert(tk.END, text)
        self.out.see(tk.END)
        self.out.configure(state=tk.DISABLED)

    def set_busy(self, value):
        self.busy_state = value
        state = tk.DISABLED if value else tk.NORMAL
        self.check_button.configure(state=state)
        self.install_button.configure(state=state)
        self.apt_button.configure(state=state)

    def check(self):
        if self.busy_state:
            return
        self.set_busy(True)
        self.write("CopperBars Update kontrol ediliyor…\n\n")
        threading.Thread(target=self._check, daemon=True).start()

    def _check(self):
        lines = [f"Kurulu CopperBarsOS: {local_version()}"]
        try:
            release = github_release()
            self.release = release
            latest_text = release.get("tag_name", "")
            lines.append(f"GitHub son sürüm: {latest_text or 'yayın yok'}")
            try:
                available = parse_version(latest_text) > parse_version(local_version())
            except ValueError:
                available = False
            lines.append(f"OS sürümü güncel mi: {'HAYIR' if available else 'EVET / bilinmiyor'}")
            bundle = choose_asset(release, "-update.tar.gz")
            checksum = choose_asset(release, "-update.tar.gz.sha256")
            if available and bundle and checksum:
                lines.append(f"Güncelleme paketi: {bundle['name']}")
                lines.append(f"Checksum: {checksum['name']}")
            elif available:
                lines.append("Yeni sürüm var fakat doğrulanabilir güncelleme paketi bu release içinde yok.")
        except (HTTPError, URLError, TimeoutError, ValueError) as exc:
            lines.append(f"GitHub kontrolü başarısız: {exc}")

        try:
            update = subprocess.run(["pkexec", "apt-get", "update"], text=True,
                                    capture_output=True, timeout=900)
            if update.returncode != 0:
                raise RuntimeError((update.stderr or update.stdout or "APT güncellemesi başarısız.").strip())
            result = subprocess.run(["apt", "list", "--upgradable"], text=True,
                                    capture_output=True, timeout=60)
            upgrades = result.stdout if result.returncode == 0 else result.stderr
            lines.extend(["", "APT:", upgrades or "Paket güncellemesi bulunamadı."])
        except Exception as exc:
            lines.extend(["", f"APT kontrolü başarısız: {exc}"])

        self.after(0, lambda: (self.write("\n".join(lines)), self.set_busy(False), self.status.configure(text="Kontrol tamamlandı")))

    def install_release(self):
        if self.busy_state:
            return
        try:
            release = self.release or github_release()
            local = parse_version(local_version())
            latest_text = release.get("tag_name", "")
            latest = parse_version(latest_text)
            if latest <= local:
                messagebox.showinfo("CopperBars Update", "Yeni bir CopperBarsOS sürümü bulunamadı.", parent=self)
                return
            bundle = choose_asset(release, "-update.tar.gz")
            checksum = choose_asset(release, "-update.tar.gz.sha256")
            if not bundle or not checksum:
                raise RuntimeError("Release doğrulanabilir güncelleme paketi içermiyor.")
            if not messagebox.askyesno(
                "CopperBars Update",
                f"CopperBarsOS {latest_text} sürümü indirilsin ve kurulum için hazırlanıp yüklensin?\n\nKurulumdan önce otomatik yedek alınır.",
                parent=self,
            ):
                return
        except Exception as exc:
            messagebox.showerror("CopperBars Update", str(exc), parent=self)
            return

        self.set_busy(True)
        self.write(f"{bundle['name']} indiriliyor…\n")
        threading.Thread(target=self._download_and_install, args=(bundle, checksum, latest_text), daemon=True).start()

    def _download_and_install(self, bundle, checksum, version):
        try:
            with tempfile.TemporaryDirectory(prefix="copperbars-update-") as tmp:
                bundle_path = pathlib.Path(tmp) / bundle["name"]
                checksum_path = pathlib.Path(tmp) / checksum["name"]
                download(bundle["browser_download_url"], bundle_path)
                download(checksum["browser_download_url"], checksum_path)
                actual_sha = verify_sha256(bundle_path, checksum_path)
                self.after(0, lambda: self.write(
                    f"Checksum doğrulandı.\n\nRelease: {version}\nPaket: {bundle['name']}\nSHA-256: {actual_sha}\n\nKurulum için yönetici izni isteniyor…"
                ))
                result = subprocess.run(
                    ["pkexec", INSTALL_HELPER, str(bundle_path), version, actual_sha],
                    text=True, capture_output=True, timeout=1800,
                )
                if result.returncode != 0:
                    raise RuntimeError((result.stderr or result.stdout or "Güncelleme kurulumu başarısız.").strip())
            self.after(0, lambda: (self.write("Güncelleme tamamlandı. Yeniden başlatman önerilir."),
                                  self.set_busy(False),
                                  self.status.configure(text="CopperBarsOS güncellendi"),
                                  messagebox.showinfo("CopperBars Update", "CopperBarsOS güncellendi. Değişikliklerin tamamlanması için yeniden başlatma önerilir.", parent=self)))
        except Exception as exc:
            self.after(0, lambda: (self.write(f"Hata: {exc}"), self.set_busy(False), self.status.configure(text="Güncelleme başarısız"),
                                  messagebox.showerror("CopperBars Update", str(exc), parent=self)))

    def install_apt(self):
        if self.busy_state:
            return
        if not messagebox.askyesno("CopperBars Update", "Sistem paketleri güncellensin mi?", parent=self):
            return
        self.set_busy(True)
        self.write("APT güncellemeleri kuruluyor…\n")
        threading.Thread(target=self._install_apt, daemon=True).start()

    def _install_apt(self):
        try:
            result = subprocess.run(["pkexec", "apt-get", "-y", "upgrade"], text=True,
                                    capture_output=True, timeout=1800)
            if result.returncode != 0:
                raise RuntimeError((result.stderr or result.stdout or "APT kurulumu başarısız.").strip())
            self.after(0, lambda: (self.write(result.stdout or "APT güncellemeleri tamamlandı."), self.set_busy(False),
                                  self.status.configure(text="Paketler güncellendi"),
                                  messagebox.showinfo("CopperBars Update", "Paket güncellemeleri tamamlandı.", parent=self)))
        except Exception as exc:
            self.after(0, lambda: (self.write(f"Hata: {exc}"), self.set_busy(False), self.status.configure(text="APT başarısız"),
                                  messagebox.showerror("CopperBars Update", str(exc), parent=self)))


if __name__ == "__main__":
    CopperBarsUpdates().mainloop()
