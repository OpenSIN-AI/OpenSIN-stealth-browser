"""
ULTRA STEALTH BROWSER - Main Entry Point (Final Version with Self-Healing)

Usage:
    python main.py                    # Normaler Start
    python main.py --check           # Stealth-Check
    python main.py --profile NAME    # Bestimmtes Profil
    python main.py --setup           # Profile einrichten
    python main.py --demo            # OpenAI Demo mit Self-Healing
"""
import asyncio
import sys
import logging
from browser import StealthBrowser
from profile_manager import ProfileManager
from config import Config
from core.executor import SafeExecutor
from core.anti_captcha import clean_path

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ============================================================
# SETUP: Profile einrichten
# ============================================================

def setup_profiles():
    """Interaktives Profil-Setup"""
    pm = ProfileManager()
    
    print("\n🔧 PROFIL-SETUP")
    print("=" * 50)
    pm.list_profiles()
    
    while True:
        print("\n[1] Neues Profil anlegen")
        print("[2] Profile anzeigen")
        print("[3] Fertig")
        
        choice = input("\nWahl: ").strip()
        
        if choice == "1":
            name = input("Profil-Name (z.B. 'work', 'private'): ").strip()
            chrome = input("Chrome Profile Directory (z.B. 'Default', 'Profile 1'): ").strip()
            cooldown = input("Cooldown in Stunden (Standard: 2): ").strip()
            cooldown = float(cooldown) if cooldown else 2.0
            
            pm.add_profile(name, chrome, cooldown)
            
        elif choice == "2":
            pm.list_profiles()
            
        elif choice == "3":
            break


# ============================================================
# STEALTH CHECK
# ============================================================

async def run_stealth_check(profile_name=None):
    """Führt einen Stealth-Check durch"""
    bot = StealthBrowser()
    await bot.start(profile_name)
    
    # Zu Bot-Detection-Test navigieren
    print("\n📡 Navigiere zu Stealth-Test-Seiten...\n")
    
    await bot.goto("https://bot.sannysoft.com")
    await bot.think(3, 5)
    await bot.screenshot("stealth_check_sannysoft")
    
    # Eigener Check
    await bot.check_stealth()
    
    await bot.goto("https://abrahamjuliot.github.io/creepjs/")
    await bot.think(5, 8)
    await bot.screenshot("stealth_check_creepjs")
    
    print("\n✅ Stealth-Check abgeschlossen!")
    print("📸 Screenshots in data/screenshots/")
    
    input("\nEnter = Browser schließen...")
    await bot.close()


# ============================================================
# DEMO: OpenAI Chat mit Self-Healing Executor
# ============================================================

async def demo_openai(profile_name=None):
    """Demo: OpenAI Chat mit robuster Self-Healing Logik"""
    bot = None
    try:
        bot = StealthBrowser()
        await bot.start(profile_name)
        
        # Stealth Check
        await bot.check_stealth()
        
        # Zu OpenAI navigieren
        logger.info("🌐 Navigiere zu https://chat.openai.com")
        await bot.goto("https://chat.openai.com")
        
        # Pfad säubern (Captchas, Cookie-Banner)
        await clean_path(bot)
        
        # Screenshot zum Debugging
        await bot.screenshot("openai_start")
        
        # Wenn Login nötig
        url = await bot.get_url()
        if "auth" in url or "login" in url:
            logger.info("🔐 Login erforderlich...")
            
            # Self-Healing Click für Login
            if await SafeExecutor.click_target(bot, "Log in"):
                await bot.think(2, 4)
                
                # Email eingeben
                email = input("Email eingeben: ").strip()
                await bot.type(email, "input[type='email']")
                await bot.think(0.5, 1.5)
                
                # Continue klicken mit Self-Healing
                await SafeExecutor.click_target(bot, "Continue")
                await bot.think(2, 4)
                
                # Passwort eingeben
                password = input("Passwort eingeben: ").strip()
                await bot.type(password, "input[type='password']")
                await bot.think(0.5, 1.5)
                
                # Continue klicken mit Self-Healing
                await SafeExecutor.click_target(bot, "Continue")
                await bot.think(4, 7)
                
                await bot.screenshot("openai_after_login")
                logger.info("✅ Login erfolgreich!")
            else:
                logger.error("❌ Konnte Login-Flow nicht starten.")
                await bot.screenshot("error_login_flow")
        else:
            logger.info("✅ Bereits eingeloggt!")
        
        # Session speichern
        await bot.save_session()
        logger.info("💾 Session gespeichert.")
        
        print("\n✅ OpenAI Chat geladen!")
        print("Browser bleibt offen. Du kannst jetzt manuell weiterarbeiten.")
        
        input("\nEnter = Browser schließen...")
        
    except Exception as e:
        logger.critical(f"💥 Kritischer Fehler: {e}", exc_info=True)
        if bot:
            await bot.screenshot("crash_state")
    finally:
        if bot:
            await bot.close()
            logger.info("🔒 Browser geschlossen.")


# ============================================================
# CUSTOM TASK mit Self-Healing
# ============================================================

async def custom_task(profile_name=None):
    """
    Hier kannst du deinen eigenen Task schreiben.
    Der Bot ist voll konfiguriert und ready mit Self-Healing.
    """
    bot = None
    try:
        bot = StealthBrowser()
        await bot.start(profile_name)
        
        # ====== DEIN CODE HIER ======
        
        # Beispiel: Robuste Navigation mit Self-Healing
        await bot.goto("https://example.com")
        await clean_path(bot)  # Captchas/Banner entfernen
        await bot.think(2, 4)
        
        # Vision-Click mit Self-Healing (versucht mehrere Strategien)
        await SafeExecutor.click_target(bot, "Some Button Text")
        
        # Text eingeben
        await bot.type("Hello World", "input[name='search']")
        
        # Scrollen
        await bot.scroll_down(3)
        await bot.think(1, 2)
        
        # Screenshot
        await bot.screenshot("result")
        
        # ====== DEIN CODE ENDE ======
        
        # Session speichern
        await bot.save_session()
        
        input("\nEnter = Browser schließen...")
        
    except Exception as e:
        logger.critical(f"💥 Kritischer Fehler: {e}", exc_info=True)
        if bot:
            await bot.screenshot("crash_state")
    finally:
        if bot:
            await bot.close(save=True)
            logger.info("🔒 Browser geschlossen.")


# ============================================================
# MAIN
# ============================================================

async def main():
    args = sys.argv[1:]
    
    profile = None
    for i, arg in enumerate(args):
        if arg == "--profile" and i + 1 < len(args):
            profile = args[i + 1]
    
    if "--setup" in args:
        setup_profiles()
        return
    
    if "--check" in args:
        await run_stealth_check(profile)
        return
    
    if "--demo" in args:
        await demo_openai(profile)
        return
    
    # Standard: Custom Task mit Self-Healing
    await custom_task(profile)


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════╗
    ║     ULTRA STEALTH BROWSER v2.0           ║
    ║     Self-Healing + Anti-Captcha          ║
    ║     Human Mouse + Iframe Support         ║
    ╚══════════════════════════════════════════╝
    """)
    
    asyncio.run(main())
