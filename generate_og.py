"""Genera og-image.jpg (1200x630) para Open Graph / Twitter Card."""
import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont
import numpy as np

OUT = "og-image.jpg"
W, H = 1200, 630

# Paleta de la web
BG       = (10, 10, 10)
INK      = (245, 241, 234)
INK_DIM  = (168, 163, 154)
GOLD     = (212, 161, 74)
GOLD_HI  = (232, 184, 106)
LINE_DARK = (40, 40, 40)

# ----- Fuentes: intenta EB Garamond / Inter Tight, fallback a Georgia / Arial -----
FONTS_DIR = "fonts"
os.makedirs(FONTS_DIR, exist_ok=True)

FONT_URLS = {
    "EBGaramond-Medium.ttf":       "https://github.com/googlefonts/EBGaramond/raw/main/fonts/ttf/EBGaramond-Medium.ttf",
    "EBGaramond-MediumItalic.ttf": "https://github.com/googlefonts/EBGaramond/raw/main/fonts/ttf/EBGaramond-MediumItalic.ttf",
    "EBGaramond-Regular.ttf":      "https://github.com/googlefonts/EBGaramond/raw/main/fonts/ttf/EBGaramond-Regular.ttf",
    "InterTight-SemiBold.ttf":     "https://github.com/rsms/inter/raw/master/docs/font-files/InterTight-SemiBold.ttf",
}

def ensure_font(name):
    path = os.path.join(FONTS_DIR, name)
    if os.path.exists(path):
        return path
    try:
        print(f"  descargando {name}...")
        urllib.request.urlretrieve(FONT_URLS[name], path)
        return path
    except Exception as e:
        print(f"  WARN: no se pudo descargar {name} ({e})")
        return None

def find_font(*candidates):
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None

eb_med  = ensure_font("EBGaramond-Medium.ttf")
eb_it   = ensure_font("EBGaramond-MediumItalic.ttf")
eb_reg  = ensure_font("EBGaramond-Regular.ttf")
inter_b = ensure_font("InterTight-SemiBold.ttf")

font_title       = find_font(eb_med, "C:/Windows/Fonts/georgia.ttf")
font_title_it    = find_font(eb_it,  "C:/Windows/Fonts/georgiai.ttf")
font_sub         = find_font(eb_reg, "C:/Windows/Fonts/georgia.ttf")
font_small_cap   = find_font(inter_b, "C:/Windows/Fonts/arialbd.ttf")

if not all([font_title, font_title_it, font_sub, font_small_cap]):
    raise SystemExit("ERROR: faltan fuentes y no se han podido descargar.")

# ----- Canvas con vignette radial sutil -----
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
cx, cy = W * 0.32, H * 0.40
maxd   = np.sqrt(cx**2 + cy**2)
dist   = np.sqrt((xx - cx)**2 + (yy - cy)**2) / maxd
# vignette: clara cerca del centro-izq, oscurece a las esquinas
vig = 1.0 - np.clip(dist, 0, 1) ** 1.6
arr = np.zeros((H, W, 3), dtype=np.float32)
arr[..., 0] = BG[0] + vig * 14
arr[..., 1] = BG[1] + vig * 14
arr[..., 2] = BG[2] + vig * 18
arr = np.clip(arr, 0, 255).astype(np.uint8)
img = Image.fromarray(arr, "RGB")
draw = ImageDraw.Draw(img)

# ----- Logo en arriba a la izquierda -----
logo = Image.open("logo-mark-white.png").convert("RGBA")
logo.thumbnail((100, 100), Image.LANCZOS)
img.paste(logo, (80, 70), logo)

# ----- Eyebrow dorado con guion -----
F_eb = ImageFont.truetype(font_small_cap, 16)
eb_text = "EDICIÓN ARTESANAL  ·  HECHO EN ESPAÑA"
draw.line([(80, 230), (130, 230)], fill=GOLD, width=2)
draw.text((148, 219), eb_text, fill=GOLD, font=F_eb)

# ----- Titular (dos líneas, segunda en cursiva dorada) -----
F_title    = ImageFont.truetype(font_title, 78)
F_title_it = ImageFont.truetype(font_title_it, 78)
draw.text((78, 280), "Tu meta no se olvida.", fill=INK, font=F_title)
draw.text((78, 360), "Se enmarca.",          fill=GOLD_HI, font=F_title_it)

# ----- Subtítulo -----
F_sub = ImageFont.truetype(font_sub, 28)
sub_l1 = "Marcos artesanales para tu dorsal, medalla y camiseta"
sub_l2 = "de carrera. Maratón, media, trail o popular."
draw.text((78, 482), sub_l1, fill=INK_DIM, font=F_sub)
draw.text((78, 518), sub_l2, fill=INK_DIM, font=F_sub)

# ----- Footer caption con linea dorada -----
F_cap = ImageFont.truetype(font_small_cap, 14)
draw.line([(78, 580), (110, 580)], fill=GOLD, width=2)
draw.text((124, 571), "DESDE 24,99 €  ·  MIMETAENMARCO.ES", fill=INK_DIM, font=F_cap)

# ----- Marco decorativo sutil a la derecha (silueta de marco) -----
# Rectángulo grande tipo marco
frame_x, frame_y = 870, 130
frame_w, frame_h = 250, 370
# Marco exterior dorado, fino
for thickness in range(2):
    draw.rectangle(
        [frame_x - thickness, frame_y - thickness,
         frame_x + frame_w + thickness, frame_y + frame_h + thickness],
        outline=GOLD if thickness == 0 else LINE_DARK,
        width=1
    )
# Interior con un círculo sutil simulando medalla
mx, my = frame_x + frame_w // 2, frame_y + 230
r = 45
draw.ellipse([mx - r, my - r, mx + r, my + r], outline=GOLD, width=2)
# Cinta de la medalla (dos líneas en V hacia arriba)
draw.line([(mx, my - r), (mx - 30, frame_y + 30)], fill=GOLD, width=2)
draw.line([(mx, my - r), (mx + 30, frame_y + 30)], fill=GOLD, width=2)
# Rectángulo dentro (simula dorsal arriba)
dorsal_w, dorsal_h = 130, 60
dx = frame_x + (frame_w - dorsal_w) // 2
dy = frame_y + 90
draw.rectangle([dx, dy, dx + dorsal_w, dy + dorsal_h], outline=GOLD, width=1)

# Label vertical bajo el marco
F_micro = ImageFont.truetype(font_small_cap, 12)
draw.text((frame_x, frame_y + frame_h + 20),
          "DORSAL  ·  MEDALLA  ·  CAMISETA",
          fill=INK_DIM, font=F_micro)

# ----- Guardar -----
img.save(OUT, "JPEG", quality=92, optimize=True, progressive=True)
print(f"\nOK -> {OUT}  ({W}x{H}, {os.path.getsize(OUT)/1024:.1f} KB)")
