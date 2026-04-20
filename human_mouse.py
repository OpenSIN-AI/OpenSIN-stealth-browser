import asyncio, random, math, numpy as np; from pynput.mouse import Button, Controller; from config import Config
mouse = Controller()
def bezier_curve(start, end, controls, num_points=50):
    pts = [start] + controls + [end]; n = len(pts) - 1; t_vals = np.linspace(0, 1, num_points); curve = []
    for t in t_vals: curve.append(tuple(int(sum(math.comb(n, i) * (t**i) * ((1-t)**(n-i)) * p[j] for i, p in enumerate(pts))) for j in range(2)))
    return curve
async def move_mouse_human(tx, ty):
    start = mouse.position; end = (int(tx), int(ty)); dist = math.sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2)
    if dist < 5: return
    pts = bezier_curve(start, end, [(start[0]+random.randint(-50,50), start[1]+random.randint(-50,50))])
    for p in pts: mouse.position = p; await asyncio.sleep(random.uniform(0.005, 0.015))
async def human_click(x, y): await move_mouse_human(x, y); mouse.click(Button.left, 1); await asyncio.sleep(0.1)