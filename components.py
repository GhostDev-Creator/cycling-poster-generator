import os
from typing import Tuple, Dict, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def get_font(size: int, font_path: Optional[str] = None) -> ImageFont.FreeTypeFont:
    if font_path and os.path.exists(font_path):
        try:
            return ImageFont.truetype(font_path, size)
        except OSError:
            pass
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()

def draw_text_with_shadow(
        draw: ImageDraw.ImageDraw,
        xy: Tuple[int, int],
        text: str,
        font: ImageFont.FreeTypeFont,
        fill_color: Tuple[int, ...],
        shadow_color: Tuple[int, ...] = (0, 0, 0, 160),
        offset: int = 2
) -> None:
    x, y = xy
    draw.text((x + offset, y + offset), text, font=font, fill=shadow_color)
    draw.text((x, y), text, font=font, fill=fill_color)

def draw_soft_blur_box(
        canvas,
        box_coords: Tuple[int, int, int, int],
        blur_radius: int = 20,
        fill_color: Tuple[int, int, int, int] = (10, 15, 20, 140),
        shape: str = "rectangle"
) -> None:
    """Renderiza um preenchimento com blur aplicado para destaque e contraste legível do texto base."""
    layer = Image.new("RGBA", (canvas.width, canvas.height), (0, 0, 0, 0))
    draw_layer = ImageDraw.Draw(layer)

    if shape == "ellipse":
        draw_layer.ellipse(box_coords, fill=fill_color)
    else:
        draw_layer.rounded_rectangle(box_coords, radius=16, fill=fill_color)

    blurred_layer = layer.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    canvas.image = Image.alpha_composite(canvas.image, blurred_layer)
    canvas.draw = ImageDraw.Draw(canvas.image)

def draw_header(canvas, start_loc: str, end_loc: str, cyclists: str, fonts: Dict[str, str],
                paleta: Dict[str, tuple]) -> None:
    x = canvas.get_x(0.08)
    y = canvas.get_y(0.08)

    font_title = get_font(int(canvas.height * 0.015), fonts.get("bold"))
    font_subtitle = get_font(int(canvas.height * 0.012), fonts.get("medium"))

    title_text = f"{start_loc.upper()}  \u2192  {end_loc.upper()}"

    draw_text_with_shadow(canvas.draw, (x, y), title_text, font_title, paleta["texto_principal"])
    draw_text_with_shadow(canvas.draw, (x, y + int(canvas.height * 0.024)), cyclists.upper(), font_subtitle,
                          paleta["texto_secundario"])

    y_line = y + int(canvas.height * 0.048)
    canvas.draw.line([(x, y_line), (x + int(canvas.width * 0.12), y_line)], fill=(255, 255, 255, 180), width=1)

def _draw_icon_fallback(draw: ImageDraw.ImageDraw, icon_type: str, cx: int, cy: int, r: int, color: tuple) -> None:
    """Implementação poligonal nativa de ícones de fallback na ausência de PNGs do sistema."""
    w = max(1, int(r * 0.15))
    if icon_type == "icon_dist":
        p1, p2, p3 = (cx - r * 0.6, cy + r * 0.5), (cx, cy - r * 0.4), (cx + r * 0.7, cy + r * 0.2)
        draw.line([p1, p2, p3], fill=color, width=w, joint="curve")
        draw.ellipse([p1[0] - w, p1[1] - w, p1[0] + w, p1[1] + w], fill=color)
        draw.ellipse([p3[0] - w, p3[1] - w, p3[0] + w, p3[1] + w], fill=color)
    elif icon_type == "icon_time":
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=w)
        draw.line([(cx, cy - r - w * 2), (cx, cy - r)], fill=color, width=w)
        draw.line([(cx, cy), (cx, cy - r * 0.5)], fill=color, width=w)
        draw.line([(cx, cy), (cx + r * 0.4, cy)], fill=color, width=w)
    elif icon_type == "icon_elev":
        base_y = cy + r * 0.8
        draw.line([(cx - r * 1.2, base_y), (cx + r * 1.2, base_y)], fill=color, width=w)
        draw.line([(cx - r * 1.1, base_y), (cx - r * 0.2, cy - r * 0.7), (cx + r * 0.4, base_y)], fill=color, width=w,
                  joint="curve")
        draw.line([(cx + r * 0.1, cy), (cx + r * 0.6, cy - r * 0.3), (cx + r * 1.1, base_y)], fill=color, width=w,
                  joint="curve")
    elif icon_type == "icon_speed":
        draw.arc([cx - r, cy - r * 0.8, cx + r, cy + r * 1.2], start=150, end=30, fill=color, width=w)
        draw.line([(cx, cy + r * 0.2), (cx + r * 0.5, cy - r * 0.4)], fill=color, width=w)
        draw.ellipse([cx - w, cy + r * 0.2 - w, cx + w, cy + r * 0.2 + w], fill=color)

def draw_metrics(canvas, distance: float, time_str: str, elevation: int, speed: float, fonts: Dict[str, str],
                 paleta: Dict[str, tuple]) -> None:
    x_base = canvas.get_x(0.08)
    y_start = canvas.get_y(0.18)
    spacing = canvas.get_y(0.065)

    font_label = get_font(int(canvas.height * 0.013), fonts.get("regular"))
    font_value = get_font(int(canvas.height * 0.035), fonts.get("bold"))

    metrics = [
        ("icon_dist", "DISTÂNCIA", f"{distance:.2f}".replace('.', ',') + " km"),
        ("icon_time", "TEMPO", time_str),
        ("icon_elev", "GANHO DE ELEVAÇÃO", f"{elevation} m"),
        ("icon_speed", "VELOCIDADE MÉDIA", f"{speed:.1f}".replace('.', ',') + " km/h")
    ]

    icon_size = int(canvas.width * 0.056)

    for i, (icon_name, label, value) in enumerate(metrics):
        y_current = y_start + (i * spacing)
        visual_center_y = y_current + int(canvas.height * 0.026)
        icon_y = visual_center_y - (icon_size // 2)

        icon_path = f"assets/icons/{icon_name}.png"

        if os.path.exists(icon_path):
            try:
                icon_img = Image.open(icon_path).convert("RGBA")
                icon_img = icon_img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
                canvas.image.paste(icon_img, (x_base, icon_y), icon_img)
            except OSError:
                _draw_icon_fallback(canvas.draw, icon_name, x_base + icon_size // 2, icon_y + icon_size // 2,
                                    icon_size // 2, paleta["texto_principal"])
        else:
            _draw_icon_fallback(canvas.draw, icon_name, x_base + icon_size // 2, icon_y + icon_size // 2,
                                icon_size // 2, paleta["texto_principal"])

        text_x = x_base + icon_size + int(canvas.width * 0.035)

        draw_text_with_shadow(canvas.draw, (text_x, y_current), label, font_label, paleta["texto_secundario"])
        draw_text_with_shadow(canvas.draw, (text_x, y_current + int(canvas.height * 0.018)), value, font_value,
                              paleta["texto_principal"])

def draw_footer(canvas, message: str, font_path: str, paleta: Dict[str, tuple]) -> None:
    if not message.strip():
        return

    if " " in message and "\n" not in message:
        partes = message.split(" ", 1)
        message = f"{partes[0]}\n{partes[1]}"

    font_footer = get_font(int(canvas.height * 0.045), font_path)

    # Renderiza em uma camada auxiliar transparente para permitir a rotação posterior
    temp_img = Image.new("RGBA", (int(canvas.width * 0.6), int(canvas.height * 0.2)), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_img)

    try:
        temp_draw.multiline_text((20, 20), message, font=font_footer, fill=(0, 0, 0, 150), align="center")
        temp_draw.multiline_text((18, 18), message, font=font_footer, fill=paleta["texto_principal"], align="center")
    except AttributeError:
        # Fallback para versões legadas do Pillow
        temp_draw.text((20, 20), message, font=font_footer, fill=(0, 0, 0, 150))
        temp_draw.text((18, 18), message, font=font_footer, fill=paleta["texto_principal"])

    box = temp_img.getbbox()
    if box:
        temp_img = temp_img.crop(box)

    x = canvas.width - temp_img.width - canvas.get_x(0.06)
    y = canvas.height - temp_img.height - canvas.get_y(0.05)

    padding_x = int(canvas.width * 0.08)
    padding_y = int(canvas.height * 0.05)
    footer_box = (
        x - padding_x,
        y - padding_y,
        x + temp_img.width + padding_x,
        y + temp_img.height + padding_y
    )

    draw_soft_blur_box(canvas, footer_box, blur_radius=60, fill_color=(0, 0, 0, 100), shape="ellipse")

    rotated_txt = temp_img.rotate(10, expand=True, resample=Image.BICUBIC)

    x_rot = x - (rotated_txt.width - temp_img.width) // 2
    y_rot = y - (rotated_txt.height - temp_img.height) // 2

    canvas.image.paste(rotated_txt, (x_rot, y_rot), rotated_txt)
    canvas.draw = ImageDraw.Draw(canvas.image)