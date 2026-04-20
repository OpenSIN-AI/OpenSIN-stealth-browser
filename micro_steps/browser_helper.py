"""
================================================================================
BROWSER HELPER - Dual-Browser Management für OpenSIN Stealth Browser v0.4.0
================================================================================

WICHTIG FÜR DEVELOPER:
----------------------
Diese Datei ist das HERZSTÜCK der Dual-Browser Architektur! 
Ohne diese Klasse funktionieren ALLE Micro-Steps NICHT richtig!

PROBLEM DAS WIR LÖSEN:
----------------------
1. Wir brauchen ZWEI getrennte Chrome-Instanzen:
   - Browser A (Port 9334): Temp-Mail.org im DEFAULT Profil (wegen Login-Persistenz)
   - Browser B (Port 9335): OpenAI.com im INKOGNITO Modus (frisch pro Run)

2. Warum nicht ein Browser?
   - Default-Profil kann nicht Incognito + Normal gleichzeitig
   - Temp-Mail Login MUSS im Default-Profil bleiben (Cookies!)
   - OpenAI muss frisch sein pro Run (Anti-Detection!)
   - Port-Kollisionen vermeiden (9334 vs 9335)

3. Was macht diese Klasse?
   - Sie entscheidet AUTOMATISCH welcher Browser für welchen Step benötigt wird
   - Sie verwaltet die CDP-Verbindungen zu beiden Browsern
   - Sie verhindert Race-Conditions durch Tab-Suche

VERWENDUNG IN MICRO-STEPS:
--------------------------
# IMMER SO MACHEN:
from browser_helper import BrowserHelper, BrowserType

async def execute(browser_helper: BrowserHelper):
    # Automatischer Browser-Select basierend auf Step-Name
    browser = browser_helper.get_browser_for_step("m05_goto_tempmail")
    
    # Jetzt mit dem richtigen Browser arbeiten
    page = await browser.get("https://temp-mail.org")

NIEMALS HARTE PORTS VERWENDEN!
FALSCH: browser = await uc.start(port=9334)  # ❌ BRICHT ALLES!
RICHTIG: browser = browser_helper.get_browser_for_step(step_name)  # ✅

AUTHOR: OpenSIN AI Team
VERSION: 0.4.0
LICENSE: MIT
================================================================================
"""

import asyncio
from enum import Enum
from typing import Optional, Dict
import nodriver as uc


class BrowserType(Enum):
    """
    Enum für Browser-Typen.
    
    TEMP_MAIL: Immer Port 9334, Default-Profil, mit Login-Persistenz
    OPENAI: Immer Port 9335, Incognito-Modus, frisch pro Run
    """
    TEMP_MAIL = "temp_mail"  # Temp-Mail.org mit Login
    OPENAI = "openai"        # OpenAI.com Incognito


class BrowserHelper:
    """
    ZENTRALES BROWSER-MANAGEMENT FÜR DUAL-BROWSER ARCHITEKTUR
    
    Diese Klasse verwaltet ZWEI parallele Chrome-Instanzen:
    1. Temp-Mail Browser (Port 9334, Default-Profil)
    2. OpenAI Browser (Port 9335, Incognito)
    
    WICHTIG: Diese Klasse ist ein Singleton pro Run!
    Nicht mehrfach instanziieren!
    
    ATTRIBUTES:
    -----------
    temp_mail_browser : uc.Browser
        Browser-Instanz für Temp-Mail (Port 9334)
    openai_browser : uc.Browser
        Browser-Instanz für OpenAI (Port 9335)
    step_to_browser : Dict[str, BrowserType]
        Mapping von Step-Namen zu Browser-Typen
        
    EXAMPLE:
    --------
    helper = BrowserHelper()
    await helper.start()
    
    # In Micro-Step:
    browser = helper.get_browser_for_step("m05_goto_tempmail")
    page = await browser.get("https://temp-mail.org")
    """
    
    def __init__(self):
        """
        Initialisiert den BrowserHelper.
        
        ACHTUNG: start() muss explizit aufgerufen werden!
        """
        self.temp_mail_browser: Optional[uc.Browser] = None
        self.openai_browser: Optional[uc.Browser] = None
        self._initialized = False
        
        # STEP-TO-BROWSER MAPPING
        # Jeder Step weiß welcher Browser benötigt wird
        # Bei neuen Steps HIER eintragen!
        self.step_to_browser: Dict[str, BrowserType] = {
            # Temp-Mail Steps (Brauchen Default-Profil wegen Login)
            "m05_goto_tempmail": BrowserType.TEMP_MAIL,
            "m06_check_tempmail": BrowserType.TEMP_MAIL,
            "m07_click_tempmail_delete": BrowserType.TEMP_MAIL,
            "m08_check_delete_confirm": BrowserType.TEMP_MAIL,
            "m09_click_delete_yes": BrowserType.TEMP_MAIL,
            "m10_click_generate_new": BrowserType.TEMP_MAIL,
            "m11_wait_and_get_email": BrowserType.TEMP_MAIL,
            "m18_switch_to_tempmail": BrowserType.TEMP_MAIL,
            "m19_wait_for_otp_email": BrowserType.TEMP_MAIL,
            "m20_extract_otp": BrowserType.TEMP_MAIL,
            "m30h_switch_tempmail_2nd": BrowserType.TEMP_MAIL,
            "m30i_wait_2nd_otp_email": BrowserType.TEMP_MAIL,
            
            # OpenAI Steps (Brauchen Incognito für frische Session)
            "m00_clear_openai_cookies": BrowserType.OPENAI,
            "m01_goto_openai_login": BrowserType.OPENAI,
            "m02_check_openai_login": BrowserType.OPENAI,
            "m03_click_register": BrowserType.OPENAI,
            "m04_check_register_page": BrowserType.OPENAI,
            "m12_switch_to_openai": BrowserType.OPENAI,
            "m13_type_email": BrowserType.OPENAI,
            "m14_click_continue": BrowserType.OPENAI,
            "m15_wait_for_password": BrowserType.OPENAI,
            "m16_type_password": BrowserType.OPENAI,
            "m17_click_continue": BrowserType.OPENAI,
            "m17b_wait_for_verification_page": BrowserType.OPENAI,
            "m21_switch_to_openai_again": BrowserType.OPENAI,
            "m22_type_otp": BrowserType.OPENAI,
            "m23_wait_for_about_you": BrowserType.OPENAI,
            "m24_type_name": BrowserType.OPENAI,
            "m25_click_bday_link": BrowserType.OPENAI,
            "m26_type_bday": BrowserType.OPENAI,
            "m28_submit_about_you": BrowserType.OPENAI,
            "m28a_handle_intermediate_login": BrowserType.OPENAI,
            "m28b_finish_onboarding": BrowserType.OPENAI,
            "m29_handle_consent": BrowserType.OPENAI,
            "m30a_open_oauth_url": BrowserType.OPENAI,
            "m30b_type_email_relogin": BrowserType.OPENAI,
            "m30c_click_continue_relogin": BrowserType.OPENAI,
            "m30d_wait_password_or_otp": BrowserType.OPENAI,
            "m30e_type_password_relogin": BrowserType.OPENAI,
            "m30f_click_continue_password": BrowserType.OPENAI,
            "m30g_check_otp_needed": BrowserType.OPENAI,
            "m30k_switch_to_openai_auth": BrowserType.OPENAI,
            "m30l_type_2nd_otp": BrowserType.OPENAI,
            "m30m_click_authorize": BrowserType.OPENAI,
            "m30n_wait_callback": BrowserType.OPENAI,
        }
    
    async def start(self):
        """
        Startet BEIDE Browser-Instanzen parallel.
        
        WICHTIG: Diese Methode MUSS vor allen Micro-Steps aufgerufen werden!
        Sie startet:
        1. Temp-Mail Browser auf Port 9334 (Default-Profil)
        2. OpenAI Browser auf Port 9335 (Incognito)
        
        RAISES:
        -------
        RuntimeError: Wenn Browser bereits gestartet wurden
        Exception: Wenn Chrome nicht gestartet werden kann
        
        RETURNS:
        --------
        self: Für Method-Chaining
        """
        if self._initialized:
            raise RuntimeError("BrowserHelper wurde bereits initialisiert!")
        
        print("\n🚀 STARTING DUAL-BROWSER ARCHITECTURE...")
        print("=" * 60)
        
        try:
            # ================================================================
            # BROWSER 1: TEMP-MAIL (Port 9334, Default-Profil)
            # ================================================================
            # WARUM Default-Profil? Weil wir dort eingeloggt sind bei temp-mail.org!
            # Cookies und Session MUSS persistent sein!
            print("📧 Starting Temp-Mail Browser (Port 9334, Default Profile)...")
            
            temp_args = [
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-blink-features=AutomationControlled',
                '--profile-directory=Default',  # WICHTIG: Default für Login-Persistenz!
                '--remote-debugging-port=9334',  # Fester Port für CDP
            ]
            
            self.temp_mail_browser = await uc.start(
                headless=False,
                browser_args=temp_args,
            )
            print("✅ Temp-Mail Browser ready!")
            
            # ================================================================
            # BROWSER 2: OPENAI (Port 9335, Incognito)
            # ================================================================
            # WARUM Incognito? Weil OpenAI jede Session trackt!
            # Fresh pro Run = Weniger Detection!
            print("🤖 Starting OpenAI Browser (Port 9335, Incognito)...")
            
            openai_args = [
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-blink-features=AutomationControlled',
                '--incognito',  # WICHTIG: Incognito für frische Session!
                '--remote-debugging-port=9335',  # Anderer Port!
            ]
            
            self.openai_browser = await uc.start(
                headless=False,
                browser_args=openai_args,
            )
            print("✅ OpenAI Browser ready!")
            
            self._initialized = True
            print("\n✅ DUAL-BROWSER ARCHITECTURE READY!")
            print("=" * 60)
            
            return self
            
        except Exception as e:
            print(f"\n❌ FEHLER BEIM BROWSER-START: {e}")
            print("HINWEIS: Vielleicht läuft schon Chrome auf Port 9334/9335?")
            print("LÖSUNG: 'pkill -9 chrome' ausführen und neu versuchen!")
            raise
    
    def get_browser_for_step(self, step_name: str) -> uc.Browser:
        """
        Gibt den RICHTIGEN Browser für einen gegebenen Step zurück.
        
        DAS IST DIE WICHTIGSTE METHODE!
        Jeder Micro-Step ruft diese Methode auf um den richtigen Browser zu bekommen.
        
        PARAMS:
        -------
        step_name : str
            Name des Micro-Steps (z.B. "m05_goto_tempmail")
            
        RETURNS:
        --------
        uc.Browser: Die richtige Browser-Instanz
        
        RAISES:
        -------
        ValueError: Wenn Step-Name unbekannt ist
        RuntimeError: Wenn BrowserHelper nicht initialisiert wurde
        
        EXAMPLE:
        --------
        >>> helper = BrowserHelper()
        >>> await helper.start()
        >>> browser = helper.get_browser_for_step("m05_goto_tempmail")
        >>> page = await browser.get("https://temp-mail.org")
        """
        if not self._initialized:
            raise RuntimeError("BrowserHelper.start() muss zuerst aufgerufen werden!")
        
        # Schritt-Name auflösen zu Browser-Typ
        if step_name not in self.step_to_browser:
            # FALLBACK: Bei unbekannten Steps OpenAI Browser verwenden
            # Das ist sicherer als Temp-Mail weil Incognito
            print(f"⚠️  WARNUNG: Unbekannter Step '{step_name}', verwende OpenAI Browser als Fallback")
            return self.openai_browser
        
        browser_type = self.step_to_browser[step_name]
        
        if browser_type == BrowserType.TEMP_MAIL:
            return self.temp_mail_browser
        else:
            return self.openai_browser
    
    async def get_page_for_step(self, step_name: str, url: Optional[str] = None) -> uc.Page:
        """
        Convenience-Methode: Gibt Page für Step zurück, öffnet URL falls angegeben.
        
        Spart Code in Micro-Steps!
        
        PARAMS:
        -------
        step_name : str
            Name des Micro-Steps
        url : Optional[str]
            URL die geöffnet werden soll (optional)
            
        RETURNS:
        --------
        uc.Page: Die Page-Instanz
        
        EXAMPLE:
        --------
        >>> page = await helper.get_page_for_step("m05_goto_tempmail", "https://temp-mail.org")
        """
        browser = self.get_browser_for_step(step_name)
        
        if url:
            page = await browser.get(url)
        else:
            # Aktuelle Page verwenden falls keine URL angegeben
            pages = await browser.pages
            if pages:
                page = pages[0]
            else:
                page = await browser.get('about:blank')
        
        return page
    
    async def find_tab_by_url(self, browser_type: BrowserType, url_pattern: str, timeout: int = 10) -> Optional[uc.Page]:
        """
        Sucht einen Tab mit bestimmter URL in einem Browser.
        
        NÜTZLICH FÜR:
        - OAuth-Flows wo sich Tabs öffnen
        - Redirects die neue Tabs erstellen
        - Multi-Tab Szenarien
        
        PARAMS:
        -------
        browser_type : BrowserType
            Welcher Browser durchsucht werden soll
        url_pattern : str
            URL-Pattern nach dem gesucht wird (substring match)
        timeout : int
            Timeout in Sekunden
            
        RETURNS:
        --------
        Optional[uc.Page]: Gefundene Page oder None
            
        EXAMPLE:
        --------
        >>> page = await helper.find_tab_by_url(BrowserType.OPENAI, "chat.openai.com")
        """
        browser = self.temp_mail_browser if browser_type == BrowserType.TEMP_MAIL else self.openai_browser
        
        for _ in range(timeout * 2):  # 2x pro Sekunde prüfen
            pages = await browser.pages
            for page in pages:
                try:
                    current_url = await page.evaluate('window.location.href')
                    if url_pattern in current_url:
                        return page
                except:
                    pass
            await asyncio.sleep(0.5)
        
        return None
    
    async def close_all(self):
        """
        Schließt BEIDE Browser sauber ab.
        
        WICHTIG: Diese Methode MUSS am Ende jedes Runs aufgerufen werden!
        Sonst bleiben Zombie-Prozesse zurück!
        
        EXAMPLE:
        --------
        >>> await helper.close_all()
        """
        print("\n🔒 Closing all browsers...")
        
        if self.temp_mail_browser:
            try:
                self.temp_mail_browser.stop()
                print("✅ Temp-Mail Browser closed")
            except:
                pass
        
        if self.openai_browser:
            try:
                self.openai_browser.stop()
                print("✅ OpenAI Browser closed")
            except:
                pass
        
        self._initialized = False
        print("✅ All browsers closed successfully!")
    
    def __del__(self):
        """
        Destructor: Stellt sicher dass Browser geschlossen werden.
        
        ABER: Verlasse dich NICHT darauf!
        Immer explizit close_all() aufrufen!
        """
        if self._initialized:
            print("⚠️  WARNUNG: BrowserHelper.__del__() wurde aufgerufen ohne close_all()!")
            print("⚠️  Das kann zu Zombie-Prozessen führen!")
