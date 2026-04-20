import asyncio, nodriver as uc, sys

_CLICK = """(function(){
    var elements = Array.from(document.querySelectorAll('a, div, span'));
    var target = elements.find(el => {
        var t = (el.innerText || el.textContent || '');
        return t.includes('Dein Code') || t.includes('Code') || t.includes('ChatGPT');
    });
    // Wenn das Element gefunden wird, klicke es direkt, oder suche das umschliessende A-Tag
    if(target && target.offsetParent !== null) {
        var link = target.closest('a') || target;
        link.click();
        return true; 
    }
    return false;
})()"""

async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    t = next((tab for tab in b.tabs if 'temp-mail.org' in getattr(tab, 'url', getattr(tab.target, 'url', ''))), None)
    if not t: return False
    
    await t.bring_to_front()
    
    for i in range(80):
        if await t.evaluate(_CLICK):
            print(f"M19 OK: OTP Email nach {i * 0.5}s geklickt.")
            await asyncio.sleep(2)
            return True
        await asyncio.sleep(0.5)
        
    print("M19 FAIL: Timeout auf OTP.")
    return False

if __name__ == "__main__": sys.exit(0 if asyncio.run(run()) else 1)
