"""
ULTRA STEALTH BROWSER - Main Entry Point

Usage:
    python main.py                    # Normaler Start
    python main.py --check           # Stealth-Check
    python main.py --profile NAME    # Bestimmtes Profil
    python main.py --setup           # Profile einrichten
"""
import asyncio
import sys
from browser import StealthBrowser
from profile_manager import ProfileManager
from config import Config


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
# DEMO: OpenAI Chat
# ============================================================

async def demo_openai(profile_name=None):
    """Demo: OpenAI Chat öffnen"""
    bot = StealthBrowser()
    await bot.start(profile_name)
    
    # Stealth Check
    await bot.check_stealth()
    
    # Zu OpenAI navigieren
    await bot.goto("https://chat.openai.com")
    await bot.think(3, 6)
    
    # Screenshot zum Debugging
    await bot.screenshot("openai_start")
    
    # Wenn Login nötig
    url = await bot.get_url()
    if "auth" in url or "login" in url:
        print("🔐 Login erforderlich...")
        
        # Email eingeben
        await bot.click("Log in")
        await bot.think(2, 4)
        
        email = input("Email eingeben: ").strip()
        await bot.type(email, "input[type='email']")
        await bot.think(0.5, 1.5)
        
        await bot.click("Continue")
        await bot.think(2, 4)
        
        password = input("Passwort eingeben: ").strip()
        await bot.type(password, "input[type='password']")
        await bot.think(0.5, 1.5)
        
        await bot.click("Continue")
        await bot.think(4, 7)
        
        await bot.screenshot("openai_after_login")
    
    print("\n✅ OpenAI Chat geladen!")
    print("Browser bleibt offen. Du kannst jetzt manuell weiterarbeiten.")
    
    # Session speichern
    await bot.save_session()
    
    input("\nEnter = Browser schließen...")
    await bot.close()


# ============================================================
# CUSTOM TASK
# ============================================================

async def custom_task(profile_name=None):
    """
    Hier kannst du deinen eigenen Task schreiben.
    Der Bot ist voll konfiguriert und ready.
    """
    bot = StealthBrowser()
    await bot.start(profile_name)
    
    # ====== DEIN CODE HIER ======
    
    await bot.goto("https://example.com")
    await bot.think(2, 4)
    
    # Vision-Click auf beliebigen Button
    await bot.click("Some Button Text")
    
    # Text eingeben
    await bot.type("Hello World", "input[name='search']")
    
    # Scrollen
    await bot.scroll_down(3)
    await bot.think(1, 2)
    
    # Screenshot
    await bot.screenshot("result")
    
    # ====== DEIN CODE ENDE ======
    
    input("\nEnter = Browser schließen...")
    await bot.close(save=True)


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
    
    # Standard: Custom Task
    await custom_task(profile)


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════╗
    ║     ULTRA STEALTH BROWSER v1.0           ║
    ║     nodriver + Vision + Bezier + OCR     ║
    ╚══════════════════════════════════════════╝
    """)
    
    asyncio.run(main())
