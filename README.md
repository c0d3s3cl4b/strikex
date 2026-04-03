# StrikeX ⚡

<p align="center">
  <img src="https://img.shields.io/badge/Version-2.0-red?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Platform-Windows%20|%20Linux%20|%20Mac-orange?style=for-the-badge" alt="Platform">
</p>

```
   ███████╗████████╗██████╗ ██╗██╗  ██╗███████╗██╗  ██╗
   ██╔════╝╚══██╔══╝██╔══██╗██║██║ ██╔╝██╔════╝╚██╗██╔╝
   ███████╗   ██║   ██████╔╝██║█████╔╝ █████╗   ╚███╔╝
   ╚════██║   ██║   ██╔══██╗██║██╔═██╗ ██╔══╝   ██╔██╗
   ███████║   ██║   ██║  ██║██║██║  ██╗███████╗██╔╝ ██╗
   ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
```

> **Profesyonel web güvenlik test araçları paketi.** Eğitim ve yetkili penetrasyon testi amaçlıdır.

---

## 🚀 Araçlar

### 🔑 BruteForceX — Web Login Brute Forcer

| Özellik            | Açıklama                              |
| ------------------ | ------------------------------------- |
| ⚡ Multi-Thread    | Paralel şifre denemesi ile yüksek hız |
| 🛡️ Proxy Desteği   | HTTP/SOCKS proxy rotasyonu            |
| 🎭 User-Agent      | Rastgele User-Agent rotasyonu         |
| 🔐 CSRF Token      | Otomatik CSRF token çekme ve gönderme |
| 🍪 Session/Cookie  | Oturum ve cookie yönetimi             |
| ⏱️ Timeout & Retry | Akıllı yeniden deneme mekanizması     |
| 📊 İlerleme Çubuğu | Canlı hız, ETA ve hata istatistikleri |
| 💾 Sonuç Kaydetme  | JSON formatında sonuç dosyası         |
| 🎨 Renkli Terminal | Profesyonel terminal arayüzü          |
| ⌨️ İnteraktif Mod  | CLI veya interaktif kullanım          |

### 📁 DirScanX — Directory Scanner

| Özellik               | Açıklama                                    |
| --------------------- | ------------------------------------------- |
| ⚡ Multi-Thread       | 20+ thread ile hızlı tarama                 |
| 🔒 HTTP/HTTPS         | Her iki protokolü destekler                 |
| 📊 Durum Kodu Analizi | 200, 301, 302, 403, 404 renkli ayrım        |
| 📎 Uzantı Desteği     | php, html, txt, bak gibi uzantılarla tarama |
| 🛡️ Proxy Desteği      | Proxy rotasyonu                             |
| 🎭 User-Agent         | Rastgele User-Agent rotasyonu               |
| 💾 Sonuç Kaydetme     | JSON/TXT formatında sonuç dosyası           |
| 📊 İlerleme Çubuğu    | Canlı hız, ETA ve bulunan sayısı            |

---

## 📦 Kurulum

```bash
# Repoyu klonla
git clone https://github.com/c0d3s3cl4b/strikex.git
cd strikex

# Bağımlılıkları yükle
pip install -r requirements.txt
```

---

## 🔧 Kullanım

### BruteForceX

#### CLI Modu

```bash
# Temel kullanım
python bruteforce.py -u http://target.com/login -n admin -w passwords.txt -f "Invalid"

# Gelişmiş kullanım
python bruteforce.py -u http://target.com/login -n admin -w passwords.txt -f "Invalid" \
  -t 20 --proxy proxies.txt --csrf csrf_token -v

# Başarılı giriş mesajı ile
python bruteforce.py -u http://target.com/login -n admin -w passwords.txt -s "Welcome"
```

#### İnteraktif Mod

```bash
python bruteforce.py
# Tüm ayarlar adım adım sorulur
```

#### Parametreler

| Parametre              | Açıklama               | Varsayılan   |
| ---------------------- | ---------------------- | ------------ |
| `-u, --url`            | Hedef login URL        | -            |
| `-n, --username`       | Kullanıcı adı          | -            |
| `-w, --wordlist`       | Şifre dosyası yolu     | -            |
| `-f, --fail-string`    | Başarısız giriş mesajı | -            |
| `-s, --success-string` | Başarılı giriş mesajı  | -            |
| `-c, --cookie`         | Cookie değeri          | -            |
| `-m, --method`         | HTTP metodu (GET/POST) | POST         |
| `-t, --threads`        | Thread sayısı          | 10           |
| `--timeout`            | Timeout (saniye)       | 10           |
| `--retries`            | Max retry              | 3            |
| `--delay`              | İstekler arası gecikme | 0            |
| `--proxy`              | Proxy dosyası          | -            |
| `--csrf`               | CSRF token alan adı    | -            |
| `-o, --output`         | Çıktı dosyası          | results.json |
| `-v, --verbose`        | Detaylı çıktı          | Kapalı       |

---

### DirScanX

#### CLI Modu

```bash
# Temel kullanım
python directories.py -u http://target.com -w wordlist.txt

# Uzantı ile tarama
python directories.py -u https://target.com -w wordlist.txt -x php,html,txt,bak

# Gelişmiş kullanım
python directories.py -u http://target.com -w wordlist.txt -t 30 --proxy proxies.txt -o results.json -v
```

#### İnteraktif Mod

```bash
python directories.py
# Tüm ayarlar adım adım sorulur
```

#### Parametreler

| Parametre                | Açıklama                 | Varsayılan       |
| ------------------------ | ------------------------ | ---------------- |
| `-u, --url`              | Hedef URL                | -                |
| `-w, --wordlist`         | Wordlist dosyası         | -                |
| `-t, --threads`          | Thread sayısı            | 20               |
| `--timeout`              | Timeout (saniye)         | 10               |
| `--retries`              | Max retry                | 2                |
| `--delay`                | İstekler arası gecikme   | 0                |
| `-x, --extensions`       | Dosya uzantıları         | -                |
| `-s, --status-filter`    | Durum kodu filtresi      | 200,301,302,403  |
| `-c, --cookie`           | Cookie değeri            | -                |
| `--proxy`                | Proxy dosyası            | -                |
| `-f, --follow-redirects` | Yönlendirmeleri takip et | Kapalı           |
| `-o, --output`           | Çıktı dosyası            | dir_results.json |
| `-v, --verbose`          | Detaylı çıktı            | Kapalı           |

---


---

## ⚠️ Yasal Uyarı

> **Bu araçlar yalnızca eğitim amaçlı ve yetkili güvenlik testleri için geliştirilmiştir.**

- 🚫 **İzinsiz** sistemlere erişim denemesi **yasadışıdır**
- ✅ Yalnızca **kendi** sistemlerinizde veya **yazılı izin aldığınız** sistemlerde kullanın
- 📜 Yerel yasalara ve düzenlemelere uygun hareket edin
- 🤝 Sorumlu güvenlik açıklama (Responsible Disclosure) politikalarına uyun

**Geliştiriciler, bu aracın kötüye kullanımından doğacak hiçbir sorumluluk kabul etmez.**

---

## 👤 Geliştirici

**c0d3s3cl4b** — Siber Güvenlik & Penetrasyon Testi

---

<p align="center">
  <sub>⚡ StrikeX v2.0 | Educational Use Only ⚡</sub>
</p>
