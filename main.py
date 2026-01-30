import tkinter as tk
import numpy as np
from scipy.interpolate import make_interp_spline

WIDTH = 800
HEIGHT = 600
GRID_SPACING = 25
radius = 5

root = tk.Tk()
root.title("Interpolation")

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="white")
canvas.pack()

points = []  # List of (id, x_canvas, y_canvas)
selected_point = None
spline_id = None

# Konversi koordinat canvas <-> kartesius
def to_cartesian(x, y):
    return x - WIDTH // 2, HEIGHT // 2 - y

def to_canvas(x, y):
    return WIDTH // 2 + x, HEIGHT // 2 - y

# Cari titik yang diklik
def find_point(x, y):
    for point_id, px, py in points:
        if (x - px) ** 2 + (y - py) ** 2 <= radius ** 2:
            return point_id
    return None

# Gambar spline
#NANTI UBAH BUKAN DARI LIBRARY
def draw_spline():
    global spline_id
    if spline_id:
        canvas.delete(spline_id)
    if len(points) < 3:
        return

    # Ambil dan urutkan titik berdasarkan x kartesius
    sorted_pts = sorted(points, key=lambda p: p[1])
    xs, ys = [], []
    for _, x_canvas, y_canvas in sorted_pts:
        x_cart, y_cart = to_cartesian(x_canvas, y_canvas)
        xs.append(x_cart)
        ys.append(y_cart)

    xs = np.array(xs)
    ys = np.array(ys)

    if len(np.unique(xs)) < 3:
        return  # Agar spline tidak error jika ada x duplikat

    #DARI SINI BISA DIUBAH
    # Interpolasi spline
    spline = make_interp_spline(xs, ys, k=2)
    xs_smooth = np.linspace(xs.min(), xs.max(), 500)
    ys_smooth = spline(xs_smooth)

    coords = []
    for x, y in zip(xs_smooth, ys_smooth):
        cx, cy = to_canvas(x, y)
        coords.extend([cx, cy])

    spline_id = canvas.create_line(coords, fill="blue", width=2, smooth=True)

# Klik kiri: tambah atau pilih
def on_left_click(event):
    global selected_point
    clicked_id = find_point(event.x, event.y)
    if clicked_id:
        selected_point = clicked_id
    else:
        dot = canvas.create_oval(event.x - radius, event.y - radius,
                                 event.x + radius, event.y + radius,
                                 fill="red", outline="black")
        points.append((dot, event.x, event.y))
        draw_spline()

# Geser titik
def on_drag(event):
    global selected_point
    if selected_point:
        canvas.coords(selected_point,
                      event.x - radius, event.y - radius,
                      event.x + radius, event.y + radius)
        for i, (pid, _, _) in enumerate(points):
            if pid == selected_point:
                points[i] = (pid, event.x, event.y)
                break
        draw_spline()

# Lepas klik kiri
def on_release(event):
    global selected_point
    selected_point = None

# Klik kanan: hapus titik
def on_right_click(event):
    clicked_id = find_point(event.x, event.y)
    if clicked_id:
        canvas.delete(clicked_id)
        for i, (pid, _, _) in enumerate(points):
            if pid == clicked_id:
                del points[i]
                break
        draw_spline()

# Gambar grid
def draw_grid():
    for x in range(0, WIDTH, GRID_SPACING):
        canvas.create_line(x, 0, x, HEIGHT, fill="#ccc")
    for y in range(0, HEIGHT, GRID_SPACING):
        canvas.create_line(0, y, WIDTH, y, fill="#ccc")
    canvas.create_line(0, HEIGHT // 2, WIDTH, HEIGHT // 2, fill="black", width=2)
    canvas.create_line(WIDTH // 2, 0, WIDTH // 2, HEIGHT, fill="black", width=2)
    for i in range(-WIDTH // 2, WIDTH // 2, GRID_SPACING):
        x = WIDTH // 2 + i
        if 0 <= x <= WIDTH:
            canvas.create_text(x, HEIGHT // 2 + 10, text=str(i // GRID_SPACING), font=("Arial", 8), anchor="n")
    for i in range(-HEIGHT // 2, HEIGHT // 2, GRID_SPACING):
        y = HEIGHT // 2 - i
        if 0 <= y <= HEIGHT:
            canvas.create_text(WIDTH // 2 + 5, y, text=str(i // GRID_SPACING), font=("Arial", 8), anchor="w")

draw_grid()

# Event binding
canvas.bind("<Button-1>", on_left_click)
canvas.bind("<B1-Motion>", on_drag)
canvas.bind("<ButtonRelease-1>", on_release)
canvas.bind("<Button-3>", on_right_click)

root.mainloop()
