import asyncio; from browser import StealthBrowser
async def main():
    bot = StealthBrowser(); await bot.start(); await bot.goto("https://bot.sannysoft.com"); print("✅ Browser Live"); await asyncio.sleep(10); await bot.close()
if __name__ == "__main__": asyncio.run(main())
