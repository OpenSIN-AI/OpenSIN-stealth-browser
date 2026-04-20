"""
Menschliche Mausbewegung mit Bezier-Kurven
Simuliert echte Handbewegungen auf OS-Level
"""
import asyncio
import random
import math
import numpy as np
from pynput.mouse import Button, Controller
from config import Config

mouse = Controller()


def bezier_curve(start, end, control_points, num_points=50):
    """
    Generiert Punkte entlang einer Bezier-Kurve.
    Echte Mausbewegungen sind nie gerade Linien.
    """
    points = [start] + control_points + [end]
    n = len(points) - 1
    t_values = np.linspace(0, 1, num_points)
    
    curve = []
    for t in t_values:
        x = 0
        y = 0
        for i, point in enumerate(points):
            # Bernstein-Polynom
            coeff = math.comb(n, i) * (t ** i) * ((1 - t) ** (n - i))
            x += coeff * point[0]
            y += coeff * point[1]
        curve.append((int(x), int(y)))
    
    return curve


def generate_control_points(start, end, num_controls=2):
    """
    Generiert zufällige Kontrollpunkte für natürliche Kurven.
    Menschen bewegen die Maus nie in perfekten Linien.
    """
    controls = []
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = math.sqrt(dx**2 + dy**2)
    
    for i in range(num_controls):
        # Kontrollpunkt liegt seitlich versetzt zur direkten Linie
        t = (i + 1) / (num_controls + 1)
        mid_x = start[0] + dx * t
        mid_y = start[1] + dy * t
        
        # Seitliche Abweichung proportional zur Distanz
        offset = distance * random.uniform(0.1, 0.35)
        angle = random.uniform(-1, 1)
        
        ctrl_x = mid_x + offset * math.cos(angle)
        ctrl_y = mid_y + offset * math.sin(angle)
        
        controls.append((ctrl_x, ctrl_y))
    
    return controls


def apply_speed_profile(points):
    """
    Menschen bewegen die Maus:
    - Langsam am Anfang (Beschleunigung)
    - Schnell in der Mitte
    - Langsam am Ende (Abbremsen, Ziel anvisieren)
    """
    n = len(points)
    delays = []
    
    for i in range(n):
        t = i / max(n - 1, 1)
        # Sigmoid-ähnliche Geschwindigkeitskurve
        # Langsam -> Schnell -> Langsam
        speed = 1.0 - 0.7 * math.sin(math.pi * t)
        
        base_delay = random.uniform(Config.MOUSE_SPEED_MIN, Config.MOUSE_SPEED_MAX) / n
        delays.append(base_delay * speed)
    
    return delays


def apply_jitter(points, jitter_px=None):
    """
    Menschliche Hände zittern leicht.
    Fügt minimales Rauschen hinzu.
    """
    jitter = jitter_px or Config.MOUSE_JITTER_PX
    jittered = []
    
    for i, (x, y) in enumerate(points):
        if i == len(points) - 1:
            # Letzter Punkt: Kein Jitter (Zielgenauigkeit)
            jittered.append((x, y))
        else:
            jx = x + random.randint(-jitter, jitter)
            jy = y + random.randint(-jitter, jitter)
            jittered.append((jx, jy))
    
    return jittered


async def move_mouse_human(target_x, target_y):
    """
    Bewegt die Maus menschlich von aktueller Position zum Ziel.
    Nutzt Bezier-Kurven + Geschwindigkeitsprofil + Jitter.
    """
    current = mouse.position
    start = (current[0], current[1])
    end = (int(target_x), int(target_y))
    
    # Distanz berechnen
    distance = math.sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2)
    
    if distance < 5:
        # Schon am Ziel
        return
    
    # Anzahl Kontrollpunkte basierend auf Distanz
    num_controls = 2 if distance > 200 else 1
    
    # Bezier-Curve generieren
    controls = generate_control_points(start, end, num_controls)
    num_points = max(20, min(Config.MOUSE_CURVE_POINTS, int(distance / 5)))
    curve_points = bezier_curve(start, end, controls, num_points)
    
    # Jitter hinzufügen
    curve_points = apply_jitter(curve_points)
    
    # Geschwindigkeitsprofil
    delays = apply_speed_profile(curve_points)
    
    # Maus bewegen
    for point, delay in zip(curve_points, delays):
        mouse.position = point
        await asyncio.sleep(delay)
    
    # Overshoot-Simulation (15% Chance)
    if random.random() < Config.MOUSE_OVERSHOOT_CHANCE and distance > 100:
        # Leicht über Ziel hinausschießen
        overshoot_x = end[0] + random.randint(-15, 15)
        overshoot_y = end[1] + random.randint(-10, 10)
        mouse.position = (overshoot_x, overshoot_y)
        await asyncio.sleep(random.uniform(0.05, 0.15))
        
        # Zurück zum echten Ziel
        correction_points = bezier_curve(
            (overshoot_x, overshoot_y), end,
            [], num_points=8
        )
        for p in correction_points:
            mouse.position = p
            await asyncio.sleep(random.uniform(0.01, 0.03))
    
    # Finale Position sicherstellen
    mouse.position = end


async def human_click(target_x, target_y, double=False):
    """
    Bewegt Maus menschlich zum Ziel und klickt.
    """
    await move_mouse_human(target_x, target_y)
    
    # Kurze Pause vor Klick (Mensch "zielt")
    await asyncio.sleep(random.uniform(0.05, 0.2))
    
    if double:
        mouse.click(Button.left, 2)
    else:
        # Realistischer Klick: Press + kleine Pause + Release
        mouse.press(Button.left)
        await asyncio.sleep(random.uniform(0.04, 0.12))
        mouse.release(Button.left)
    
    # Kurze Pause nach Klick
    await asyncio.sleep(random.uniform(0.1, 0.3))


async def human_scroll(direction="down", amount=None):
    """Menschliches Scrollen"""
    scroll_amount = amount or random.randint(2, 6)
    
    if direction == "down":
        scroll_amount = -scroll_amount
    
    # Scrollen in kleinen Schritten
    for _ in range(abs(scroll_amount)):
        mouse.scroll(0, 1 if scroll_amount > 0 else -1)
        await asyncio.sleep(random.uniform(0.02, 0.08))
    
    await asyncio.sleep(random.uniform(0.3, 0.8))