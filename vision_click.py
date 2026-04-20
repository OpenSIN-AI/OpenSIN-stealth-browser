"""
OCR-basiertes Vision Click System
Findet Buttons/Text per Bilderkennung und klickt auf OS-Level.
Der Browser weiß NICHT dass ein Script klickt.
"""
import asyncio
import random
import time
from pathlib import Path
from io import BytesIO

import numpy as np
import cv2
from PIL import Image

from config import Config
from human_mouse import human_click, move_mouse_human

# EasyOCR lazy-load (dauert beim ersten Mal)
_ocr_reader = None

def get_ocr():
    global _ocr_reader
    if _ocr_reader is None:
        import easyocr
        _ocr_reader = easyocr.Reader(
            Config.OCR_LANGUAGES,
            gpu=False,
            verbose=False
        )
        print("✅ OCR Engine geladen")
    return _ocr_reader


async def take_screenshot(page) -> np.ndarray:
    """Screenshot vom Browser machen und als OpenCV-Array zurückgeben"""
    timestamp = int(time.time())
    path = Config.SCREENSHOT_DIR / f"screen_{timestamp}.png"
    
    # nodriver screenshot
    await page.save_screenshot(str(path))
    
    img = cv2.imread(str(path))
    return img, path


def find_text_in_image(img: np.ndarray, target_text: str, confidence=None):
    """
    Findet Text im Bild per OCR.
    Gibt die Bounding-Box-Koordinaten zurück.
    """
    conf = confidence or Config.OCR_CONFIDENCE
    reader = get_ocr()
    
    results = reader.readtext(img)
    
    matches = []
    target_lower = target_text.lower().strip()
    
    for (bbox, text, prob) in results:
        text_lower = text.lower().strip()
        
        # Exakter Match oder enthält den Text
        if target_lower in text_lower or text_lower in target_lower:
            if prob >= conf:
                # Berechne Zentrum der Bounding Box
                top_left = bbox[0]
                bottom_right = bbox[2]
                center_x = (top_left[0] + bottom_right[0]) / 2
                center_y = (top_left[1] + bottom_right[1]) / 2
                
                matches.append({
                    "text": text,
                    "confidence": prob,
                    "center_x": center_x,
                    "center_y": center_y,
                    "bbox": bbox,
                    "width": bottom_right[0] - top_left[0],
                    "height": bottom_right[1] - top_left[1],
                })
    
    # Sortiere nach Confidence
    matches.sort(key=lambda m: m["confidence"], reverse=True)
    return matches


def find_button_by_color(img: np.ndarray, color_range=None):
    """
    Findet Buttons anhand ihrer Farbe (z.B. grüne/blaue Buttons).
    Backup-Methode wenn OCR versagt.
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Standard: Suche nach typischen Button-Farben
    color_ranges = [
        # Grün (OpenAI Continue Button)
        (np.array([35, 80, 80]), np.array([85, 255, 255])),
        # Blau (Standard Submit Buttons)
        (np.array([100, 80, 80]), np.array([130, 255, 255])),
        # Weiß/Hell (Light Mode Buttons)
        (np.array([0, 0, 200]), np.array([180, 30, 255])),
    ]
    
    buttons = []
    for lower, upper in color_ranges:
        mask = cv2.inRange(hsv, lower, upper)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 2000 < area < 50000:  # Typische Button-Größe
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                if 1.5 < aspect_ratio < 8:  # Buttons sind breiter als hoch
                    buttons.append({
                        "center_x": x + w / 2,
                        "center_y": y + h / 2,
                        "width": w,
                        "height": h,
                        "area": area,
                    })
    
    buttons.sort(key=lambda b: b["area"], reverse=True)
    return buttons


async def vision_find_and_click(page, text: str, browser_offset_y=85):
    """
    HAUPTFUNKTION: Findet Text per OCR und klickt mit OS-Level Maus.
    
    browser_offset_y: Pixel-Offset für Browser-Toolbar (Tab-Leiste etc.)
    """
    print(f"👁️  Vision-Suche nach: '{text}'")
    
    img, screenshot_path = await take_screenshot(page)
    
    if img is None:
        print("❌ Screenshot fehlgeschlagen")
        return False
    
    # 1. Versuche OCR
    matches = find_text_in_image(img, text)
    
    if matches:
        best = matches[0]
        t = best["text"]
        c = best["confidence"]
        print(f"✅ OCR gefunden: '{t}' (Confidence: {c:.2f})")
        
        # Koordinaten mit Browser-Offset
        click_x = best["center_x"]
        click_y = best["center_y"] + browser_offset_y
        
        # Leichte Randomisierung innerhalb des Button-Bereichs
        click_x += random.randint(-int(best["width"]*0.2), int(best["width"]*0.2))
        click_y += random.randint(-int(best["height"]*0.15), int(best["height"]*0.15))
        
        await human_click(click_x, click_y)
        print(f"🖱️  Geklickt auf ({click_x}, {click_y})")
        return True
    
    # 2. Fallback: Button-Farberkennung
    print(f"⚠️  OCR hat '{text}' nicht gefunden, versuche Farberkennung...")
    buttons = find_button_by_color(img)
    
    if buttons:
        # Nimm den größten Button
        btn = buttons[0]
        click_x = btn["center_x"]
        click_y = btn["center_y"] + browser_offset_y
        
        await human_click(click_x, click_y)
        print(f"🖱️  Farb-Klick auf ({click_x}, {click_y})")
        return True
    
    print(f"❌ '{text}' weder per OCR noch Farbe gefunden")
    return False


async def vision_find_and_click_with_retry(page, text: str, max_retries=3, wait_between=2):
    """Vision Click mit Retry-Logik"""
    for attempt in range(max_retries):
        if await vision_find_and_click(page, text):
            return True
        
        print(f"🔄 Retry {attempt + 1}/{max_retries}...")
        await asyncio.sleep(wait_between)
    
    return False


async def vision_type_in_field(page, field_label: str, text: str, browser_offset_y=85):
    """
    Findet ein Eingabefeld per OCR (anhand des Labels) und tippt Text ein.
    """
    img, _ = await take_screenshot(page)
    matches = find_text_in_image(img, field_label)
    
    if matches:
        best = matches[0]
        # Klicke leicht unterhalb/rechts des Labels (dort ist das Input-Feld)
        field_x = best["center_x"] + best["width"]
        field_y = best["center_y"] + best["height"] + 15 + browser_offset_y
        
        await human_click(field_x, field_y)
        await asyncio.sleep(0.3)
        
        # Tippe Text mit realistischem Timing
        from pynput.keyboard import Controller as KeyboardController
        keyboard = KeyboardController()
        
        for char in text:
            keyboard.type(char)
            await asyncio.sleep(random.uniform(
                Config.TYPE_SPEED_MIN, Config.TYPE_SPEED_MAX
            ))
            if random.random() < Config.TYPE_PAUSE_CHANCE:
                await asyncio.sleep(random.uniform(
                    Config.TYPE_PAUSE_MIN, Config.TYPE_PAUSE_MAX
                ))
        
        return True
    
    return False