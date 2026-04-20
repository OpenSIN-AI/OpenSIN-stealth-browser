import asyncio, nodriver as uc, sys, random
import nodriver.cdp.input_ as input_cdp

async def _type(t, text):
    for char in text:
        await t.send(input_cdp.dispatch_key_event(type_="char", text=char))
        await asyncio.sleep(0.04)

async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    t = next((tab for tab in b.tabs if 'about-you' in getattr(tab, 'url', getattr(tab.target, 'url', ''))), None)
    if not t: return False
    
    # 1. Zuerst das Feld fuer Alter/Geburtstag fokussieren (das 2. sichtbare input)
    has_second_input = await t.evaluate("""
        (() => {
            const inputs = Array.from(document.querySelectorAll('input')).filter(i => i.type !== 'hidden');
            if (inputs.length >= 2) {
                inputs[1].focus();
                inputs[1].value = '';
                inputs[1].dispatchEvent(new Event('input', {bubbles: true}));
                return true;
            }
            return false;
        })()
    """)
    
    if not has_second_input:
        print("M26 WARN: 2. Input nicht gefunden!")
        # Fallback
        await t.evaluate("""
            const bday = document.querySelector('input[name="birthday"], input[name="age"]');
            if(bday) { bday.focus(); bday.value = ''; }
        """)

    await asyncio.sleep(0.5)
    
    # 2. Herauszufinden, ob das Feld 'Alter' oder 'Geburtsdatum' verlangt
    # Wir lesen den Text der umgebenden Labels
    page_text = await t.evaluate("document.body.innerText.toLowerCase()")
    if "alter" in page_text or "age" in page_text:
        # OpenAI fragt nach dem Alter (z.B. "Wie alt bist du?" / "Alter")
        age = str(random.randint(30, 45))
        await _type(t, age)
        print(f"M26 OK: Alter '{age}' getippt.")
    else:
        # OpenAI fragt nach dem Geburtsdatum (z.B. DD/MM/YYYY)
        # 8 Ziffern für die Aria-Maske
        bday = f"{random.randint(10, 28):02d}{random.randint(10, 12):02d}{random.randint(1980, 1995)}"
        await _type(t, bday)
        print(f"M26 OK: Geburtsdatum '{bday}' getippt.")

    return True

if __name__ == "__main__": 
    sys.exit(0 if asyncio.run(run()) else 1)
