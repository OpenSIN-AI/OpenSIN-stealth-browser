# 🕵️ Ultra Stealth Browser - OpenSIN AI System

**Teil des OpenSIN AI Ökosystems** | [Overview](https://github.com/OpenSIN-AI/OpenSIN-overview) | [Bridge](https://github.com/OpenSIN-AI/OpenSIN-Bridge) | [Global Brain](https://github.com/OpenSIN-AI/Infra-SIN-Global-Brain)

Ein vollständiger, modularer Stealth-Browser-Wrapper basierend auf **nodriver** + echtem Chrome-Profil. 
Optimiert für maximale Erfolgsrate (90-95%) bei Browser-Automatisierung ohne erkannt zu werden.

> ⚠️ **Wichtig**: Es gibt keine 100%ige Sicherheit gegen moderne Anti-Bot-Systeme. Dieser Browser maximiert die Erfolgsrate durch menschliche Simulation, Self-Healing-Logik und konsistente Fingerprints.

## 🚀 Features

| Feature | Beschreibung | Warum wichtig? |
|---|---|---|
| **TLS-Fingerprint** | Echtes Chrome BoringSSL (kein Fake nötig) | Vermeidet TLS-Erkennung als Bot |
| **Bezier-Mausbewegungen** | OS-Level, vollständig menschlich mit physiologischem Tremor | Umgeht Maus-Analyse-Algorithmen |
| **OCR Vision Click** | EasyOCR findet Buttons per Bilderkennung | Funktioniert auch bei dynamischen Klassen |
| **Self-Healing Executor** | 4 Strategien pro Klick (Vision, DOM, Iframe, JS) | Gibt nie auf, probiert alternative Wege |
| **Fingerprint Consistency** | Gleicher GPU/Screen/Audio pro Profil | Vermeidet Inkonsistenzen im Fingerprint |
| **IP-Modus-Steuerung** | STICKY_IP für Umfragen oder normale Nutzung | Wichtig für Plattformen mit IP-Tracking |
| **Profil-Rotation** | Mehrere Chrome-Profile mit Cooldown | Ermöglicht parallele Sessions |
| **Session-Speicherung** | Verschlüsselte Cookie-Persistenz | Login-Daten bleiben erhalten |
| **Tippfehler-Simulation** | 2% Chance auf Typo + Korrektur | Menschliches Tippverhalten |
| **Anti-Captcha** | Turnstile, hCaptcha, Cookie-Banner Auto-Klick | Räumt Hindernisse automatisch weg |
| **Shadow DOM Support** | Durchsucht auch Shadow Roots und Iframes | Findet versteckte Elemente |

---

## 📦 Installation

### 1. Voraussetzungen

```bash
# Python 3.11+ muss installiert sein
python --version

# Google Chrome muss installiert sein
# Windows: https://www.google.com/chrome/
# Mac: brew install --cask google-chrome
# Linux: sudo apt install google-chrome-stable

# Tesseract OCR installieren (für EasyOCR)
# Windows: https://github.com/tesseract-ocr/tesseract/releases
# Mac: brew install tesseract
# Linux: sudo apt install tesseract-ocr
```

### 2. Repository klonen

```bash
git clone https://github.com/OpenSIN-AI/OpenSIN-stealth-browser.git
cd OpenSIN-stealth-browser
```

### 3. Abhängigkeiten installieren

```bash
# Virtuelle Umgebung erstellen (empfohlen)
python -m venv venv

# Unter Windows:
venv\Scripts\activate

# Unter Mac/Linux:
source venv/bin/activate

# Alle Pakete installieren
pip install -r requirements.txt
```

### 4. Konfiguration

Erstelle eine `.env` Datei im Hauptverzeichnis:

```bash
# .env Datei erstellen
cp .env.example .env

# .env bearbeiten und folgende Werte setzen:
STICKY_IP=false           # true für Umfragen/Logins, false für Rotation
USER_AGENT=random         # Oder spezifischen User-Agent setzen
TIMEZONE=Europe/Berlin    # Deine Zeitzone
LANGUAGE=de-DE,de;q=0.9   # Deine Sprache
```

### 5. Profile einrichten

```bash
# Interaktives Setup starten
python main.py --setup

# Folge den Anweisungen:
# [1] Neues Profil anlegen
# [2] Profile anzeigen
# [3] Fertig
```

---

## 💻 Benutzung

### Grundlegende Befehle

```bash
# Normaler Start (führt custom_task aus main.py aus)
python main.py

# Mit spezifischem Profil
python main.py --profile mein_profil

# Stealth-Check durchführen (empfohlen vor erst_use)
python main.py --check

# OpenAI Demo mit Self-Healing Login
python main.py --demo

# Profile verwalten
python main.py --setup
```

### Eigene Tasks schreiben

Bearbeite die Funktion `custom_task()` in `main.py`:

```python
async def custom_task(profile_name=None):
    bot = StealthBrowser()
    await bot.start(profile_name)
    
    # Beispiel: Robuste Navigation
    await bot.goto("https://example.com")
    await clean_path(bot)  # Captchas entfernen
    
    # Self-Healing Click (versucht mehrere Strategien)
    await SafeExecutor.click_target(bot, "Button Text")
    
    # Text eingeben
    await bot.type("Suchbegriff", "input[name='search']")
    
    # Screenshot speichern
    await bot.screenshot("ergebnis")
    
    await bot.close()
```

---

## 📁 Projektstruktur

```
OpenSIN-stealth-browser/
├── main.py                 # Haupt-Einstiegspunkt mit Beispielen
├── browser.py              # StealthBrowser Klasse (Hauptlogik)
├── config.py               # Zentrale Konfiguration
├── fingerprint.py          # Fingerprint-Management
├── human_mouse.py          # Menschliche Mausbewegungen
├── profile_manager.py      # Profil-Verwaltung
├── proxy_manager.py        # Proxy-Rotation
├── session_manager.py      # Session/Cookie Speicherung
├── requirements.txt        # Python-Abhängigkeiten
│
├── core/                   # Kern-Module (wichtig!)
│   ├── executor.py         # Self-Healing Executor (4 Strategien)
│   ├── anti_captcha.py     # Captcha & Banner Entfernung
│   └── browser.py          # Browser-Erweiterungen
│
├── input/                  # Eingabe-Module
│   └── human_mouse.py      # Physiologische Mausbewegungen
│
├── data/                   # Daten-Verzeichnis
│   ├── profiles/           # Gespeicherte Profile
│   ├── sessions/           # Verschlüsselte Sessions
│   └── screenshots/        # Debug-Screenshots
│
├── logs/                   # Log-Dateien
└── scripts/                # Hilfs-Skripte
```

---

## 🔍 Chrome-Profil finden

### Windows
```
C:\Users\DEIN_NAME\AppData\Local\Google\Chrome\User Data\
```
Gängige Profil-Namen: `Default`, `Profile 1`, `Profile 2`

### Mac
```
~/Library/Application Support/Google/Chrome/
```

### Linux
```
~/.config/google-chrome/
```

**Tipp**: Schließe Chrome vollständig bevor du den Bot startest!

---

## 🛡️ Stealth-Level

| Level | Beschreibung | Erfolgsrate |
|---|---|---|
| **Basis** | Nur nodriver ohne Optimierungen | ~60% |
| **Standard** | Mit Fingerprint-Konsistenz | ~75% |
| **Fortgeschritten** | + Human Mouse + OCR | ~85% |
| **Ultimate** | + Self-Healing + Iframe Scan | ~90-95% |

Dieses Projekt nutzt das **Ultimate** Level mit allen Optimierungen.

---

## ⚙️ IP-Modus Erklärung

### STICKY_IP = true (Für Umfragen/Login-Plattformen)
- Behält dieselbe IP für gesamte Session
- Wichtig für Plattformen wie SurveyJunkie, Prolific, etc.
- Vermeidet Erkennung durch IP-Wechsel

### STICKY_IP = false (Normale Nutzung)
- Ermöglicht vorsichtige Rotation zwischen Sessions
- Gut für allgemeines Scraping ohne Account-Bindung

**Konfiguration in `config.py`:**
```python
STICKY_IP = True  # Für Umfragen
# ODER
STICKY_IP = False  # Für normale Nutzung
```

---

## ⚠️ Wichtige Hinweise

1. **Chrome vollständig schließen** vor dem Start
   - Activity Monitor (Mac) oder Task Manager (Windows) prüfen
   - Alle Chrome-Prozesse beenden

2. **Residential Proxies empfohlen** für maximale Erfolgsrate
   - Anbieter: Bright Data, Smartproxy, IPRoyal
   - Datacenter-Proxies werden oft blockiert

3. **Immer mit `--check` starten** beim ersten Mal
   - Verifiziert Stealth-Konfiguration
   - Zeigt Screenshots von Test-Seiten

4. **Niemals headless=True** verwenden
   - OpenAI und Cloudflare prüfen GPU-Rendering
   - Headless = sofortige Erkennung

5. **Warm-Up Phase einbauen** bei neuen Sessions
   - 30-60 Sekunden warten vor ersten Aktionen
   - Zufällig scrollen und hoveren

---

## 🔧 Troubleshooting

| Problem | Lösung |
|---|---|
| Chrome startet nicht | Chrome komplett schließen, Activity Monitor prüfen |
| Vision-Click funktioniert nicht | `USE_OCR=false` in config.py, dann DOM-Klick |
| Session wird nicht gespeichert | `SESSION_DIR` in .env geändert? Sessions löschen: `rm -rf data/sessions/*` |
| Proxy verbindet nicht | Proxy in `proxy_manager.py` prüfen, `use_proxy=False` zum Testen |
| Fingerprint inkonsistent | Chrome-Erweiterungen deaktivieren, anderen Profil-Ordner versuchen |
| Turnstile nicht lösbar | Manuell lösen beim ersten Mal, Session wird gespeichert |
| Iframe-Element nicht gefunden | `executor.py` debuggen, ARIA-Labels prüfen |

---

## 🔄 Integration ins OpenSIN Ökosystem

Dieser Stealth Browser ist Teil des größeren OpenSIN AI Systems:

- **[OpenSIN Overview](https://github.com/OpenSIN-AI/OpenSIN-overview)**: Gesamtarchitektur und Dokumentation
- **[OpenSIN Bridge](https://github.com/OpenSIN-AI/OpenSIN-Bridge)**: Verbindung zwischen Agenten und Tools
- **[Infra-SIN Global Brain](https://github.com/OpenSIN-AI/Infra-SIN-Global-Brain)**: Zentrale KI-Steuerung

### Verwendung mit OpenSIN Bridge

```python
from bridge import OpenSINBridge

bridge = OpenSINBridge()
await bridge.connect()

# Stealth Browser als Tool registrieren
await bridge.register_tool("stealth_browser", StealthBrowser)

# Agent kann jetzt Browser-Befehle senden
await bridge.execute("stealth_browser", "goto", "https://example.com")
```

---

## 📄 Lizenz

Apache 2.0 - Siehe LICENSE Datei

## 🤝 Contributing

Siehe CONTRIBUTING.md für Richtlinien

## 📅 Changelog

Siehe CHANGELOG.md für Versionshistorie

---

**Made with ❤️ by the OpenSIN AI Team**
