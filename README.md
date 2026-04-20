# 🕵️ Ultra Stealth Browser

Ein vollständiger, modularer Stealth-Browser-Wrapper basierend auf **nodriver** + echtem Chrome-Profil.

## Features

| Feature | Details |
|---|---|
| **TLS-Fingerprint** | Echtes Chrome BoringSSL (kein Fake nötig) |
| **Bezier-Mausbewegungen** | OS-Level, vollständig menschlich |
| **OCR Vision Click** | EasyOCR findet Buttons per Bilderkennung |
| **Fingerprint Consistency** | Gleicher GPU/Screen/Audio pro Profil |
| **Profil-Rotation** | Mehrere Chrome-Profile mit Cooldown |
| **Proxy-Rotation** | SOCKS5/HTTP mit automatischem Wechsel |
| **Session-Speicherung** | Verschlüsselte Cookie-Persistenz |
| **Tippfehler-Simulation** | 2% Chance auf Typo + Korrektur |
| **Stealth-JS** | Canvas, WebGL, Audio, Battery, Fonts |

---

## Installation

### 1. Voraussetzungen

- Python 3.11+
- Google Chrome installiert
- Tesseract OCR (für EasyOCR Backend)



### 2. Repository klonen



### 3. Abhängigkeiten installieren

Requirement already satisfied: nodriver>=0.38 in ./venv/lib/python3.14/site-packages (from -r requirements.txt (line 1)) (0.48.1)
Requirement already satisfied: Pillow>=10.0 in ./venv/lib/python3.14/site-packages (from -r requirements.txt (line 2)) (12.2.0)
Requirement already satisfied: opencv-python-headless>=4.8 in ./venv/lib/python3.14/site-packages (from -r requirements.txt (line 3)) (4.13.0.92)
Requirement already satisfied: numpy>=1.24 in ./venv/lib/python3.14/site-packages (from -r requirements.txt (line 4)) (2.4.4)
Requirement already satisfied: easyocr>=1.7 in ./venv/lib/python3.14/site-packages (from -r requirements.txt (line 5)) (1.7.2)
Requirement already satisfied: pynput>=1.7 in ./venv/lib/python3.14/site-packages (from -r requirements.txt (line 6)) (1.8.1)
Requirement already satisfied: python-dotenv>=1.0 in ./venv/lib/python3.14/site-packages (from -r requirements.txt (line 7)) (1.2.2)
Requirement already satisfied: cryptography>=41.0 in ./venv/lib/python3.14/site-packages (from -r requirements.txt (line 8)) (46.0.7)
Requirement already satisfied: aiofiles>=23.0 in ./venv/lib/python3.14/site-packages (from -r requirements.txt (line 9)) (25.1.0)
Requirement already satisfied: mss in ./venv/lib/python3.14/site-packages (from nodriver>=0.38->-r requirements.txt (line 1)) (10.1.0)
Requirement already satisfied: websockets>=14 in ./venv/lib/python3.14/site-packages (from nodriver>=0.38->-r requirements.txt (line 1)) (16.0)
Requirement already satisfied: deprecated in ./venv/lib/python3.14/site-packages (from nodriver>=0.38->-r requirements.txt (line 1)) (1.3.1)
Requirement already satisfied: torch in ./venv/lib/python3.14/site-packages (from easyocr>=1.7->-r requirements.txt (line 5)) (2.11.0)
Requirement already satisfied: torchvision>=0.5 in ./venv/lib/python3.14/site-packages (from easyocr>=1.7->-r requirements.txt (line 5)) (0.26.0)
Requirement already satisfied: scipy in ./venv/lib/python3.14/site-packages (from easyocr>=1.7->-r requirements.txt (line 5)) (1.17.1)
Requirement already satisfied: scikit-image in ./venv/lib/python3.14/site-packages (from easyocr>=1.7->-r requirements.txt (line 5)) (0.26.0)
Requirement already satisfied: python-bidi in ./venv/lib/python3.14/site-packages (from easyocr>=1.7->-r requirements.txt (line 5)) (0.6.7)
Requirement already satisfied: PyYAML in ./venv/lib/python3.14/site-packages (from easyocr>=1.7->-r requirements.txt (line 5)) (6.0.3)
Requirement already satisfied: Shapely in ./venv/lib/python3.14/site-packages (from easyocr>=1.7->-r requirements.txt (line 5)) (2.1.2)
Requirement already satisfied: pyclipper in ./venv/lib/python3.14/site-packages (from easyocr>=1.7->-r requirements.txt (line 5)) (1.4.0)
Requirement already satisfied: ninja in ./venv/lib/python3.14/site-packages (from easyocr>=1.7->-r requirements.txt (line 5)) (1.13.0)
Requirement already satisfied: six in ./venv/lib/python3.14/site-packages (from pynput>=1.7->-r requirements.txt (line 6)) (1.17.0)
Requirement already satisfied: pyobjc-framework-ApplicationServices>=8.0 in ./venv/lib/python3.14/site-packages (from pynput>=1.7->-r requirements.txt (line 6)) (12.1)
Requirement already satisfied: pyobjc-framework-Quartz>=8.0 in ./venv/lib/python3.14/site-packages (from pynput>=1.7->-r requirements.txt (line 6)) (12.1)
Requirement already satisfied: cffi>=2.0.0 in ./venv/lib/python3.14/site-packages (from cryptography>=41.0->-r requirements.txt (line 8)) (2.0.0)
Requirement already satisfied: pycparser in ./venv/lib/python3.14/site-packages (from cffi>=2.0.0->cryptography>=41.0->-r requirements.txt (line 8)) (3.0)
Requirement already satisfied: pyobjc-core>=12.1 in ./venv/lib/python3.14/site-packages (from pyobjc-framework-ApplicationServices>=8.0->pynput>=1.7->-r requirements.txt (line 6)) (12.1)
Requirement already satisfied: pyobjc-framework-Cocoa>=12.1 in ./venv/lib/python3.14/site-packages (from pyobjc-framework-ApplicationServices>=8.0->pynput>=1.7->-r requirements.txt (line 6)) (12.1)
Requirement already satisfied: pyobjc-framework-CoreText>=12.1 in ./venv/lib/python3.14/site-packages (from pyobjc-framework-ApplicationServices>=8.0->pynput>=1.7->-r requirements.txt (line 6)) (12.1)
Requirement already satisfied: filelock in ./venv/lib/python3.14/site-packages (from torch->easyocr>=1.7->-r requirements.txt (line 5)) (3.29.0)
Requirement already satisfied: typing-extensions>=4.10.0 in ./venv/lib/python3.14/site-packages (from torch->easyocr>=1.7->-r requirements.txt (line 5)) (4.15.0)
Requirement already satisfied: setuptools<82 in ./venv/lib/python3.14/site-packages (from torch->easyocr>=1.7->-r requirements.txt (line 5)) (81.0.0)
Requirement already satisfied: sympy>=1.13.3 in ./venv/lib/python3.14/site-packages (from torch->easyocr>=1.7->-r requirements.txt (line 5)) (1.14.0)
Requirement already satisfied: networkx>=2.5.1 in ./venv/lib/python3.14/site-packages (from torch->easyocr>=1.7->-r requirements.txt (line 5)) (3.6.1)
Requirement already satisfied: jinja2 in ./venv/lib/python3.14/site-packages (from torch->easyocr>=1.7->-r requirements.txt (line 5)) (3.1.6)
Requirement already satisfied: fsspec>=0.8.5 in ./venv/lib/python3.14/site-packages (from torch->easyocr>=1.7->-r requirements.txt (line 5)) (2026.3.0)
Requirement already satisfied: mpmath<1.4,>=1.1.0 in ./venv/lib/python3.14/site-packages (from sympy>=1.13.3->torch->easyocr>=1.7->-r requirements.txt (line 5)) (1.3.0)
Requirement already satisfied: wrapt<3,>=1.10 in ./venv/lib/python3.14/site-packages (from deprecated->nodriver>=0.38->-r requirements.txt (line 1)) (2.1.2)
Requirement already satisfied: MarkupSafe>=2.0 in ./venv/lib/python3.14/site-packages (from jinja2->torch->easyocr>=1.7->-r requirements.txt (line 5)) (3.0.3)
Requirement already satisfied: imageio!=2.35.0,>=2.33 in ./venv/lib/python3.14/site-packages (from scikit-image->easyocr>=1.7->-r requirements.txt (line 5)) (2.37.3)
Requirement already satisfied: tifffile>=2022.8.12 in ./venv/lib/python3.14/site-packages (from scikit-image->easyocr>=1.7->-r requirements.txt (line 5)) (2026.4.11)
Requirement already satisfied: packaging>=21 in ./venv/lib/python3.14/site-packages (from scikit-image->easyocr>=1.7->-r requirements.txt (line 5)) (26.1)
Requirement already satisfied: lazy-loader>=0.4 in ./venv/lib/python3.14/site-packages (from scikit-image->easyocr>=1.7->-r requirements.txt (line 5)) (0.5)

### 4. Konfiguration



### 5. Profile einrichten



---

## Benutzung



---

## Projektstruktur



---

## Chrome-Profil finden



---

## Stealth-Level



---

## Wichtige Hinweise

- Schließe Chrome **vollständig** bevor du den Bot startest
- Nutze echte Proxy-Anbieter (Residential > Datacenter)
- Setze einen zufälligen  in 
- Starte immer mit  um Stealth zu verifizieren

---

## Troubleshooting

| Problem | Lösung |
|---|---|
|  | Chrome komplett schließen, Activity Monitor prüfen |
|  |  in config.py, dann DOM-Klick |
|  |  in .env geändert? Sessions löschen:  |
|  | Proxy in  prüfen,  zum Testen |
|  | Chrome-Erweiterungen deaktivieren, anderen Profil-Ordner versuchen |
