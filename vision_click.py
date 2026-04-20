import asyncio, random, time, numpy as np, cv2; from config import Config; from human_mouse import human_click
async def vision_find_and_click(page, text):
    path = Config.SCREENSHOT_DIR / f"screen_{int(time.time())}.png"; await page.save_screenshot(str(path))
    import easyocr; reader = easyocr.Reader([\'en\', \'de\'], gpu=False, verbose=False)
    results = reader.readtext(str(path))
    for (bbox, t, prob) in results:
        if text.lower() in t.lower() and prob > Config.OCR_CONFIDENCE:
            tl, br = bbox[0], bbox[2]; await human_click((tl[0]+br[0])/2, (tl[1]+br[1])/2 + 85); return True
    return False