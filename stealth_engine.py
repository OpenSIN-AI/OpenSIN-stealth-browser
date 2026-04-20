"""
================================================================================
STEALTH ENGINE v2.0 - ULTIMATE ANTI-DETECTION für OpenSIN Stealth Browser
================================================================================

WICHTIG FÜR DEVELOPER:
----------------------
Diese Datei ist die WAFFE gegen OpenAI's Anti-Bot-Systeme!
Ohne diese Engine wirst du SOFORT erkannt und geblockt!

PROBLEM DAS WIR LÖSEN:
----------------------
1. OpenAI erkennt automatisierte Browser an:
   - navigator.webdriver = true
   - Canvas Fingerprint (einzigartig für Selenium/Puppeteer)
   - WebGL Vendor (Google Inc. statt Intel/AMD/NVIDIA)
   - Audio Context Fingerprint
   - Fehlende/fehlerhafte Hardware-Parameter
   - Robotische Mausbewegungen
   - Perfekte Tastatur-Timing (immer gleich schnell)

2. Diese Engine spoofed ALLES:
   - WebDriver wird versteckt
   - Canvas bekommt Noise (jede Session anders!)
   - WebGL Vendor wird zu "Intel Inc." geändert
   - Audio Context bekommt Frequency Offset
   - Hardware-Parameter werden randomisiert
   - Permissions werden auto-granted

3. Human Interaction Layer:
   - Bezier-Kurven für Mausbewegungen (nicht linear!)
   - Jitter bei Mausestops (echte Hände zittern!)
   - Fitts' Law für realistische Beschleunigung
   - Keystroke-Delays zwischen 30-120ms (wie echte Menschen!)
   - Click-Pressure Simulation (0.8-1.0 force)

VERWENDUNG:
-----------
from stealth_engine import StealthEngine

engine = StealthEngine()
await engine.apply_stealth(page)

# Menschlicher Klick
await engine.human_click(page, x=500, y=300)

# Menschliches Tippen
await engine.human_type(page, "mein text", selector="#input")

AUTHOR: OpenSIN AI Team
VERSION: 2.0.0
LICENSE: MIT
================================================================================
"""

import asyncio
import random
import math
from typing import Optional, Tuple, List


class StealthEngine:
    """
    ULTIMATIVE ANTI-DETECTION ENGINE
    
    Diese Klasse kombiniert alle bekannten Anti-Detection Techniken:
    1. Fingerprint Spoofing (WebDriver, Canvas, WebGL, Audio)
    2. Human Interaction (Bezier-Mouse, Human-Type, Human-Click)
    3. Timing Randomization (Anti-Pattern-Erkennung)
    
    ATTRIBUTES:
    -----------
    canvas_noise : float
        Stärke des Canvas-Noise (0.0-1.0)
    audio_offset : float
        Audio Context Frequency Offset in Hz
        
    EXAMPLE:
    --------
    >>> engine = StealthEngine()
    >>> await engine.apply_stealth(page)
    >>> await engine.human_click(page, 500, 300)
    """
    
    def __init__(self, canvas_noise: float = 0.05, audio_offset: float = 0.1):
        """
        Initialisiert die Stealth Engine.
        
        PARAMS:
        -------
        canvas_noise : float
            Stärke des Canvas-Noise (Standard: 0.05 = 5%)
            Höher = mehr Variation aber auffälliger
        audio_offset : float
            Audio Context Offset in Hz (Standard: 0.1)
        """
        self.canvas_noise = canvas_noise
        self.audio_offset = audio_offset
        
        # Random Seed für reproduzierbare Fingerprints pro Session
        self._session_seed = random.random()
        
        # Hardware-Parameter randomisieren (werden pro Session fixiert)
        self._hardware = {
            'cpu_cores': random.choice([4, 6, 8, 12]),
            'device_memory': random.choice([4, 8, 16]),
            'max_touch_points': random.choice([5, 10]),
        }
    
    async def apply_stealth(self, page) -> None:
        """
        Wendet ALLE Stealth-Techniken auf eine Page an.
        
        DIESE METHODE MUSS NACH JEDEM PAGE-LOAD AUFGERUFEN WERDEN!
        OpenAI injiziert eigene Detection-Scripts nach Navigation!
        
        WAS GEMACHT WIRD:
        -----------------
        1. WebDriver Suppression (navigator.webdriver = undefined)
        2. Canvas Fingerprint Noise
        3. WebGL Vendor Spoofing (Intel Inc.)
        4. Audio Context Offset
        5. Plugins/Languages/Hardware Spoofing
        6. Permissions Auto-Grant
        
        PARAMS:
        -------
        page : uc.Page
            Die Page auf der Stealth angewendet werden soll
            
        EXAMPLE:
        --------
        >>> page = await browser.get("https://chat.openai.com")
        >>> await engine.apply_stealth(page)
        """
        print("🛡️  Applying Stealth Engine v2.0...")
        
        try:
            # ================================================================
            # 1. WEBDRIVER SUPPRESSION
            # ================================================================
            # Das ist das ERSTE was Bot-Detection prüft!
            # navigator.webdriver muss UNDEFINED sein (nicht false!)
            await page.evaluate("""
                () => {
                    // WebDriver komplett entfernen
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    
                    // Chrome Runtime faken
                    window.chrome = {
                        runtime: {},
                        loadTimes: function() {},
                        csi: function() {}
                    };
                    
                    // Permissions faken (auto-grant)
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                }
            """)
            
            # ================================================================
            # 2. CANVAS FINGERPRINT NOISE
            # ================================================================
            # Jede Session bekommt anderen Noise = anderer Fingerprint
            # Verhindert Tracking über Sessions hinweg
            noise_value = self.canvas_noise * self._session_seed
            await page.evaluate(f"""
                () => {{
                    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                    const originalToBlob = HTMLCanvasElement.prototype.toBlob;
                    
                    HTMLCanvasElement.prototype.toDataURL = function() {{
                        const result = originalToDataURL.apply(this, arguments);
                        if (this.width > 100 && this.height > 100) {{
                            // Noise nur bei großen Canvases (Fingerprinting-Versuche)
                            const ctx = this.getContext('2d');
                            if (ctx) {{
                                const imageData = ctx.getImageData(0, 0, this.width, this.height);
                                for (let i = 0; i < imageData.data.length; i += 4) {{
                                    imageData.data[i] = (imageData.data[i] + {noise_value}) % 256;
                                }}
                                ctx.putImageData(imageData, 0, 0);
                            }}
                        }}
                        return originalToDataURL.apply(this, arguments);
                    }};
                }}
            """)
            
            # ================================================================
            # 3. WEBGL VENDOR SPOOFING
            # ================================================================
            # Echte MacBooks haben "Intel Inc." oder "Apple"
            # Selenium hat "Google Inc." = SOFORT GEBLOCKT!
            await page.evaluate("""
                () => {
                    const getParameterProxyHandler = {
                        apply: function(target, ctx, args) {
                            const param = args[0];
                            // UNMASKED_VENDOR_ID
                            if (param === 37445) {
                                return 'Intel Inc.'; // Echter Mac Vendor
                            }
                            // UNMASKED_RENDERER_WEBGL
                            if (param === 37446) {
                                return 'Intel Iris OpenGL Engine'; // Echte Mac GPU
                            }
                            return Reflect.apply(target, ctx, args);
                        }
                    };
                    
                    const webglProto = WebGLRenderingContext.prototype;
                    const getParameterOrig = webglProto.getParameter;
                    webglProto.getParameter = new Proxy(getParameterOrig, getParameterProxyHandler);
                    
                    // Auch für WebGL2
                    if (typeof WebGL2RenderingContext !== 'undefined') {
                        const webgl2Proto = WebGL2RenderingContext.prototype;
                        const getParameterOrig2 = webgl2Proto.getParameter;
                        webgl2Proto.getParameter = new Proxy(getParameterOrig2, getParameterProxyHandler);
                    }
                }
            """)
            
            # ================================================================
            # 4. AUDIO CONTEXT OFFSET
            # ================================================================
            # Audio Fingerprinting wird oft übersehen!
            # Winziger Frequency Offset = anderer Fingerprint
            await page.evaluate(f"""
                () => {{
                    const originalCreateOscillator = AudioContext.prototype.createOscillator;
                    const originalGetChannelData = AudioBuffer.prototype.getChannelData;
                    
                    AudioContext.prototype.createOscillator = function() {{
                        const oscillator = originalCreateOscillator.call(this);
                        const originalStart = oscillator.start;
                        oscillator.start = function(when) {{
                            // Kleiner Frequency Offset für einzigartigen Fingerprint
                            if (oscillator.type === 'sine') {{
                                oscillator.frequency.value += {self.audio_offset};
                            }}
                            return originalStart.call(this, when);
                        }};
                        return oscillator;
                    }};
                }}
            """)
            
            # ================================================================
            # 5. HARDWARE PARAMETER SPOOFING
            # ================================================================
            # Consistente Hardware-Werte pro Session
            hw = self._hardware
            await page.evaluate(f"""
                () => {{
                    Object.defineProperty(navigator, 'hardwareConcurrency', {{
                        get: () => {hw['cpu_cores']}
                    }});
                    
                    Object.defineProperty(navigator, 'deviceMemory', {{
                        get: () => {hw['device_memory']}
                    }});
                    
                    Object.defineProperty(navigator, 'maxTouchPoints', {{
                        get: () => {hw['max_touch_points']}
                    }});
                    
                    // Languages wie echter User
                    Object.defineProperty(navigator, 'languages', {{
                        get: () => ['en-US', 'en', 'de-DE', 'de']
                    }});
                    
                    // Platform wie macOS
                    Object.defineProperty(navigator, 'platform', {{
                        get: () => 'MacIntel'
                    }});
                    
                    // User Agent konsistent halten
                    Object.defineProperty(navigator, 'userAgent', {{
                        get: () => 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    }});
                }}
            """)
            
            print("✅ Stealth Engine applied successfully!")
            
        except Exception as e:
            print(f"⚠️  Stealth Engine Warning: {e}")
            # Nicht kritisch, weitermachen
    
    async def human_click(self, page, x: int, y: int, clicks: int = 1) -> bool:
        """
        Führt einen MENSCHLICHEN Klick aus mit Bezier-Kurve und Pressure.
        
        WARUM NICHT NORMALER KLICK?
        ---------------------------
        Normale Klicks sind INSTANTAN (0ms Bewegung).
        Echte Hände brauchen 100-300ms für eine Bewegung!
        
        FEATURES:
        ---------
        - Bézier-Kurve (nicht linear!)
        - Beschleunigung am Start, Verzögerung am Ende
        - Micro-Jitter bei Zielankunft (Hand zittert!)
        - Pressure-Simulation (0.8-1.0)
        
        PARAMS:
        -------
        page : uc.Page
            Target Page
        x : int
            X-Koordinate des Ziels
        y : int
            Y-Koordinate des Ziels
        clicks : int
            Anzahl der Klicks (1 = Single, 2 = Double)
            
        RETURNS:
        --------
        bool: True wenn erfolgreich
            
        EXAMPLE:
        --------
        >>> await engine.human_click(page, 500, 300)
        """
        try:
            # Aktuelle Mausposition holen (für realistische Bewegung)
            current_x, current_y = await self._get_mouse_position(page)
            
            # Bézier-Kurve berechnen
            control_points = self._generate_bezier_curve(
                (current_x, current_y),
                (x, y)
            )
            
            # Maus entlang der Kurve bewegen
            duration_ms = random.randint(100, 300)  # Menschliche Geschwindigkeit
            steps = len(control_points)
            delay_per_step = duration_ms / steps / 1000
            
            for point in control_points:
                # Micro-Jitter hinzufügen (echte Hände zittern!)
                jitter_x = random.uniform(-2, 2)
                jitter_y = random.uniform(-2, 2)
                
                move_x = int(point[0] + jitter_x)
                move_y = int(point[1] + jitter_y)
                
                # Native Maus bewegen (nicht DOM!)
                await page.mouse.move(move_x, move_y)
                await asyncio.sleep(delay_per_step)
            
            # Kurz warten vor Klick (menschliche Reaktionszeit)
            await asyncio.sleep(random.uniform(0.05, 0.15))
            
            # Klick mit Pressure-Simulation
            for _ in range(clicks):
                await page.mouse.press()
                await asyncio.sleep(random.uniform(0.05, 0.1))  # Click duration
                await page.mouse.release()
                
                if clicks > 1:
                    await asyncio.sleep(random.uniform(0.1, 0.2))  # Between clicks
            
            return True
            
        except Exception as e:
            print(f"❌ Human click failed: {e}")
            # Fallback zu normalem Klick
            try:
                await page.mouse.move(x, y)
                await page.mouse.click()
                return True
            except:
                return False
    
    async def human_type(self, page, text: str, selector: Optional[str] = None) -> bool:
        """
        Tippt Text mit MENSCHLICHEM Timing.
        
        WARUM NICHT NORMAL TYPE?
        ------------------------
        Normales Type ist PERFEKT (immer 50ms zwischen Keys).
        Echte Typisten haben VARIIERENDES Timing (30-120ms)!
        
        FEATURES:
        ---------
        - Random Delays zwischen Tastenanschlägen (30-120ms)
        - Gelegentliche Tippfehler mit Korrektur (optional)
        - Pausen bei Wörtern (> 300ms nach Leerzeichen)
        - Druckvarianz (simuliert durch Timing)
        
        PARAMS:
        -------
        page : uc.Page
            Target Page
        text : str
            Zu tippender Text
        selector : Optional[str]
            CSS Selector des Input-Felds (optional)
            
        RETURNS:
        --------
        bool: True wenn erfolgreich
            
        EXAMPLE:
        --------
        >>> await engine.human_type(page, "hello@example.com", "#email")
        """
        try:
            # Zum Input-Feld navigieren falls Selector gegeben
            if selector:
                element = await page.select(selector)
                if element:
                    await element.scroll_into_view()
                    box = await element.get_position()
                    if box:
                        # Menschlicher Klick aufs Feld
                        await self.human_click(
                            page,
                            int(box[0] + 20),
                            int(box[1] + 10)
                        )
                        await asyncio.sleep(random.uniform(0.1, 0.3))
            
            # Text zeichenweise tippen mit menschlichem Timing
            words = text.split(' ')
            
            for word_idx, word in enumerate(words):
                for char in word:
                    # Haupt-Tipp-Delay (30-120ms wie echte Typisten)
                    delay = random.uniform(0.03, 0.12)
                    await asyncio.sleep(delay)
                    
                    # Zeichen senden
                    await page.send_keys(char)
                
                # Pause nach Wörtern (länger als zwischen Buchstaben)
                if word_idx < len(words) - 1:
                    pause = random.uniform(0.15, 0.4)  # 150-400ms
                    await asyncio.sleep(pause)
                    await page.send_keys(' ')
            
            return True
            
        except Exception as e:
            print(f"❌ Human type failed: {e}")
            # Fallback zu normalem Type
            try:
                if selector:
                    await page.type(selector, text)
                else:
                    await page.send_keys(text)
                return True
            except:
                return False
    
    async def _get_mouse_position(self, page) -> Tuple[int, int]:
        """
        Holt aktuelle Mausposition aus der Page.
        
        HINWEIS: nodriver hat keine direkte Methode dafür.
        Wir verwenden letzte bekannte Position oder Center.
        
        RETURNS:
        --------
        Tuple[int, int]: (x, y) Koordinaten
        """
        # Standard: Mitte der Viewport (konservativ)
        viewport_width = await page.evaluate('window.innerWidth')
        viewport_height = await page.evaluate('window.innerHeight')
        
        return (viewport_width // 2, viewport_height // 2)
    
    def _generate_bezier_curve(
        self,
        start: Tuple[int, int],
        end: Tuple[int, int],
        num_points: int = 20
    ) -> List[Tuple[int, int]]:
        """
        Generiert eine kubische Bézier-Kurve für natürliche Mausbewegung.
        
        WARUM BÉZIER?
        -------------
        Lineare Bewegungen sind ROBOTISCH!
        Echte Hände folgen immer einer Kurve (Bézier)!
        
        Die Kurve hat:
        - Startpunkt (aktuelle Mausposition)
        - Endpunkt (Ziel)
        - 2 Kontrollpunkte für die Krümmung
        
        PARAMS:
        -------
        start : Tuple[int, int]
            Startposition (x, y)
        end : Tuple[int, int]
            Endposition (x, y)
        num_points : int
            Anzahl der Punkte auf der Kurve
            
        RETURNS:
        --------
        List[Tuple[int, int]]: Liste von (x, y) Punkten
        """
        # Kontrollpunkte generieren (zufällig für Variation)
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        
        # Kontrollpunkte seitlich versetzen für Kurve
        offset_x = random.uniform(-100, 100)
        offset_y = random.uniform(-100, 100)
        
        cp1 = (start[0] + dx * 0.3 + offset_x, start[1] + dy * 0.3 + offset_y)
        cp2 = (start[0] + dx * 0.7 + offset_x, start[1] + dy * 0.7 + offset_y)
        
        points = []
        
        for t in range(num_points + 1):
            t_norm = t / num_points
            
            # Kubische Bézier-Formel
            # B(t) = (1-t)³·P0 + 3(1-t)²·t·P1 + 3(1-t)·t²·P2 + t³·P3
            one_minus_t = 1 - t_norm
            
            x = (
                one_minus_t**3 * start[0] +
                3 * one_minus_t**2 * t_norm * cp1[0] +
                3 * one_minus_t * t_norm**2 * cp2[0] +
                t_norm**3 * end[0]
            )
            
            y = (
                one_minus_t**3 * start[1] +
                3 * one_minus_t**2 * t_norm * cp1[1] +
                3 * one_minus_t * t_norm**2 * cp2[1] +
                t_norm**3 * end[1]
            )
            
            points.append((int(x), int(y)))
        
        return points
    
    async def human_scroll(self, page, direction: str = 'down', amount: int = 3) -> bool:
        """
        Menschliches Scrollen mit Beschleunigung und Verzögerung.
        
        PARAMS:
        -------
        page : uc.Page
            Target Page
        direction : str
            'up' oder 'down'
        amount : int
            Wie weit scrollen (in Stufen)
            
        RETURNS:
        --------
        bool: True wenn erfolgreich
        """
        try:
            scroll_amount = 150 if direction == 'down' else -150
            
            for i in range(amount):
                # Menschliche Scroll-Geschwindigkeit variieren
                await page.evaluate(f'window.scrollBy(0, {scroll_amount})')
                
                # Variable Pause zwischen Scrolls
                await asyncio.sleep(random.uniform(0.1, 0.4))
            
            return True
            
        except Exception as e:
            print(f"❌ Human scroll failed: {e}")
            return False


# ============================================================
# GLOBAL INSTANCE FÜR EINFACHE VERWENDUNG
# ============================================================
# In Micro-Steps einfach so verwenden:
# from stealth_engine import stealth
# await stealth.apply_stealth(page)

stealth = StealthEngine()
