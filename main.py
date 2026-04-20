import asyncio, sys; from browser import StealthBrowser
async def main():
    bot = StealthBrowser(); await bot.start(); await bot.goto("https://chat.openai.com"); print("✅ Ultra Stealth Ready"); input("Enter to close..."); await bot.close()
if __name__ == "__main__": asyncio.run(main())