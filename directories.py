#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║                StrikeX — DirScanX v2.0                       ║
║            Professional Directory Scanner                    ║
║                  Educational Use Only                        ║
╚══════════════════════════════════════════════════════════════╝

Features:
  - Multi-threaded directory scanning
  - HTTP/HTTPS support
  - Status code analysis with color coding
  - Random User-Agent rotation
  - Timeout & retry mechanism
  - Progress bar with live statistics
  - Result logging to file (JSON/TXT)
  - Rate limiting support
  - Colorful terminal UI

⚠️  DISCLAIMER: This tool is for educational & authorized testing only.
    Unauthorized access to systems is illegal. Use responsibly.
"""

import sys
import os
import time
import signal
import random
import json
import argparse
import threading
from datetime import datetime
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
    from colorama import init, Fore, Style
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
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0",
]


# ──────────────────────────────────────────────────────────────
# BANNER
# ──────────────────────────────────────────────────────────────
def print_banner():
    banner = f"""
{Colors.BRIGHT_CYAN}{Colors.BOLD}
    ██████╗ ██╗██████╗ ███████╗ ██████╗ █████╗ ███╗   ██╗██╗  ██╗
    ██╔══██╗██║██╔══██╗██╔════╝██╔════╝██╔══██╗████╗  ██║╚██╗██╔╝
    ██║  ██║██║██████╔╝███████╗██║     ███████║██╔██╗ ██║ ╚███╔╝
    ██║  ██║██║██╔══██╗╚════██║██║     ██╔══██║██║╚██╗██║ ██╔██╗
    ██████╔╝██║██║  ██║███████║╚██████╗██║  ██║██║ ╚████║██╔╝ ██╗
    ╚═════╝ ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝
{Colors.RESET}
    {Colors.BRIGHT_CYAN}╔══════════════════════════════════════════════════════════════════════════════╗
    ║  {Colors.BRIGHT_YELLOW}⚡ StrikeX — DirScanX v2.0 {Colors.BRIGHT_CYAN}│ {Colors.WHITE}Professional Directory Scanner{Colors.BRIGHT_CYAN}           ║
    ║  {Colors.BRIGHT_MAGENTA}👤 Author: c0d3s3cl4b {Colors.BRIGHT_CYAN}│ {Colors.WHITE}Educational & Authorized Testing Only{Colors.BRIGHT_CYAN}              ║
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
        "FOUND": Colors.BRIGHT_GREEN + Colors.BOLD,
        "FORBIDDEN": Colors.BRIGHT_YELLOW,
        "REDIRECT": Colors.BRIGHT_MAGENTA,
    }
    color = level_colors.get(level, Colors.WHITE)
    icons = {
        "INFO": "ℹ️ ",
        "SUCCESS": "✅",
        "WARNING": "⚠️ ",
        "ERROR": "❌",
        "FOUND": "🎯",
        "FORBIDDEN": "🔒",
        "REDIRECT": "↪️ ",
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


def get_status_color(status_code):
    """HTTP durum koduna göre renk döndürür."""
    if 200 <= status_code < 300:
        return Colors.BRIGHT_GREEN
    elif 300 <= status_code < 400:
        return Colors.BRIGHT_MAGENTA
    elif status_code == 403:
        return Colors.BRIGHT_YELLOW
    elif 400 <= status_code < 500:
        return Colors.BRIGHT_RED
    elif 500 <= status_code < 600:
        return Colors.RED
    return Colors.WHITE


def get_status_label(status_code):
    """HTTP durum koduna göre etiket döndürür."""
    labels = {
        200: "OK",
        201: "Created",
        301: "Moved Permanently",
        302: "Found (Redirect)",
        307: "Temporary Redirect",
        308: "Permanent Redirect",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        500: "Internal Server Error",
        502: "Bad Gateway",
        503: "Service Unavailable",
    }
    return labels.get(status_code, f"HTTP {status_code}")


# ──────────────────────────────────────────────────────────────
# ANA DİZİN TARAMA SINIFI
# ──────────────────────────────────────────────────────────────
class DirScanX:
    """Profesyonel dizin tarama aracı."""

    def __init__(self, config):
        self.url = config["url"].rstrip("/")
        self.wordlist = config["wordlist"]
        self.threads = config.get("threads", 20)
        self.timeout = config.get("timeout", 10)
        self.max_retries = config.get("retries", 2)
        self.delay = config.get("delay", 0)
        self.extensions = config.get("extensions", [])
        self.status_filter = config.get("status_filter", [200, 201, 301, 302, 307, 308, 401, 403])
        self.follow_redirects = config.get("follow_redirects", False)
        self.cookie_value = config.get("cookie", "")
        self.output_file = config.get("output", "")
        self.verbose = config.get("verbose", False)
        self.proxy_file = config.get("proxy_file", "")

        # İç state
        self.directories = []
        self.proxies = []
        self.found_paths = []
        self.lock = threading.Lock()
        self.total_scanned = 0
        self.total_dirs = 0
        self.error_count = 0
        self.start_time = None
        self.stop_flag = False

    # ─── YÜKLEME ──────────────────────────────────────────────

    def load_wordlist(self):
        """Dizin wordlist dosyasını yükler."""
        if not os.path.isfile(self.wordlist):
            log_message(f"Wordlist dosyası bulunamadı: {self.wordlist}", "ERROR")
            sys.exit(1)

        try:
            with open(self.wordlist, "r", encoding="utf-8", errors="ignore") as f:
                base_dirs = [line.strip() for line in f if line.strip() and not line.startswith("#")]

            # Eğer extension varsa, her dizin için extension'lı versiyonları da ekle
            self.directories = []
            for d in base_dirs:
                self.directories.append(d)
                for ext in self.extensions:
                    ext = ext.lstrip(".")
                    self.directories.append(f"{d}.{ext}")

            self.total_dirs = len(self.directories)
            log_message(f"{self.total_dirs:,} adet dizin/dosya yolu yüklendi", "INFO")
            if self.extensions:
                log_message(f"Uzantılar: {', '.join(self.extensions)}", "INFO")
        except Exception as e:
            log_message(f"Wordlist dosyası okunamadı: {e}", "ERROR")
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
                self.proxies = [line.strip() for line in f if line.strip()]
            log_message(f"{len(self.proxies)} adet proxy yüklendi", "INFO")
        except Exception as e:
            log_message(f"Proxy dosyası okunamadı: {e}", "WARNING")

    # ─── SESSION YÖNETİMİ ────────────────────────────────────

    def create_session(self):
        """Retry mekanizmalı bir requests session oluşturur."""
        session = requests.Session()

        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["HEAD", "GET"],
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=self.threads,
            pool_maxsize=self.threads,
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        session.headers.update({
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        })

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

    # ─── TARAMA LOJİĞİ ───────────────────────────────────────

    def scan_directory(self, directory, session):
        """Tek bir dizini tarar."""
        if self.stop_flag:
            return None

        session.headers["User-Agent"] = random.choice(USER_AGENTS)
        full_url = f"{self.url}/{directory}"
        proxies = self.get_random_proxy()

        try:
            response = session.get(
                full_url,
                timeout=self.timeout,
                proxies=proxies,
                allow_redirects=self.follow_redirects,
                verify=True,
            )

            status = response.status_code
            content_length = len(response.content)

            with self.lock:
                self.total_scanned += 1

            if status in self.status_filter:
                result = {
                    "url": full_url,
                    "status": status,
                    "size": content_length,
                    "directory": directory,
                }

                with self.lock:
                    self.found_paths.append(result)

                color = get_status_color(status)
                label = get_status_label(status)
                size_str = self._format_size(content_length)

                # İlerleme satırını temizle
                sys.stdout.write("\r" + " " * 120 + "\r")
                sys.stdout.flush()

                log_message(
                    f"[{Colors.BOLD}{color}{status}{Colors.RESET}] "
                    f"{Colors.WHITE}{full_url} "
                    f"{Colors.DIM}({label} | {size_str}){Colors.RESET}",
                    "FOUND" if status == 200 else ("FORBIDDEN" if status == 403 else "REDIRECT"),
                )

                return result
            else:
                with self.lock:
                    pass  # 404 veya filtrelenmemiş kodlar
                return None

        except requests.exceptions.Timeout:
            with self.lock:
                self.total_scanned += 1
                self.error_count += 1
            if self.verbose:
                log_message(f"Timeout: {full_url}", "WARNING")
            return None

        except requests.exceptions.ConnectionError:
            with self.lock:
                self.total_scanned += 1
                self.error_count += 1
            if self.verbose:
                log_message(f"Bağlantı hatası: {full_url}", "ERROR")
            return None

        except requests.exceptions.SSLError:
            with self.lock:
                self.total_scanned += 1
                self.error_count += 1
            if self.verbose:
                log_message(f"SSL hatası: {full_url}", "ERROR")
            return None

        except Exception as e:
            with self.lock:
                self.total_scanned += 1
                self.error_count += 1
            if self.verbose:
                log_message(f"Beklenmeyen hata ({full_url}): {e}", "ERROR")
            return None

    # ─── İLERLEME GÖSTERGESİ ──────────────────────────────────

    def progress_monitor(self):
        """Arka planda ilerleme bilgisi gösterir."""
        while not self.stop_flag and self.total_scanned < self.total_dirs:
            time.sleep(0.5)
            if self.stop_flag:
                break

            elapsed = time.time() - self.start_time
            speed = self.total_scanned / elapsed if elapsed > 0 else 0
            remaining = self.total_dirs - self.total_scanned
            eta = remaining / speed if speed > 0 else 0

            bar = create_progress_bar(self.total_scanned, self.total_dirs, 30)
            status = (
                f"\r  {bar} "
                f"{Colors.WHITE}{self.total_scanned:,}/{self.total_dirs:,} "
                f"{Colors.BRIGHT_CYAN}⚡ {speed:.0f}/sn "
                f"{Colors.BRIGHT_YELLOW}⏱️  ETA: {format_time(eta)} "
                f"{Colors.BRIGHT_GREEN}🎯 {len(self.found_paths)} bulundu "
                f"{Colors.BRIGHT_RED}❌ {self.error_count} hata"
                f"{Colors.RESET}    "
            )
            sys.stdout.write(status)
            sys.stdout.flush()

    # ─── ANA TARAMA ───────────────────────────────────────────

    def run(self):
        """Ana dizin taramasını başlatır."""
        self.load_wordlist()
        self.load_proxies()

        if not self.directories:
            log_message("Dizin listesi boş!", "ERROR")
            sys.exit(1)

        self._print_target_info()

        self.start_time = time.time()
        log_message("Tarama başlatılıyor...", "INFO")
        print()

        # İlerleme thread'i
        progress_thread = threading.Thread(target=self.progress_monitor, daemon=True)
        progress_thread.start()

        session = self.create_session()

        try:
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = {}
                for directory in self.directories:
                    if self.stop_flag:
                        break

                    if self.delay > 0:
                        time.sleep(self.delay)

                    future = executor.submit(self.scan_directory, directory, session)
                    futures[future] = directory

                for future in as_completed(futures):
                    if self.stop_flag:
                        for f in futures:
                            f.cancel()
                        break

        except KeyboardInterrupt:
            self.stop_flag = True
            print(f"\n\n  {Colors.BRIGHT_YELLOW}⚠️  Kullanıcı tarafından durduruldu!{Colors.RESET}")

        self.stop_flag = True

        # İlerleme satırını temizle
        sys.stdout.write("\r" + " " * 120 + "\r")
        sys.stdout.flush()

        elapsed = time.time() - self.start_time

        print()
        self._print_results(elapsed)

        if self.found_paths and self.output_file:
            self._save_results()

    # ─── YARDIMCI ─────────────────────────────────────────────

    @staticmethod
    def _format_size(size_bytes):
        """Boyutu okunabilir formata çevirir."""
        if size_bytes < 1024:
            return f"{size_bytes}B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f}KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f}MB"

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
            ("🔒 Protokol", parsed.scheme.upper()),
            ("📁 Wordlist", os.path.basename(self.wordlist)),
            ("🔢 Toplam Yol", f"{self.total_dirs:,}"),
            ("🧵 Thread Sayısı", str(self.threads)),
            ("⏱️  Timeout", f"{self.timeout}s"),
            ("🔄 Max Retry", str(self.max_retries)),
            ("📊 Filtre Kodları", ", ".join(map(str, self.status_filter))),
        ]

        if self.extensions:
            items.append(("📎 Uzantılar", ", ".join(self.extensions)))
        if self.delay > 0:
            items.append(("⏳ Gecikme", f"{self.delay}s"))
        if self.proxies:
            items.append(("🛡️  Proxy Sayısı", str(len(self.proxies))))

        for label, value in items:
            print(f"  {Colors.WHITE}  {label:<20}{Colors.RESET}: {Colors.BRIGHT_GREEN}{value}{Colors.RESET}")

        print(f"  {Colors.BRIGHT_CYAN}{'═' * 60}{Colors.RESET}\n")

    def _print_results(self, elapsed):
        """Sonuçları detaylı tablo halinde gösterir."""
        speed = self.total_scanned / elapsed if elapsed > 0 else 0

        print(f"  {Colors.BRIGHT_CYAN}{'═' * 60}{Colors.RESET}")
        print(f"  {Colors.BOLD}{Colors.BRIGHT_YELLOW}  📊 TARAMA RAPORU{Colors.RESET}")
        print(f"  {Colors.BRIGHT_CYAN}{'═' * 60}{Colors.RESET}")

        if self.found_paths:
            print(f"\n  {Colors.BRIGHT_GREEN}{Colors.BOLD}  🎯 Bulunan Dizin/Dosyalar ({len(self.found_paths)} adet):{Colors.RESET}\n")

            # Durum koduna göre grupla
            status_groups = {}
            for result in self.found_paths:
                status = result["status"]
                if status not in status_groups:
                    status_groups[status] = []
                status_groups[status].append(result)

            for status in sorted(status_groups.keys()):
                color = get_status_color(status)
                label = get_status_label(status)
                print(f"    {color}{Colors.BOLD}── [{status}] {label} ──{Colors.RESET}")
                for result in status_groups[status]:
                    size_str = self._format_size(result["size"])
                    print(f"    {color}  ➤ {result['url']} {Colors.DIM}({size_str}){Colors.RESET}")
                print()
        else:
            print(f"\n  {Colors.BRIGHT_RED}{Colors.BOLD}  ❌ Hiçbir dizin/dosya bulunamadı!{Colors.RESET}\n")

        # İstatistik tablosu
        stats_items = [
            ("⏱️  Toplam Süre", format_time(elapsed)),
            ("🔢 Taranan Yol", f"{self.total_scanned:,}"),
            ("🎯 Bulunan", str(len(self.found_paths))),
            ("⚡ Hız", f"{speed:.1f} istek/sn"),
            ("❌ Hata Sayısı", str(self.error_count)),
            ("🧵 Thread Sayısı", str(self.threads)),
        ]

        for label, value in stats_items:
            print(f"  {Colors.WHITE}  {label:<20}{Colors.RESET}: {Colors.BRIGHT_CYAN}{value}{Colors.RESET}")

        print(f"\n  {Colors.BRIGHT_CYAN}{'═' * 60}{Colors.RESET}\n")

    def _save_results(self):
        """Sonuçları dosyaya kaydeder."""
        try:
            if self.output_file.endswith(".json"):
                data = {
                    "timestamp": datetime.now().isoformat(),
                    "target_url": self.url,
                    "total_scanned": self.total_scanned,
                    "total_found": len(self.found_paths),
                    "errors": self.error_count,
                    "elapsed_time": format_time(time.time() - self.start_time),
                    "results": self.found_paths,
                }
                with open(self.output_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                with open(self.output_file, "w", encoding="utf-8") as f:
                    f.write(f"# DirScanX Sonuçları - {datetime.now().isoformat()}\n")
                    f.write(f"# Hedef: {self.url}\n")
                    f.write(f"# Bulunan: {len(self.found_paths)} adet\n\n")
                    for result in self.found_paths:
                        f.write(f"[{result['status']}] {result['url']} ({self._format_size(result['size'])})\n")

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
    config["url"] = ask("Hedef URL (http/https ile)")
    config["wordlist"] = ask("Wordlist Dosyası Yolu")

    # Opsiyonel ayarlar
    print(f"\n  {Colors.BRIGHT_YELLOW}── Opsiyonel Ayarlar (boş bırakabilirsiniz) ──{Colors.RESET}\n")

    config["threads"] = int(ask("Thread Sayısı", default="20", required=False) or 20)
    config["timeout"] = int(ask("Timeout (saniye)", default="10", required=False) or 10)
    config["retries"] = int(ask("Max Retry", default="2", required=False) or 2)
    config["delay"] = float(ask("İstekler Arası Gecikme (saniye)", default="0", required=False) or 0)
    config["cookie"] = ask("Cookie Değeri (key=value;key2=value2)", required=False)
    config["proxy_file"] = ask("Proxy Dosyası Yolu", required=False)
    config["output"] = ask("Sonuç Dosyası Yolu", default="dir_results.json", required=False) or "dir_results.json"
    config["verbose"] = ask("Detaylı Çıktı (e/h)", default="h", required=False).lower() in ("e", "evet", "y", "yes")

    ext = ask("Dosya Uzantıları (php,html,txt,bak)", required=False)
    if ext:
        config["extensions"] = [e.strip() for e in ext.split(",") if e.strip()]

    follow = ask("Yönlendirmeleri Takip Et (e/h)", default="h", required=False)
    config["follow_redirects"] = follow.lower() in ("e", "evet", "y", "yes")

    status = ask("Durum Kodu Filtresi (200,301,302,403)", default="200,201,301,302,307,308,401,403", required=False)
    if status:
        config["status_filter"] = [int(s.strip()) for s in status.split(",") if s.strip().isdigit()]

    return config


# ──────────────────────────────────────────────────────────────
# ARGPARSE YAPILANDIRMASI
# ──────────────────────────────────────────────────────────────
def parse_arguments():
    """Komut satırı argümanlarını parse eder."""
    parser = argparse.ArgumentParser(
        description="StrikeX — DirScanX v2.0 - Professional Directory Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  %(prog)s -u http://target.com -w wordlist.txt
  %(prog)s -u https://target.com -w wordlist.txt -t 30 -x php,html,txt
  %(prog)s -u http://target.com -w wordlist.txt --proxy proxies.txt -o results.json
  %(prog)s   (interaktif mod)
        """,
    )

    parser.add_argument("-u", "--url", help="Hedef URL (http/https)")
    parser.add_argument("-w", "--wordlist", help="Dizin wordlist dosyası yolu")
    parser.add_argument("-t", "--threads", help="Thread sayısı", type=int, default=20)
    parser.add_argument("--timeout", help="Timeout (saniye)", type=int, default=10)
    parser.add_argument("--retries", help="Max retry sayısı", type=int, default=2)
    parser.add_argument("--delay", help="İstekler arası gecikme (saniye)", type=float, default=0)
    parser.add_argument("-x", "--extensions", help="Dosya uzantıları (php,html,txt)", default="")
    parser.add_argument("-s", "--status-filter", help="Gösterilecek durum kodları (200,301,403)",
                        default="200,201,301,302,307,308,401,403")
    parser.add_argument("-c", "--cookie", help="Cookie değeri", default="")
    parser.add_argument("--proxy", help="Proxy dosyası yolu", default="")
    parser.add_argument("-f", "--follow-redirects", help="Yönlendirmeleri takip et", action="store_true")
    parser.add_argument("-o", "--output", help="Sonuç dosyası yolu", default="dir_results.json")
    parser.add_argument("-v", "--verbose", help="Detaylı çıktı", action="store_true")

    return parser.parse_args()


# ──────────────────────────────────────────────────────────────
# ANA GİRİŞ NOKTASI
# ──────────────────────────────────────────────────────────────
def main():
    """Ana giriş noktası."""
    signal.signal(signal.SIGINT, lambda s, f: (
        print(f"\n\n  {Colors.BRIGHT_YELLOW}⚠️  Program sonlandırılıyor...{Colors.RESET}\n"),
        sys.exit(0),
    ))

    print_banner()

    args = parse_arguments()

    if not all([args.url, args.wordlist]):
        config = interactive_mode()
    else:
        config = {
            "url": args.url,
            "wordlist": args.wordlist,
            "threads": args.threads,
            "timeout": args.timeout,
            "retries": args.retries,
            "delay": args.delay,
            "cookie": args.cookie,
            "proxy_file": args.proxy,
            "output": args.output,
            "verbose": args.verbose,
            "follow_redirects": args.follow_redirects,
        }

        if args.extensions:
            config["extensions"] = [e.strip() for e in args.extensions.split(",") if e.strip()]

        if args.status_filter:
            config["status_filter"] = [int(s.strip()) for s in args.status_filter.split(",") if s.strip().isdigit()]

    scanner = DirScanX(config)
    scanner.run()


if __name__ == "__main__":
    main()
