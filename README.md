<!-- 
  OpenSIN Stealth Browser - Visual README
  Designed for maximum impact, clarity, and developer experience.
  Aligns with Infra-SIN-OpenCode-Stack visual standards.
-->

# 🛡️ OpenSIN Stealth Browser

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-yellow.svg)
![Status](https://img.shields.io/badge/status-production%20ready-brightgreen.svg)
[![OpenSIN Ecosystem](https://img.shields.io/badge/OpenSIN-Ecosystem-purple.svg)](https://github.com/OpenSIN-AI)

**Die unaufhaltbare Maschine für Browser-Automatisierung.**
*Self-Healing • Anti-Bot Immunität • Menschliche Biometrie-Simulation*

[Installation](#-installation) • [Features](#-features) • [Dokumentation](#-dokumentation) • [Roadmap](#-roadmap)

</div>

---

## 🚀 Warum OpenSIN Stealth Browser?

Herkömmliche Automatisierungstools (Selenium, Playwright) werden von modernen Anti-Bot-Systemen (Cloudflare, PerimeterX, Akamai) sofort erkannt und blockiert. 

**OpenSIN Stealth Browser** ändert die Spielregeln:
- ✅ **Keine Erkennung:** Simuliert echte menschliche Verhaltensbiometrie (Maus-Tremor, Beschleunigungskurven).
- ✅ **Self-Healing:** Wenn ein Klick fehlschlägt, probiert der Agent automatisch 3 alternative Strategien.
- ✅ **IP-Intelligenz:** Erkennt automatisch, ob eine "Sticky IP" (für Umfragen) oder Rotation benötigt wird.
- ✅ **Zero-Config:** Funktioniert sofort ohne komplexe Proxy-Einrichtung (nutzt lokale IP sicher).

---

## 🏗 Architektur-Übersicht

So funktioniert das System unter der Haube. Eine modulare, selbstheilende Architektur.

```text
┌─────────────────────────────────────────────────────────────────┐
│                    OPENSIN STEALTH BROWSER                      │
├─────────────────────────────────────────────────────────────────┤
│  🧠 CORE BRAIN (Executor & Decision Logic)                      │
│     ├─ Self-Healing Loop (Retry/Fallback Strategies)            │
│     ├─ IP-Mode Detector (Sticky vs. Dynamic)                    │
│     └─ State Manager (Session Persistence)                      │
├─────────────────────────────────────────────────────────────────┤
│  🎭 ANTI-DETECTION LAYER                                        │
│     ├─ Human Mouse (Bezier + Physiologic Tremor)                │
│     ├─ Fingerprint Spoofing (WebGL, Canvas, Audio)              │
│     └─ Timing Randomization (Gaussian Delays)                   │
├─────────────────────────────────────────────────────────────────┤
│  👁️ PERCEPTION MODULE                                           │
│     ├─ DOM Parser (Deep Search)                                 │
│     ├─ Iframe & Shadow DOM Scanner                              │
│     └─ OCR / Vision Fallback (Tesseract/EasyOCR)                │
├─────────────────────────────────────────────────────────────────┤
│  🛡️ DEFENSE SYSTEMS                                             │
│     ├─ Turnstile Solver                                         │
│     ├─ hCaptcha Handler                                         │
│     └─ Cookie Banner Auto-Killer                                │
└─────────────────────────────────────────────────────────────────┘
           ⬇️ interacts with ⬇️
┌─────────────────────────────────────────────────────────────────┐
│                 TARGET PLATFORMS (OpenAI, Surveys, Shops)       │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✨ Key Features im Detail

| Feature | Beschreibung | Vorteil |
| :--- | :--- | :--- |
| **🖱️ Physiologische Maus** | Simuliert Mikro-Zittern (8-12Hz) und natürliche Beschleunigung. | Umgeht Behavioral Biometrics von Cloudflare. |
| **🔄 Self-Healing Clicks** | Versucht nacheinander: Vision → DOM → Iframe Scan → JS Force. | Der Bot bleibt nie stecken, auch bei UI-Änderungen. |
| **🍪 Cookie Killer** | Entfernt automatisch nervige Banner und Pop-ups. | Sauberer Screen für den Agenten, weniger Fehler. |
| **🔒 IP-Modus Switch** | Automatische Erkennung: Brauche ich Sticky IP (Umfragen)? | Verhindert Bans bei sensiblen Plattformen. |
| **🧩 Modular Design** | Einfach zu erweiternde Python-Klassen. | Perfekt für dumme Agenten und komplexe Enterprise-Flows. |

---

## 📦 Installation

Starte in weniger als 2 Minuten. Keine komplexen Abhängigkeiten.

### 1. Repository klonen
```bash
git clone https://github.com/OpenSIN-AI/OpenSIN-stealth-browser.git
cd OpenSIN-stealth-browser
```

### 2. Abhängigkeiten installieren
Wir nutzen `nodriver` (asynchrones Chrome) und `opencv` für Vision.
```bash
pip install -r requirements.txt
```

### 3. Ersten Test laufen lassen
```bash
python main.py
```

---

## 💻 Anwendungsbeispiele

### Beispiel A: Einfacher Login (Self-Healing)
Der Agent findet den Button selbstständig, egal wo er liegt.

```python
import asyncio
from core.browser import StealthBrowser
from core.executor import SafeExecutor

async def login_flow():
    bot = StealthBrowser()
    await bot.start(profile_name="user_01")
    
    await bot.goto("https://example.com/login")
    
    # Self-Healing: Sucht nach "Login", "Sign In" oder dem Icon
    if await SafeExecutor.click_anywhere(bot, "Login"):
        await bot.type("user@example.com", selector="#email")
        await bot.type("secure_password_123", selector="#password")
        await SafeExecutor.click_anywhere(bot, "Submit")
        
    await bot.close()

if __name__ == "__main__":
    asyncio.run(login_flow())
```

### Beispiel B: Umfrage mit Sticky-IP Modus
Wichtig für Plattformen, die IP-Wechsel bestrafen.

```python
# In config.yaml oder direkt im Code
CONFIG = {
    "ip_mode": "STICKY",  # Verhindert Rotation während der Session
    "human_delay": True   # Aktiviert Gaußsche Wartezeiten
}
```

---

## 📂 Projektstruktur

```text
OpenSIN-stealth-browser/
├── 📄 main.py                  # Entry Point & Demo Script
├── 📄 requirements.txt         # Dependencies
├── 📄 README.md                # Diese Datei
├── 📂 core/                    # Das Herzstück
│   ├── browser.py              # Chrome Wrapper & Stealth Config
│   ├── executor.py             # Self-Healing Logik (WICHTIG!)
│   └── anti_captcha.py         # Löser für Turnstile/Cookies
├── 📂 input/                   # Menschliche Simulation
│   └── human_mouse.py          # Bezier-Kurven & Tremor
├── 📂 config/                  # Einstellungen
│   └── settings.yaml           # IP-Modus & Timeouts
└── 📂 logs/                    # Automatische Logs & Screenshots
```

---

## 🗺️ Roadmap

Wir entwickeln uns ständig weiter, um einen Schritt vor den Anti-Bot-Systemen zu bleiben.

- [x] **v1.0**: Basis Stealth & Human Mouse
- [x] **v2.0**: Self-Healing Executor & Iframe Support
- [ ] **v2.1**: Integriertes Warm-Up Verhalten (30s Scrollen vor Aktion)
- [ ] **v3.0**: KI-gestützte CAPTCHA Lösung (ohne externe APIs)
- [ ] **v4.0**: Distributed Swarm Mode (Multi-Browser Orchestrierung)

---

## 🤝 Beitrag leisten (Contributing)

Wir begrüßen Beiträge! Bitte beachte unsere Richtlinien:
1.  **Kommentiere deinen Code:** Wir wollen, dass auch Anfänger verstehen, was deine Funktion tut.
2.  **Teste lokal:** Stelle sicher, dass dein Code mindestens 3 verschiedene Webseiten übersteht.
3.  **Pull Request:** Öffne einen PR gegen den `main` Branch.

Siehe [CONTRIBUTING.md](CONTRIBUTING.md) für Details.

---

## 📄 Lizenz

Dieses Projekt ist unter der **Apache 2.0 Lizenz** lizenziert. 
Kostenlos für Forschung, Entwicklung und kommerzielle Nutzung.

<div align="center">

**Gebaut mit ❤️ vom OpenSIN AI Team**  
[Overview](https://github.com/OpenSIN-AI/OpenSIN-overview) | [Bridge](https://github.com/OpenSIN-AI/OpenSIN-Bridge) | [Global Brain](https://github.com/OpenSIN-AI/Infra-SIN-Global-Brain)

</div>
