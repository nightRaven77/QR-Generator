import os
import math
import sys
import subprocess
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import qrcode
from qrcode.constants import (
    ERROR_CORRECT_L,
    ERROR_CORRECT_M,
    ERROR_CORRECT_Q,
    ERROR_CORRECT_H
)

ERROR_CORRECTION_MAP = {
    "L": ERROR_CORRECT_L,
    "M": ERROR_CORRECT_M,
    "Q": ERROR_CORRECT_Q,
    "H": ERROR_CORRECT_H,
}

FONT_FAMILY_MAP = {
    "Sans-Serif": ["Helvetica", "Helvetica Neue", "Arial", "DejaVuSans-Bold", "LiberationSans-Bold"],
    "Serif": ["Times New Roman", "Times", "Georgia", "DejaVuSerif-Bold", "LiberationSerif-Bold"],
    "Monospace": ["Courier New", "Courier", "Menlo", "DejaVuSansMono-Bold", "LiberationMono-Bold"],
    "Trebuchet": ["Trebuchet MS", "Arial"],
    "Impact": ["Impact", "Arial Black", "Helvetica-Bold"],
    "Futura": ["Futura", "Avenir", "Century Gothic", "Arial"]
}

def hex_to_rgb(hex_str) -> tuple:
    """Convierte cadena Hex (#RRGGBB o RRGGBB) o tupla a Tupla RGB (R, G, B)"""
    if isinstance(hex_str, tuple):
        return hex_str[:3]
    if not isinstance(hex_str, str):
        return (0, 0, 0)
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = "".join([c*2 for c in hex_str])
    if len(hex_str) != 6:
        return (0, 0, 0)
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def calculate_contrast_ratio(color1: tuple, color2: tuple) -> float:
    """Calcula la relación de contraste de color según el estándar WCAG 2.1 (W3C)."""
    def relative_luminance(rgb: tuple) -> float:
        r, g, b = [x / 255.0 for x in rgb]
        r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    l1 = relative_luminance(color1)
    l2 = relative_luminance(color2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

def is_finder_pattern(r: int, c: int, matrix_size: int) -> bool:
    """Determina si una celda (r, c) pertenece a uno de los 3 Finder Patterns (7x7)"""
    if r < 7 and c < 7:
        return True
    if r < 7 and c >= matrix_size - 7:
        return True
    if r >= matrix_size - 7 and c < 7:
        return True
    return False

def get_best_system_font(font_size: int, font_family: str = "Sans-Serif"):
    """Busca la fuente según la familia elegida (Sans-Serif, Serif, Monospace, Trebuchet, Impact, Futura)"""
    candidates = FONT_FAMILY_MAP.get(font_family, FONT_FAMILY_MAP["Sans-Serif"])
    for font_name in candidates:
        try:
            return ImageFont.truetype(font_name, font_size)
        except Exception:
            pass
    try:
        return ImageFont.load_default()
    except Exception:
        return None

def draw_custom_rounded_cell(draw, x, y, box_size, radius, fill_rgb, back_rgb, tl=True, tr=True, br=True, bl=True):
    """Dibuja una celda con esquinas redondeadas seleccionables sin el bug interno de Pillow."""
    draw.rectangle([x, y, x + box_size, y + box_size], fill=fill_rgb)
    r = min(radius, box_size // 2)
    if r <= 0:
        return
    d = r * 2
    if tl:
        draw.rectangle([x, y, x + r, y + r], fill=back_rgb)
        draw.pieslice([x, y, x + d, y + d], start=180, end=270, fill=fill_rgb)
    if tr:
        draw.rectangle([x + box_size - r, y, x + box_size, y + r], fill=back_rgb)
        draw.pieslice([x + box_size - d, y, x + box_size, y + d], start=270, end=360, fill=fill_rgb)
    if br:
        draw.rectangle([x + box_size - r, y + box_size - r, x + box_size, y + box_size], fill=back_rgb)
        draw.pieslice([x + box_size - d, y + box_size - d, x + box_size, y + box_size], start=0, end=90, fill=fill_rgb)
    if bl:
        draw.rectangle([x, y + box_size - r, x + r, y + box_size], fill=back_rgb)
        draw.pieslice([x, y + box_size - d, x + d, y + box_size], start=90, end=180, fill=fill_rgb)

def makeQRDinamico(
    data: str,
    logo_path: str = None,
    back_color: tuple = (255, 255, 255),
    module_color: tuple = (9, 9, 11),
    finder_frame_color: tuple = None,
    finder_center_color: tuple = None,
    logo_background_color: tuple = None,
    module_shape: str = "square",
    finder_frame_shape: str = "square",
    finder_center_shape: str = "square",
    error_correction: str = "H",
    logo_ratio: float = 0.22,
    logo_background_pad: bool = True,
    module_scale: float = 1.0,
    card_corner_radius: float = 0.0,
    top_heading: str = "",
    top_heading_color: tuple = None,
    top_heading_size: int = 24,
    bottom_caption: str = "",
    bottom_caption_color: tuple = None,
    bottom_caption_size: int = 24,
    font_family: str = "Sans-Serif",
    target_resolution: int = 1200,
    canvas_padding_px: int = 40,
    box_size: int = 14,
    border: int = 4
) -> Image.Image:
    """
    Genera la imagen PIL del código QR con espaciado vertical estrecho para textos y selección de tipografía.
    """
    if not data:
        data = "https://homielab.com"

    ec_level = ERROR_CORRECTION_MAP.get(error_correction.upper(), ERROR_CORRECT_H)
    back_rgb = hex_to_rgb(back_color)
    module_rgb = hex_to_rgb(module_color)
    ff_rgb = hex_to_rgb(finder_frame_color) if finder_frame_color else module_rgb
    fc_rgb = hex_to_rgb(finder_center_color) if finder_center_color else ff_rgb
    logo_bg_rgb = hex_to_rgb(logo_background_color) if logo_background_color else back_rgb

    head_rgb = hex_to_rgb(top_heading_color) if top_heading_color else module_rgb
    cap_rgb = hex_to_rgb(bottom_caption_color) if bottom_caption_color else module_rgb

    # Generar matriz QR
    qr = qrcode.QRCode(
        version=None,
        error_correction=ec_level,
        box_size=1,
        border=0
    )
    qr.add_data(data)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    matrix_size = len(matrix)

    total_cells = matrix_size + (border * 2)
    qr_draw_size = total_cells * box_size

    qr_canvas = Image.new("RGBA", (qr_draw_size, qr_draw_size), back_rgb + (255,))
    draw = ImageDraw.Draw(qr_canvas)

    m_scale = max(0.5, min(1.0, module_scale))
    m_pad = int((1.0 - m_scale) * (box_size / 2.0))

    # 1. Dibujar Módulos del Cuerpo
    for r in range(matrix_size):
        for c in range(matrix_size):
            if matrix[r][c] and not is_finder_pattern(r, c, matrix_size):
                x = (c + border) * box_size
                y = (r + border) * box_size

                mx1 = x + m_pad
                my1 = y + m_pad
                mx2 = x + box_size - m_pad
                my2 = y + box_size - m_pad
                mw = mx2 - mx1

                has_left = (c > 0) and matrix[r][c-1] and not is_finder_pattern(r, c-1, matrix_size)
                has_right = (c < matrix_size - 1) and matrix[r][c+1] and not is_finder_pattern(r, c+1, matrix_size)
                has_top = (r > 0) and matrix[r-1][c] and not is_finder_pattern(r-1, c, matrix_size)
                has_bottom = (r < matrix_size - 1) and matrix[r+1][c] and not is_finder_pattern(r+1, c, matrix_size)

                if module_shape in ["dots", "circle"]:
                    pad = int(box_size * 0.12)
                    draw.ellipse([mx1 + pad, my1 + pad, mx2 - pad, my2 - pad], fill=module_rgb)

                elif module_shape == "organic":
                    draw_custom_rounded_cell(draw, mx1, my1, mw, int(mw * 0.42), module_rgb, back_rgb, True, True, True, True)

                elif module_shape in ["leaf", "teardrop"]:
                    draw_custom_rounded_cell(draw, mx1, my1, mw, int(mw * 0.45), module_rgb, back_rgb, False, True, True, True)

                elif module_shape == "soft_rounded":
                    draw_custom_rounded_cell(draw, mx1, my1, mw, int(mw * 0.3), module_rgb, back_rgb, True, True, True, True)

                elif module_shape == "gapped_square":
                    gap = int(box_size * 0.12)
                    draw.rectangle([x + gap, y + gap, x + box_size - gap, y + box_size - gap], fill=module_rgb)

                elif module_shape == "diamond":
                    cx, cy = x + box_size / 2, y + box_size / 2
                    h_w = mw / 2.2
                    points = [(cx, cy - h_w), (cx + h_w, cy), (cx, cy + h_w), (cx - h_w, cy)]
                    draw.polygon(points, fill=module_rgb)

                elif module_shape == "pebble":
                    pad = int(box_size * 0.1)
                    draw.ellipse([mx1 + pad, my1 + pad, mx2 - pad, my2 - pad], fill=module_rgb)

                elif module_shape == "star":
                    cx, cy = x + box_size / 2, y + box_size / 2
                    q_w = mw / 4
                    points = [
                        (cx, cy - mw/2), (cx + q_w, cy - q_w), (cx + mw/2, cy), (cx + q_w, cy + q_w),
                        (cx, cy + mw/2), (cx - q_w, cy + q_w), (cx - mw/2, cy), (cx - q_w, cy - q_w)
                    ]
                    draw.polygon(points, fill=module_rgb)

                elif module_shape == "heart":
                    cx, cy = x + box_size / 2, y + box_size / 2
                    h_w = mw / 2
                    points = [
                        (cx, cy + h_w * 0.8), (cx - h_w * 0.9, cy), (cx - h_w * 0.4, cy - h_w * 0.8),
                        (cx, cy - h_w * 0.3), (cx + h_w * 0.4, cy - h_w * 0.8), (cx + h_w * 0.9, cy)
                    ]
                    draw.polygon(points, fill=module_rgb)

                elif module_shape == "cross":
                    cx, cy = x + box_size / 2, y + box_size / 2
                    w3 = mw / 3
                    draw.rectangle([cx - w3/2, cy - mw/2, cx + w3/2, cy + mw/2], fill=module_rgb)
                    draw.rectangle([cx - mw/2, cy - w3/2, cx + mw/2, cy + w3/2], fill=module_rgb)

                elif module_shape == "rounded":
                    tl = (not has_top) and (not has_left)
                    tr = (not has_top) and (not has_right)
                    br = (not has_bottom) and (not has_right)
                    bl = (not has_bottom) and (not has_left)
                    draw_custom_rounded_cell(draw, x, y, box_size, int(box_size * 0.45), module_rgb, back_rgb, tl, tr, br, bl)

                elif module_shape == "horizontal_bars":
                    hx1 = x if has_left else (x + int(box_size * 0.1))
                    hx2 = (x + box_size) if has_right else (x + box_size - int(box_size * 0.1))
                    hy1 = y + int(box_size * 0.16)
                    hy2 = y + box_size - int(box_size * 0.16)
                    draw.rectangle([hx1, hy1, hx2, hy2], fill=module_rgb)

                elif module_shape == "vertical_bars":
                    vx1 = x + int(box_size * 0.16)
                    vx2 = x + box_size - int(box_size * 0.16)
                    vy1 = y if has_top else (y + int(box_size * 0.1))
                    vy2 = (y + box_size) if has_bottom else (y + box_size - int(box_size * 0.1))
                    draw.rectangle([vx1, vy1, vx2, vy2], fill=module_rgb)

                else: # square
                    draw.rectangle([x, y, x + box_size, y + box_size], fill=module_rgb)

    # 2. Dibujar Finder Patterns
    finder_positions = [
        (0, 0),
        (0, matrix_size - 7),
        (matrix_size - 7, 0)
    ]

    for r_off, c_off in finder_positions:
        fx = (c_off + border) * box_size
        fy = (r_off + border) * box_size
        fw = 7 * box_size

        draw.rectangle([fx, fy, fx + fw, fy + fw], fill=back_rgb)

        if finder_frame_shape == "circle":
            draw.ellipse([fx, fy, fx + fw, fy + fw], fill=ff_rgb)
            inner_pad = box_size
            draw.ellipse([fx + inner_pad, fy + inner_pad, fx + fw - inner_pad, fy + fw - inner_pad], fill=back_rgb)
        elif finder_frame_shape in ["soft_square", "rounded"]:
            radius = int(box_size * 1.5)
            draw.rounded_rectangle([fx, fy, fx + fw, fy + fw], radius=radius, fill=ff_rgb)
            inner_pad = box_size
            draw.rounded_rectangle([fx + inner_pad, fy + inner_pad, fx + fw - inner_pad, fx + fw - inner_pad], radius=int(radius * 0.6), fill=back_rgb)
        elif finder_frame_shape == "leaf":
            draw_custom_rounded_cell(draw, fx, fy, fw, int(box_size * 2.2), ff_rgb, back_rgb, False, True, True, True)
            inner_pad = box_size
            draw_custom_rounded_cell(draw, fx + inner_pad, fy + inner_pad, fw - 2 * inner_pad, int(box_size * 1.2), back_rgb, ff_rgb, False, True, True, True)
        elif finder_frame_shape == "diamond":
            cx, cy = fx + fw / 2, fy + fw / 2
            draw.polygon([(cx, fy), (fx + fw, cy), (cx, fy + fw), (fx, cy)], fill=ff_rgb)
            draw.polygon([(cx, fy + box_size), (fx + fw - box_size, cy), (cx, fy + fw - box_size), (fx + box_size, cy)], fill=back_rgb)
        elif finder_frame_shape == "shield":
            draw_custom_rounded_cell(draw, fx, fy, fw, int(box_size * 2.0), ff_rgb, back_rgb, True, True, False, False)
            inner_pad = box_size
            draw_custom_rounded_cell(draw, fx + inner_pad, fy + inner_pad, fw - 2 * inner_pad, int(box_size * 1.2), back_rgb, ff_rgb, True, True, False, False)
        else: # square
            draw.rectangle([fx, fy, fx + fw, fy + fw], fill=ff_rgb)
            inner_pad = box_size
            draw.rectangle([fx + inner_pad, fy + inner_pad, fx + fw - inner_pad, fy + fw - inner_pad], fill=back_rgb)

        cx = fx + (2 * box_size)
        cy = fy + (2 * box_size)
        cw = 3 * box_size

        if finder_center_shape == "circle":
            draw.ellipse([cx, cy, cx + cw, cy + cw], fill=fc_rgb)
        elif finder_center_shape in ["soft_square", "rounded"]:
            radius = int(box_size * 0.5)
            draw.rounded_rectangle([cx, cy, cx + cw, cy + cw], radius=radius, fill=fc_rgb)
        elif finder_center_shape == "diamond":
            mcx, mcy = cx + cw / 2, cy + cw / 2
            draw.polygon([(mcx, cy), (cx + cw, mcy), (mcx, cy + cw), (cx, mcy)], fill=fc_rgb)
        elif finder_center_shape == "leaf":
            draw_custom_rounded_cell(draw, cx, cy, cw, int(box_size * 0.6), fc_rgb, back_rgb, False, True, True, True)
        elif finder_center_shape == "star":
            mcx, mcy = cx + cw / 2, cy + cw / 2
            qw = cw / 4
            points = [
                (mcx, cy), (mcx + qw, mcy - qw), (cx + cw, mcy), (mcx + qw, mcy + qw),
                (mcx, cy + cw), (mcx - qw, mcy + qw), (cx, mcy), (mcx - qw, mcy - qw)
            ]
            draw.polygon(points, fill=fc_rgb)
        else: # square
            draw.rectangle([cx, cy, cx + cw, cy + cw], fill=fc_rgb)

    # 3. Incrustar Logo Central
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo_target_size = int(qr_draw_size * logo_ratio)
            logo.thumbnail((logo_target_size, logo_target_size), Image.Resampling.LANCZOS)
            lw, lh = logo.size

            pos_x = (qr_draw_size - lw) // 2
            pos_y = (qr_draw_size - lh) // 2

            if logo_background_pad:
                pad = int(box_size * 0.5)
                bg_box = Image.new("RGBA", (lw + pad * 2, lh + pad * 2), (0, 0, 0, 0))
                draw_bg = ImageDraw.Draw(bg_box)
                draw_bg.rounded_rectangle([0, 0, lw + pad * 2, lh + pad * 2], radius=int(box_size * 0.5), fill=logo_bg_rgb + (255,))
                qr_canvas.paste(bg_box, (pos_x - pad, pos_y - pad), bg_box)

            qr_canvas.paste(logo, (pos_x, pos_y), logo)
        except Exception as e:
            print(f"Error cargando logo: {e}")

    # 4. Construir Lienzo Final con Ajuste de Texto Ajustado
    font_h = get_best_system_font(top_heading_size, font_family) if top_heading else None
    font_c = get_best_system_font(bottom_caption_size, font_family) if bottom_caption else None

    # Medir altura exacta de textos sin espacios inflados
    dummy_img = Image.new("RGBA", (1, 1))
    measurer = ImageDraw.Draw(dummy_img)

    head_w, head_h = 0, 0
    if top_heading and font_h:
        tb_h = measurer.textbbox((0, 0), top_heading, font=font_h)
        head_w = tb_h[2] - tb_h[0]
        head_h = tb_h[3] - tb_h[1]

    cap_w, cap_h = 0, 0
    if bottom_caption and font_c:
        tb_c = measurer.textbbox((0, 0), bottom_caption, font=font_c)
        cap_w = tb_c[2] - tb_c[0]
        cap_h = tb_c[3] - tb_c[1]

    # Separación estrecha (text_gap de 8px a 12px)
    text_gap = int(max(6, box_size * 0.5))

    header_space = (head_h + text_gap) if top_heading else 0
    caption_space = (cap_h + text_gap) if bottom_caption else 0

    pad_px = int(canvas_padding_px)

    total_w = qr_draw_size + (pad_px * 2)
    total_h = qr_draw_size + (pad_px * 2) + header_space + caption_space

    final_img = Image.new("RGBA", (total_w, total_h), back_rgb + (255,))
    final_draw = ImageDraw.Draw(final_img)

    qr_x = pad_px
    qr_y = pad_px + header_space
    final_img.paste(qr_canvas, (qr_x, qr_y), qr_canvas)

    # Dibujar Top Heading ajustado
    if top_heading and font_h:
        tx = (total_w - head_w) // 2
        ty = pad_px
        final_draw.text((tx, ty), top_heading, fill=head_rgb, font=font_h)

    # Dibujar Bottom Caption ajustado
    if bottom_caption and font_c:
        tx = (total_w - cap_w) // 2
        ty = qr_y + qr_draw_size + (text_gap // 2)
        final_draw.text((tx, ty), bottom_caption, fill=cap_rgb, font=font_c)

    # Redondeo de Tarjeta Completa
    if card_corner_radius > 0:
        c_rad = int(min(total_w, total_h) * (card_corner_radius / 100.0))
        if c_rad > 0:
            mask = Image.new("L", (total_w, total_h), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle([0, 0, total_w, total_h], radius=c_rad, fill=255)

            rounded_card = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))
            rounded_card.paste(final_img, (0, 0), mask)
            final_img = rounded_card

    if target_resolution and target_resolution != total_w:
        final_img = final_img.resize((target_resolution, int(target_resolution * (total_h / total_w))), Image.Resampling.LANCZOS)

    return final_img

def copy_image_to_clipboard(pil_img: Image.Image) -> bool:
    """Copia la imagen PIL directamente al portapapeles de Windows / MacOS"""
    try:
        if sys.platform == "darwin":
            output = BytesIO()
            pil_img.save(output, format="PNG")
            data = output.getvalue()
            process = subprocess.Popen(["pbcopy", "-Device", "clipboard"], stdin=subprocess.PIPE)
            process.communicate(data)
            return True
        elif sys.platform == "win32":
            output = BytesIO()
            pil_img.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]
            import win32clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
            return True
    except Exception as e:
        print(f"Error copiando al portapapeles: {e}")
    return False

def save_qr_as_svg(data: str, save_path: str, back_color: tuple, module_color: tuple) -> bool:
    """Exporta el código QR en formato vectorial SVG verdadero"""
    try:
        import qrcode.image.svg
        factory = qrcode.image.svg.SvgPathImage
        qr = qrcode.QRCode(image_factory=factory, error_correction=ERROR_CORRECT_H)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color=module_color, back_color=back_color)
        img.save(save_path)
        return True
    except Exception as e:
        print(f"Error guardando SVG: {e}")
        return False
