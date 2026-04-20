"""
JS-Injections für Stealth-Erweiterungen.
"""
async def inject_stealth(page):
    await page.evaluate("""
    Object.defineProperty(navigator, 'webdriver', {get: () => false});
    
    // Weitere Spoofs
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) return 'Intel Inc.';
        if (parameter === 37446) return 'Intel(R) UHD Graphics 630';
        return getParameter.apply(this, arguments);
    };

    // AudioContext Spoof
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (AudioContext) {
        Object.defineProperty(AudioContext.prototype, 'sampleRate', {get: () => 48000});
    }

    // Fonts
    Object.defineProperty(document, 'fonts', {
        get: () => ({ size: 42, check: () => true })
    });
    """)
    print("✅ Stealth JS injected")
