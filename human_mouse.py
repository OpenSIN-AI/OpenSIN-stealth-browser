import asyncio, random, math; import numpy as np; from pynput.mouse import Button, Controller; from config import Config
mouse = Controller()
def bezier_curve(start, end, control_points, num_points=50):
    points = [start] + control_points + [end]; n = len(points) - 1; t_values = np.linspace(0, 1, num_points); curve = []
    for t in t_values:
        x = 0; y = 0
        for i, point in enumerate(points): coeff = math.comb(n, i) * (t ** i) * ((1 - t) ** (n - i)); x += coeff * point[0]; y += coeff * point[1]
        curve.append((int(x), int(y)))
    return curve
def generate_control_points(start, end, num_controls=2):
    controls = []; dx = end[0] - start[0]; dy = end[1] - start[1]; distance = math.sqrt(dx**2 + dy**2)
    for i in range(num_controls): t = (i + 1) / (num_controls + 1); mid_x = start[0] + dx * t; mid_y = start[1] + dy * t; offset = distance * random.uniform(0.1, 0.35); angle = random.uniform(-1, 1); controls.append((mid_x + offset * math.cos(angle), mid_y + offset * math.sin(angle)))
    return controls
async def move_mouse_human(target_x, target_y):
    current = mouse.position; start = (current[0], current[1]); end = (int(target_x), int(target_y)); distance = math.sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2)
    if distance < 5: return
    controls = generate_control_points(start, end, 2 if distance > 200 else 1); num_points = max(20, min(Config.MOUSE_CURVE_POINTS, int(distance / 5))); curve_points = bezier_curve(start, end, controls, num_points)
    for p in curve_points: mouse.position = p; await asyncio.sleep(random.uniform(0.005, 0.015))
async def human_click(x, y, double=False):
    await move_mouse_human(x, y); await asyncio.sleep(random.uniform(0.1, 0.2))
    if double: mouse.click(Button.left, 2)
    else: mouse.press(Button.left); await asyncio.sleep(random.uniform(0.05, 0.12)); mouse.release(Button.left)
