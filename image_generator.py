from PIL import Image, ImageDraw, ImageFont
import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HOLIDAY_TEXTS = {
    "qurbon":  ("Qurbon Hayiti", "muborak bo'lsin!"),
    "ramazon": ("Ramazon Hayiti", "muborak bo'lsin!"),
    "arafa":   ("Arafa kuni", "muborak bo'lsin!"),
}

# greet_y, name_y, hol_y, sub_y — 0.0 (yuqori) dan 1.0 (past) gacha
# color: (R, G, B)

BOTH_THEMES = [
    # both1 — qora fon, oy va chiroqlar yuqorida, pastki qism bo'sh
    {"file": "both1.png",
     "greet_x": 0.71, "greet_y": 0.24, "greet_color": (255, 215, 0),  "greet_size": 60,
     "name_x": 0.71, "name_y":  0.33, "name_color":  (255, 215, 0), "name_size":  70,
     "hol_y":   0.79, "hol_color":   (255, 215, 0),   "hol_size":   55,
     "sub_y":   0.88, "sub_color":   (255, 215, 0),   "sub_size":   45,
     "shadow": (20, 10, 0)},
 
    # both2 — ko'k romb, ichida bo'sh joy
    {"file": "both2.png",
     "greet_y": 0.38, "greet_color": (255, 255, 255), "greet_size": 60,
     "name_y":  0.48, "name_color":  (212, 175, 55),  "name_size":  78,
     "hol_y":   0.60, "hol_color":   (212, 175, 55),  "hol_size":   60,
     "sub_y":   0.69, "sub_color":   (200, 220, 255),  "sub_size":   45,
     "shadow": (5, 15, 40)},
 
    # both3 — oltin fon, qora ramka ichida bo'sh
    {"file": "both3.png",
     "greet_x": 0.52, "greet_y": 0.30, "greet_color": (212, 175, 55),  "greet_size": 55,
     "name_x":  0.52, "name_y":  0.40, "name_color":  (212, 175, 55),  "name_size":  68,
     "hol_x":   0.52, "hol_y":   0.52, "hol_color":   (212, 175, 55),   "hol_size":   50,
     "sub_x":   0.52, "sub_y":   0.62, "sub_color":   (212, 175, 55),   "sub_size":   42,
     "shadow": (10, 5, 0)},
 
    # both4 — ko'k gumbaz ichida bo'sh joy
    {"file": "both4.png",
     "greet_y": 0.42, "greet_color": (255, 255, 255), "greet_size": 60,
     "name_y":  0.52, "name_color":  (212, 175, 55),  "name_size":  78,
     "hol_y":   0.64, "hol_color":   (212, 175, 55),  "hol_size":   55,
     "sub_y":   0.73, "sub_color":   (200, 220, 255),  "sub_size":   45,
     "shadow": (5, 15, 40)},
 
    # both5 — qora romb, chiroqlar atrofida
    {"file": "both5.png",
     "greet_y": 0.40, "greet_color": (212, 175, 55),  "greet_size": 47,
     "name_y":  0.50, "name_color":  (255, 215, 0),   "name_size":  55,
     "hol_y":   0.60, "hol_color":   (212, 175, 55),  "hol_size":   45,
     "sub_y":   0.67, "sub_color":   (212, 175, 55),  "sub_size":   38,
     "shadow": (10, 5, 0)},
 
    # both6 — oq gumbaz, katta bo'sh joy
    {"file": "both6.png",
     "greet_y": 0.35, "greet_color": (150, 100, 20),  "greet_size": 55,
     "name_y":  0.45, "name_color":  (100, 60, 10),   "name_size":  75,
     "hol_y":   0.57, "hol_color":   (150, 100, 20),  "hol_size":   50,
     "sub_y":   0.67, "sub_color":   (150, 100, 20),  "sub_size":   40,
     "shadow": (200, 180, 150)},
 
    # both7 — yashil gumbaz, katta bo'sh joy
    {"file": "both7.png",
     "greet_y": 0.35, "greet_color": (212, 175, 55),  "greet_size": 60,
     "name_y":  0.45, "name_color":  (212, 175, 55),  "name_size":  80,
     "hol_y":   0.55, "hol_color":   (212, 175, 55),  "hol_size":   55,
     "sub_y":   0.63, "sub_color":   (212, 175, 55),  "sub_size":   45,
     "shadow": (5, 20, 15)},
 
    # both8 — binafsha, katta bo'sh joy
    {"file": "both8.png",
     "greet_y": 0.35, "greet_color": (212, 175, 55),  "greet_size": 60,
     "name_y":  0.45, "name_color":  (255, 215, 0),   "name_size":  80,
     "hol_y":   0.55, "hol_color":   (212, 175, 55),  "hol_size":   55,
     "sub_y":   0.65, "sub_color":   (212, 175, 55),  "sub_size":   45,
     "shadow": (30, 5, 40)},
 
    # both9 — ko'k yulduz shakli, markazda bo'sh
    {"file": "both9.png",
     "greet_y": 0.32, "greet_color": (212, 175, 55),  "greet_size": 55,
     "name_y":  0.42, "name_color":  (255, 215, 0),   "name_size":  70,
     "hol_y":   0.54, "hol_color":   (212, 175, 55),  "hol_size":   50,
     "sub_y":   0.63, "sub_color":   (212, 175, 55),  "sub_size":   40,
     "shadow": (5, 20, 40)},
 
    # both10 — oq yashil masjid, yuqori qism bo'sh
    {"file": "both10.png",
     "greet_y": 0.30, "greet_color": (150, 100, 20),  "greet_size": 60,
     "name_y":  0.40, "name_color":  (80,  50,  10),  "name_size":  80,
     "hol_y":   0.52, "hol_color":   (150, 100, 20),  "hol_size":   55,
     "sub_y":   0.61, "sub_color":   (150, 100, 20),  "sub_size":   45,
     "shadow": (200, 180, 140)},
]
 
QURBON_THEMES = [
    # qurbon1 — qo'y va masjid, to'la rasm, yuqori qism
    {"file": "qurbonhayiti1.png",
     "greet_x": 0.72, "greet_y": 0.35, "greet_color": (255, 215, 0), "greet_size": 60,
     "name_x":  0.72, "name_y":  0.44, "name_color":  (255, 215, 0),   "name_size":  78,
     "hol_x":   0.72, "hol_y":   0.55, "hol_color":   (255, 215, 0),   "hol_size":   55,
     "sub_x":   0.72, "sub_y":   0.64, "sub_color":   (255, 215, 0),  "sub_size":   45,
     "shadow": (50, 30, 0)
     },
 
    # qurbon2 — o'ng tomonda oq panel
    {"file": "qurbonhayiti2.png",
    "greet_x": 0.71, "greet_y": 0.25,  "greet_color": (100, 60, 10),  "greet_size": 53,
    "name_x":  0.71, "name_y":  0.34,  "name_color":  (80,  50, 10),  "name_size":  65,
    "hol_x":   0.70, "hol_y":   0.44,  "hol_color":   (100, 60, 10),  "hol_size":   55,
    "sub_x":   0.70, "sub_y":   0.54,  "sub_color":   (100, 60, 10),  "sub_size":   45,
    "shadow": (200, 180, 150),
    "x_offset": 280}, # o'ng panelga siljitish
 
    # qurbon3 — o'ng tomonda oq panel
    {"file": "qurbonhayiti3.png",
     "greet_x": 0.72, "greet_y": 0.25, "greet_color": (100, 60, 10),   "greet_size": 50,
     "name_x":  0.71, "name_y":  0.35, "name_color":  (80,  50,  10),  "name_size":  60,
     "hol_x":   0.71, "hol_y":   0.47, "hol_color":   (100, 60, 10),   "hol_size":   50,
     "sub_x":   0.71, "sub_y":   0.57, "sub_color":   (100, 60, 10),   "sub_size":   45,
     "shadow": (200, 180, 150),
     "x_offset": 280},
 
    # qurbon4 — oq fon, o'ng tomonda bo'sh
    {"file": "qurbonhayiti4.jpeg",
     "greet_x": 0.68, "greet_y": 0.25, "greet_color": (80,  50,  80),  "greet_size": 60,
     "name_x":  0.70, "name_y":  0.40, "name_color":  (60,  20,  80),  "name_size":  72,
     "hol_x":   0.70, "hol_y":   0.55, "hol_color":   (80,  50,  80),  "hol_size":   55,
     "sub_x":   0.70, "sub_y":   0.65, "sub_color":   (80,  50,  80),  "sub_size":   45,
     "shadow": (200, 200, 220),
     "x_offset": 280},
 
    # qurbon5 — ko'k masjid ramkasi
    {"file": "qurbonhayiti5.png",
     "greet_y": 0.33, "greet_color": (212, 175, 55),  "greet_size": 60,
     "name_y":  0.43, "name_color":  (255, 215, 0),   "name_size":  78,
     "hol_y":   0.55, "hol_color":   (212, 175, 55),  "hol_size":   55,
     "sub_y":   0.65, "sub_color":   (212, 175, 55),  "sub_size":   45,
     "shadow": (5, 15, 40)},
]
 
RAMAZON_THEMES = [
    # ramazon1 — chap masjid, o'ng qora bo'sh
    {"file": "ramazonhayiti1.jpeg",
     "greet_x": 0.73, "greet_y": 0.35, "greet_color": (212, 175, 55),  "greet_size": 50,
     "name_x":  0.77, "name_y":  0.46, "name_color":  (255, 215, 0),   "name_size":  60,
     "hol_x":   0.77, "hol_y":   0.56, "hol_color":   (212, 175, 55),  "hol_size":   45,
     "sub_x":   0.77, "sub_y":   0.66, "sub_color":   (212, 175, 55),  "sub_size":   40,
     "shadow": (5, 15, 40),
     "x_offset": 280},
 
    # ramazon2 — chiroq rasm, yuqori qism bo'sh
    {"file": "ramazonhayiti2.jpeg",
     "greet_x": 0.33, "greet_y": 0.35, "greet_color": (212, 175, 55),  "greet_size": 55,
     "name_x":  0.33, "name_y":  0.50, "name_color":  (255, 215, 0),   "name_size":  65,
     "hol_x":   0.33, "hol_y":   0.65, "hol_color":   (212, 175, 55),  "hol_size":   45,
     "sub_x":   0.33, "sub_y":   0.80, "sub_color":   (212, 175, 55),  "sub_size":   39,
     "shadow": (5, 10, 30)},
 
    # ramazon3 — ko'k oy masjid, pastki qism bo'sh
    {"file": "ramazonhayiti3.jpeg",
     "greet_x": 0.33, "greet_y": 0.07, "greet_color": (200, 230, 255), "greet_size": 57,
     "name_x":  0.33, "name_y":  0.15, "name_color":  (200, 230, 255),  "name_size":  69,
     "hol_x":   0.75, "hol_y":   0.82, "hol_color":   (200, 230, 255),  "hol_size":   55,
     "sub_x":   0.75, "sub_y":   0.92, "sub_color":   (200, 230, 255),  "sub_size":   45,
     "shadow": (5, 20, 50)},
 
    # ramazon4 — oltin gumbaz, markazda bo'sh joy
    {"file": "ramazonhayiti4.jpeg",
     "greet_x": 0.68, "greet_y": 0.42, "greet_color": (255, 215, 0),  "greet_size": 59,
     "name_x":  0.73, "name_y":  0.52, "name_color":  (255, 215, 0),   "name_size":  70,
     "hol_x":   0.73, "hol_y":   0.64, "hol_color":   (255, 215, 0),  "hol_size":   55,
     "sub_x":   0.73, "sub_y":   0.73, "sub_color":   (255, 215, 0),  "sub_size":   45,
     "shadow": (10, 5, 0)},
 
    # ramazon5 — galaktika, pastki qism bo'sh
    {"file": "ramazonhayiti5.jpeg",
     "greet_x": 0.53, "greet_y": 0.10, "greet_color": (255, 215, 0),  "greet_size": 60,
     "name_x":  0.53, "name_y":  0.20, "name_color":  (255, 215, 0),   "name_size":  72,
     "hol_x":   0.53, "hol_y":   0.30, "hol_color":   (255, 215, 0),  "hol_size":   55,
     "sub_x":   0.53, "sub_y":   0.37, "sub_color":   (255, 215, 0),  "sub_size":   45,
     "shadow": (10, 5, 0)},
]

# Bayram turiga qarab tegishli THEMES ni qaytaradi
def get_themes(holiday_type):
    if holiday_type == "qurbon":
        return BOTH_THEMES + QURBON_THEMES
    elif holiday_type == "ramazon":
        return BOTH_THEMES + RAMAZON_THEMES
    else:  # arafa
        return BOTH_THEMES

# Bot import qilishi uchun THEMES (arafa uchun)
THEMES = BOTH_THEMES


def get_font(size):
    font_paths = [
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/Library/Fonts/Georgia.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/freefont/FreeSerifBoldItalic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/georgia.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, size)
                print(f"Font topildi: {path}, size: {size}")
                return font
            except Exception as e:
                print(f"Fontni yuklashda xato: {path}, error: {e}")
                continue
    return ImageFont.load_default()


def draw_text(draw, text, font, y, width, color, shadow, x_offset=0, shadow_offset=3, x_ratio=None):
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
    except:
        tw = len(text) * 30

    if x_ratio is not None:
        x = int(width * x_ratio) - tw // 2
    elif x_offset:
        panel_width = width - x_offset
        x = x_offset + (panel_width - tw) // 2
    else:
        x = (width - tw) // 2

    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow)
    draw.text((x, y), text, font=font, fill=color)


def generate_card(name, holiday_type="qurbon", theme_index=None):
    themes = get_themes(holiday_type)

    if theme_index is None:
        theme_index = random.randint(0, len(themes) - 1)

    t = themes[theme_index % len(themes)]
    img_path = os.path.join(BASE_DIR, t["file"])

    if not os.path.exists(img_path):
        raise FileNotFoundError(f"Shablon topilmadi: {img_path}")

    img = Image.open(img_path).convert("RGB")
    w, h = img.size
    draw = ImageDraw.Draw(img)

    holiday_name, holiday_sub = HOLIDAY_TEXTS.get(holiday_type, ("Hayit", "muborak bo'lsin!"))
    x_off = t.get("x_offset", 0)

    greet_font = get_font(t["greet_size"])
    draw_text(draw, "Assalamu alaykum!", greet_font,
              int(h * t["greet_y"]), w, t["greet_color"], t["shadow"], x_off, x_ratio=t.get("greet_x"))
    

    name_font = get_font(t["name_size"])
    draw_text(draw, name, name_font,
              int(h * t["name_y"]), w, t["name_color"], t["shadow"], x_off, x_ratio=t.get("name_x"))

    hol_font = get_font(t["hol_size"])
    draw_text(draw, holiday_name, hol_font,
              int(h * t["hol_y"]), w, t["hol_color"], t["shadow"], x_off, x_ratio=t.get("hol_x"))

    sub_font = get_font(t["sub_size"])
    draw_text(draw, holiday_sub, sub_font,
              int(h * t["sub_y"]), w, t["sub_color"], t["shadow"], x_off, x_ratio=t.get("sub_x"))

    output_path = f"/tmp/hayit_{name}_{theme_index}.jpg"
    img.save(output_path, "JPEG", quality=95)
    return output_path