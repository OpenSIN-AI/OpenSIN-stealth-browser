import asyncio, nodriver as uc, sys, os, json

async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = None
    b._process_pid = None
    
    print("M30n: Warte auf localhost:1455...")
    for i in range(120): # Erhöht auf 60 Sekunden
        # 1. Check tabs for the localhost URL
        for tab in b.tabs:
            curr = getattr(tab.target, "url", "") or ""
            if "localhost:1455" in curr or "127.0.0.1:1455" in curr:
                print(f"M30n OK: Callback erreicht nach {i*0.5}s!")
                await asyncio.sleep(5)
                return True
        
        # 2. Check if auth.json was actually updated even if we missed the tab redirect
        auth_path = os.path.expanduser("~/.local/share/opencode/auth.json")
        if not os.path.exists(auth_path):
            auth_path = os.path.expanduser("~/.config/opencode/auth.json")
            
        if os.path.exists(auth_path):
            try:
                mtime = os.path.getmtime(auth_path)
                if (time.time() - mtime) < 15: # Wurde in den letzten 15s aktualisiert
                    print("M30n OK: auth.json Update erkannt!")
                    return True
            except: pass
            
        await asyncio.sleep(0.5)
    print("M30n FAIL: Callback nicht erreicht.")
    return False

if __name__ == "__main__":
    import time
    sys.exit(0 if asyncio.run(run()) else 1)
