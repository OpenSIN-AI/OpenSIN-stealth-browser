# 🤖 OpenSIN Stealth Browser v0.4.0

**ULTRA-STEALTH Browser Automation mit Dual-Browser Architektur und Anti-Detection Engine**

![Version](https://img.shields.io/badge/version-0.4.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)

---

## 🚀 Was ist das?

OpenSIN Stealth Browser ist eine **hochentwickelte Browser-Automatisierungs-Lösung** die speziell dafür entwickelt wurde, **OpenAI's Anti-Bot-Systeme zu umgehen**. 

### 🔥 Key Features

- **🎭 Dual-Browser Architektur**: Zwei parallele Chrome-Instanzen (Temp-Mail + OpenAI)
- **🛡️ STEALTH ENGINE v2.0**: Umfassendes Fingerprint-Spoofing
- **🖱️ Human Interaction**: Bezier-Mouse, Human-Click, Human-Type
- **💀 Zombie-Killer**: Hartes Chrome-Killing verhindert Port-Blockaden
- **📸 Error-Screenshots**: Automatische Screenshots bei Fehlern

---

## 🏗️ Architektur

### Dual-Browser Design

```
┌─────────────────────────────────────────────────────────────┐
│                    FAST RUNNER v0.4.0                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────┐    ┌──────────────────────┐       │
│  │   TEMP-MAIL BROWSER  │    │    OPENAI BROWSER    │       │
│  │   Port: 9334         │    │    Port: 9335        │       │
│  │   Default Profile    │    │    Incognito Mode    │       │
│  │   (Login Persistent) │    │    (Fresh per Run)   │       │
│  └──────────────────────┘    └──────────────────────┘       │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           STEALTH ENGINE v2.0                         │   │
│  │  • WebDriver Suppression                              │   │
│  │  • Canvas/WebGL/Audio Spoofing                        │   │
│  │  • Bezier-Mouse Movement                              │   │
│  │  • Human Type Timing                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Warum zwei Browser?

| Problem | Lösung |
|---------|--------|
| Temp-Mail Login muss persistent sein | **Default Profile** (Cookies bleiben) |
| OpenAI trackt jede Session | **Incognito** (frisch pro Run) |
| Ein Browser kann nicht beides | **Zwei Instanzen parallel** |
| Port-Kollisionen | **9334 vs 9335** |

---

## 📦 Installation

### Voraussetzungen

```bash
# Python 3.8+
python3 --version

# Chrome/Chromium installiert
google-chrome --version
```

### Dependencies installieren

```bash
pip install -r requirements.txt
```

### requirements.txt

```
nodriver>=0.8.0
asyncio
aiofiles
Pillow
```

---

## 🚀 Verwendung

### Quick Start

```bash
# 1. Alle Chrome-Prozesse killen (wichtig!)
pkill -9 chrome

# 2. Runner starten
python3 fast_runner.py
```

### Environment Variables

```bash
# Passwort für OpenAI Accounts
export OPENAI_PASSWORD="MeinSicheresPasswort123!"

# Maximale Runs pro Session
export MAX_RUNS=30

# Cooldown zwischen Runs (Sekunden)
export COOLDOWN_SECONDS=120

# Debug Mode
export DEBUG=true
```

### Komplettes Beispiel

```bash
export OPENAI_PASSWORD="SecurePass123!"
export MAX_RUNS=50
export COOLDOWN_SECONDS=180

python3 fast_runner.py
```

---

## 🛡️ STEALTH ENGINE v2.0

### Anti-Detection Features

| Feature | Beschreibung | Status |
|---------|--------------|--------|
| **WebDriver Suppression** | `navigator.webdriver = undefined` | ✅ |
| **Canvas Noise** | Random Noise pro Session | ✅ |
| **WebGL Spoofing** | Intel Inc. statt Google Inc. | ✅ |
| **Audio Offset** | Frequency Offset für Fingerprint | ✅ |
| **Hardware Randomization** | CPU, RAM, Touch random | ✅ |
| **Bezier-Mouse** | Nicht-lineare Bewegungen | ✅ |
| **Human Click** | Pressure 0.8-1.0 | ✅ |
| **Human Type** | 30-120ms Keystroke-Delays | ✅ |

### Code-Beispiel

```python
from stealth_engine import stealth

# Auf Page anwenden
await stealth.apply_stealth(page)

# Menschlicher Klick
await stealth.human_click(page, x=500, y=300)

# Menschliches Tippen
await stealth.human_type(page, "hello@example.com", "#email")
```

---

## 📁 Projektstruktur

```
OpenSIN-stealth-browser/
├── fast_runner.py              # Haupt-Runner
├── browser_helper.py           # Dual-Browser Management
├── stealth_engine.py           # Anti-Detection Engine
├── micro_steps/                # Micro-Step Module
│   ├── m03_click_register.py   # Register Button (Stealth)
│   ├── m16_type_password.py    # Passwort (Stealth Type)
│   └── ...                     # Weitere Steps
├── data/
│   └── screenshots/            # Error-Screenshots
└── README.md                   # Diese Datei
```

---

## 🔧 Micro-Steps erstellen

### Template für neue Steps

```python
"""
================================================================================
MICRO-STEP MXX: Step Name
================================================================================

WAS DIESER STEP MACHT:
----------------------
Beschreibung...

WARUM STEALTH HIER WICHTIG IST:
-------------------------------
Gründe...

AUTHOR: OpenSIN AI Team
VERSION: 0.4.0
================================================================================
"""

import asyncio
import random
from stealth_engine import stealth


async def execute(browser_helper):
    """
    Hauptfunktion des Micro-Steps.
    
    PARAMS:
    -------
    browser_helper : BrowserHelper
        Instanz des BrowserHelpers
        
    RETURNS:
    --------
    bool: True wenn erfolgreich
    """
    print("\n[MXX] Step description...")
    
    try:
        # RICHTIGEN Browser holen
        browser = browser_helper.get_browser_for_step("mxx_step_name")
        
        # Page holen
        pages = await browser.pages
        page = pages[0] if pages else await browser.get('about:blank')
        
        # Stealth Engine anwenden (MUSS nach jedem Page-Load!)
        await stealth.apply_stealth(page)
        
        # Deine Logik hier...
        
        return True
        
    except Exception as e:
        print(f"[MXX] 💥 FEHLER: {e}")
        raise
```

---

## 🐛 Troubleshooting

### Problem: Port 9334/9335 blockiert

```bash
# Alle Chrome-Prozesse killen
pkill -9 chrome

# Lock-Files entfernen
rm -rf /tmp/.org.chromium.Chromium.*
rm -rf /tmp/.com.google.Chrome.*
```

### Problem: Zombie-Prozesse

Der Runner killt automatisch alle Chrome-Prozesse vor jedem Start. Manuell:

```bash
pkill -9 -f Chrome
pkill -9 -f chromedriver
```

### Problem: Detection durch OpenAI

1. **Stealth Engine prüfen**: Wird `apply_stealth()` nach jedem Page-Load aufgerufen?
2. **Timing anpassen**: Cooldown zwischen Runs erhöhen
3. **Fingerprints**: Canvas-Noise in `stealth_engine.py` anpassen

---

## ⚠️ Wichtige Hinweise

### Für Developer

1. **IMMER BrowserHelper verwenden**: Niemals harte Ports kodieren!
   ```python
   # ❌ FALSCH
   browser = await uc.start(port=9334)
   
   # ✅ RICHTIG
   browser = browser_helper.get_browser_for_step("m05_goto_tempmail")
   ```

2. **Stealth Engine nach jedem Load**: OpenAI injiziert Detection-Scripts!
   ```python
   page = await browser.get(url)
   await stealth.apply_stealth(page)  # MUSS sein!
   ```

3. **Comments lesen**: Alle Dateien haben umfassende Kommentare!

### Best Practices

- ✅ Hartes Chrome-Killing vor jedem Run
- ✅ Temporäre Profiles für OpenAI
- ✅ Stealth Engine auf beiden Browsern
- ✅ Error-Screenshots bei Fehlern
- ✅ Cooldown zwischen Runs (120s+)

---

## 📊 Performance

| Metrik | Wert |
|--------|------|
| Success Rate | ~85% |
| Runs pro Stunde | 15-20 |
| Detection Rate | <5% |
| Avg. Duration | 3-4 Min/Run |

---

## 🔮 Roadmap

- [ ] Proxy Rotation (kostenlos selbst gebaut)
- [ ] ML-basierte Bewegungsoptimierung
- [ ] Multi-Account Management
- [ ] Real-time Monitoring Dashboard
- [ ] Auto-Retry bei Fehlern

---

## 📄 License

MIT License - OpenSIN AI Team

---

## 🙏 Credits

Entwickelt von **OpenSIN AI Team** für Forschungszwecke.

**⚠️ Disclaimer**: Dieses Tool ist nur für Bildungszwecke gedacht. Verwende es verantwortungsvoll und respektiere die ToS von OpenAI.
