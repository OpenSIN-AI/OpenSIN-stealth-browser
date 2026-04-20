import asyncio, random, time; from pathlib import Path; import numpy as np; import cv2; from config import Config
_ocr_reader = None
def get_ocr():
    global _ocr_reader
    if _ocr_reader is None: import easyocr; _ocr_reader = easyocr.Reader(Config.OCR_LANGUAGES, gpu=False, verbose=False)
    return _ocr_reader
async def take_screenshot(page):
    path = Config.SCREENSHOT_DIR / f"screen_{int(time.time())}.png"; await page.save_screenshot(str(path)); return cv2.imread(str(path)), path
async def vision_find_and_click(page, text, offset_y=85):
    img, _ = await take_screenshot(page); reader = get_ocr(); results = reader.readtext(img); target = text.lower().strip()
    for (bbox, t, prob) in results:
        if target in t.lower().strip() and prob >= Config.OCR_CONFIDENCE:
            tl, br = bbox[0], bbox[2]; cx = (tl[0] + br[0]) / 2; cy = (tl[1] + br[1]) / 2 + offset_y
            from human_mouse import human_click; await human_click(cx + random.randint(-5, 5), cy + random.randint(-5, 5)); return True
    return False
