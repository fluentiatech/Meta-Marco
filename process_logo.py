"""Recorta el logo, lo pasa a blanco sobre fondo transparente,
y genera dos versiones: marca (cuadrado con medalla) y completa (marca + texto)."""
from PIL import Image
import numpy as np

SRC = "logo.jpg"
OUT_MARK = "logo-mark-white.png"
OUT_FULL = "logo-white.png"

THRESHOLD = 110  # pixeles mas oscuros que esto se consideran tinta

img = Image.open(SRC).convert("L")
arr = np.array(img)
mask = (arr < THRESHOLD).astype(np.uint8) * 255  # 255 donde hay tinta

def crop_to_mask(mask_arr, padding=20):
    rows = np.any(mask_arr > 0, axis=1)
    cols = np.any(mask_arr > 0, axis=0)
    if not rows.any() or not cols.any():
        return None
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    rmin = max(0, rmin - padding)
    cmin = max(0, cmin - padding)
    rmax = min(mask_arr.shape[0] - 1, rmax + padding)
    cmax = min(mask_arr.shape[1] - 1, cmax + padding)
    return rmin, rmax, cmin, cmax

def build_white_rgba(mask_arr):
    h, w = mask_arr.shape
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[..., 0:3] = 255  # blanco
    rgba[..., 3] = mask_arr  # alfa = mascara de tinta
    return Image.fromarray(rgba, "RGBA")

# ----- LOGO COMPLETO (marca + texto) -----
box = crop_to_mask(mask, padding=24)
rmin, rmax, cmin, cmax = box
mask_full = mask[rmin:rmax+1, cmin:cmax+1]
white_full = build_white_rgba(mask_full)
white_full.save(OUT_FULL, optimize=True)
print(f"OK -> {OUT_FULL}  ({white_full.size[0]}x{white_full.size[1]})")

# ----- SOLO MARCA (cuadrado superior con medalla) -----
# Buscamos un gap horizontal de filas vacias entre marca y texto.
row_has_ink = np.any(mask > 0, axis=1)
ink_rows = np.where(row_has_ink)[0]
first_ink, last_ink = ink_rows[0], ink_rows[-1]
gap_start = None
gap_len = 0
best_gap = (0, 0)
# solo considerar gaps INTERIORES (rodeados de tinta por arriba y por abajo)
for r in range(first_ink, last_ink + 1):
    if not row_has_ink[r]:
        if gap_start is None:
            gap_start = r
        gap_len += 1
        if gap_len > best_gap[1]:
            best_gap = (gap_start, gap_len)
    else:
        gap_start = None
        gap_len = 0

gap_row, gap_size = best_gap
if gap_size < 20:
    print("WARN: no se encontro gap claro; uso solo bbox completo")
    mark_mask = mask_full
else:
    # recortar la marca: desde el inicio del bbox hasta el inicio del gap
    mark_rmin = rmin
    mark_rmax = gap_row - 1
    mark_mask = mask[mark_rmin:mark_rmax+1, cmin:cmax+1]
    # re-ajustar lateralmente sobre la marca
    sub_box = crop_to_mask(mark_mask, padding=18)
    if sub_box:
        srmin, srmax, scmin, scmax = sub_box
        mark_mask = mark_mask[srmin:srmax+1, scmin:scmax+1]

white_mark = build_white_rgba(mark_mask)
white_mark.save(OUT_MARK, optimize=True)
print(f"OK -> {OUT_MARK}  ({white_mark.size[0]}x{white_mark.size[1]})")
