import os
import sys
import subprocess
from io import BytesIO
from PIL import Image, ImageDraw
import qrcode
from qrcode.constants import (
    ERROR_CORRECT_L,
    ERROR_CORRECT_M,
    ERROR_CORRECT_Q,
    ERROR_CORRECT_H
)

# Map string keys to qrcode error correction constants
ERROR_CORRECTION_MAP = {
    "L": ERROR_CORRECT_L,
    "M": ERROR_CORRECT_M,
    "Q": ERROR_CORRECT_Q,
    "H": ERROR_CORRECT_H,
}


def hex_to_rgb(hex_str: str) -> tuple:
    """Convierte cadena Hex (#RRGGBB o RRGGBB) a Tupla RGB (R, G, B)"""
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
    """
    Calcula la relación de contraste de color según el estándar WCAG 2.1 (W3C).

    Determina si la diferencia de brillo entre dos colores (ej. módulos del QR vs. fondo)
    es suficiente para que las cámaras de los smartphones puedan escanear el código.

    Valores de retorno típicos:
      - 21.0 : 1  -> Máximo contraste (Negro absoluto sobre Blanco puro).
      - >= 3.0 : 1 -> Contraste suficiente para lectura garantizada por cámaras.
      - < 3.0 : 1  -> Contraste bajo (alerta de posible dificultad al escanear).

    Args:
        color1 (tuple): Tupla RGB del primer color, ej. (0, 0, 0)
        color2 (tuple): Tupla RGB del segundo color, ej. (255, 255, 255)

    Returns:
        float: Relación de contraste entre 1.0 (sin contraste) y 21.0 (máximo contraste).
    """
    def relative_luminance(rgb: tuple) -> float:
        """
        Calcula la luminancia relativa física basada en la norma sRGB (IEC 61966-2-1:1999).
        Convierte el espacio de color digital no lineal a la energía luminosa real.
        """
        # Paso 1: Normalización de canales RGB de escala 0-255 a escala decimal 0.0 - 1.0
        r, g, b = [x / 255.0 for x in rgb]

        # Paso 2: Corrección Gamma (Linealización sRGB)
        # La pantalla no emite luz linealmente. Se eliminan las constantes de distorsión gamma:
        #   - 0.03928: Umbral de sombras oscuras (RGB ~10/255). Por debajo, la respuesta es lineal.
        #   - 12.92: Pendiente lineal ajustada para sombras profundas.
        #   - 0.055 y 1.055: Desplazamiento del 5.5% para compensar reflejos de luz ambiental.
        #   - ** 2.4: Exponente Gamma que simula la conversión de energía eléctrica a fotones en pantallas.
        r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4

        # Paso 3: Ponderación de Luminancia según la Biología Ocular Humana
        # El ojo humano es muy sensible al verde, moderadamente al rojo y muy poco al azul.
        #   - Verde (G): 71.52% de la percepción de brillo.
        #   - Rojo (R):  21.26% de la percepción de brillo.
        #   - Azul (B):   7.22% de la percepción de brillo.
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    # Obtener luminancia relativa física de ambos colores
    l1 = relative_luminance(color1)
    l2 = relative_luminance(color2)

    # Identificar cuál es el color más claro y cuál el más oscuro
    lighter = max(l1, l2)
    darker = min(l1, l2)

    # Paso 4: Proporción final de contraste WCAG
    # El valor +0.05 es un ajuste ambiental para evitar la división por cero con negro absoluto.
    return (lighter + 0.05) / (darker + 0.05)


def is_finder_pattern(r: int, c: int, matrix_size: int) -> bool:
    """Determina si una celda (row, col) pertenece a uno de los 3 Finder Patterns de las esquinas"""
    # Superior Izquierda: rows 0-6, cols 0-6
    if r < 7 and c < 7:
        return True
    # Superior Derecha: rows 0-6, cols (size-7) a size-1
    if r < 7 and c >= matrix_size - 7:
        return True
    # Inferior Izquierda: rows (size-7) a size-1, cols 0-6
    if r >= matrix_size - 7 and c < 7:
        return True
    return False


def makeQRDinamico(
    data: str,
    logo_path: str = None,
    back_color: tuple = (255, 255, 255),
    module_color: tuple = (9, 9, 11),
    finder_frame_color: tuple = None,
    finder_center_color: tuple = None,
    # square, rounded, dots, organic, diamond, horizontal, vertical
    module_shape: str = "square",
    finder_frame_shape: str = "square",  # square, circle, rounded
    finder_center_shape: str = "square",  # square, circle
    error_correction: str = "H",        # L, M, Q, H
    logo_ratio: float = 0.22,
    box_size: int = 14,
    border: int = 4
) -> Image.Image:
    """
    Genera una imagen PIL del código QR con estilos avanzados de módulos,
    patrones de búsqueda (finder eyes) independientes, colores personalizados y logo central.
    """
    if not data:
        data = ""

    ec_level = ERROR_CORRECTION_MAP.get(
        error_correction.upper(), ERROR_CORRECT_H)
    back_rgb = hex_to_rgb(back_color)
    module_rgb = hex_to_rgb(module_color)
    ff_rgb = hex_to_rgb(
        finder_frame_color) if finder_frame_color else module_rgb
    fc_rgb = hex_to_rgb(finder_center_color) if finder_center_color else ff_rgb

    # Generar matriz QR usando la librería qrcode
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

    # Dimensiones totales con borde
    total_cells = matrix_size + (border * 2)
    img_size = total_cells * box_size

    # Crear lienzo en blanco
    img = Image.new("RGBA", (img_size, img_size), back_rgb + (255,))
    draw = ImageDraw.Draw(img)

    # 1. Dibujar módulos del cuerpo (excluyendo la zona de los 3 Finder patterns)
    for r in range(matrix_size):
        for c in range(matrix_size):
            if matrix[r][c] and not is_finder_pattern(r, c, matrix_size):
                x = (c + border) * box_size
                y = (r + border) * box_size

                if module_shape in ["dots", "circle"]:
                    padding = box_size * 0.1
                    draw.ellipse([x + padding, y + padding, x + box_size -
                                 padding, y + box_size - padding], fill=module_rgb)
                elif module_shape == "rounded":
                    radius = box_size * 0.35
                    draw.rounded_rectangle(
                        [x, y, x + box_size - 0.5, y + box_size - 0.5], radius=radius, fill=module_rgb)
                elif module_shape == "diamond":
                    cx, cy = x + box_size / 2, y + box_size / 2
                    points = [(cx, y), (x + box_size, cy),
                              (cx, y + box_size), (x, cy)]
                    draw.polygon(points, fill=module_rgb)
                elif module_shape == "organic":
                    # Esquinas alternadas redondeadas
                    radius = box_size * 0.45
                    draw.rounded_rectangle(
                        [x + 0.5, y + 0.5, x + box_size - 0.5, y + box_size - 0.5], radius=radius, fill=module_rgb)
                elif module_shape == "horizontal":
                    draw.rectangle(
                        [x, y + box_size*0.2, x + box_size, y + box_size*0.8], fill=module_rgb)
                elif module_shape == "vertical":
                    draw.rectangle(
                        [x + box_size*0.2, y, x + box_size*0.8, y + box_size], fill=module_rgb)
                else:  # square
                    draw.rectangle(
                        [x, y, x + box_size, y + box_size], fill=module_rgb)

    # 2. Dibujar los 3 Finder Patterns (Ojos) en las esquinas
    finder_positions = [
        (0, 0),                            # Superior Izquierda
        (0, matrix_size - 7),               # Superior Derecha
        (matrix_size - 7, 0)                # Inferior Izquierda
    ]

    for r_off, c_off in finder_positions:
        fx = (c_off + border) * box_size
        fy = (r_off + border) * box_size
        fw = 7 * box_size

        # A) Limpiar área del Finder con color de fondo
        draw.rectangle([fx, fy, fx + fw, fy + fw], fill=back_rgb)

        # B) Dibujar Marco Exterior (7x7 celdas, grosor 1 celda)
        if finder_frame_shape == "circle":
            draw.ellipse([fx, fy, fx + fw, fy + fw], fill=ff_rgb)
            inner_pad = box_size
            draw.ellipse([fx + inner_pad, fy + inner_pad, fx +
                         fw - inner_pad, fy + fw - inner_pad], fill=back_rgb)
        elif finder_frame_shape == "rounded":
            radius = box_size * 1.5
            draw.rounded_rectangle(
                [fx, fy, fx + fw, fy + fw], radius=radius, fill=ff_rgb)
            inner_pad = box_size
            draw.rounded_rectangle([fx + inner_pad, fy + inner_pad, fx + fw -
                                   inner_pad, fy + fw - inner_pad], radius=radius * 0.6, fill=back_rgb)
        else:  # square
            draw.rectangle([fx, fy, fx + fw, fy + fw], fill=ff_rgb)
            inner_pad = box_size
            draw.rectangle([fx + inner_pad, fy + inner_pad, fx +
                           fw - inner_pad, fy + fw - inner_pad], fill=back_rgb)

        # C) Dibujar Centro Interior (3x3 celdas)
        cx = fx + (2 * box_size)
        cy = fy + (2 * box_size)
        cw = 3 * box_size

        if finder_center_shape == "circle":
            draw.ellipse([cx, cy, cx + cw, cy + cw], fill=fc_rgb)
        else:  # square
            radius = box_size * 0.4 if finder_frame_shape == "rounded" else 0
            if radius > 0:
                draw.rounded_rectangle(
                    [cx, cy, cx + cw, cy + cw], radius=radius, fill=fc_rgb)
            else:
                draw.rectangle([cx, cy, cx + cw, cy + cw], fill=fc_rgb)

    # 3. Incrustar Logo central si existe
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo_target_size = int(img_size * logo_ratio)

            # Redimensionar manteniendo aspecto
            logo.thumbnail((logo_target_size, logo_target_size),
                           Image.Resampling.LANCZOS)
            lw, lh = logo.size

            # Fondo protector blanco/color fondo alrededor del logo
            pad = int(box_size * 0.6)
            pos_x = (img_size - lw) // 2
            pos_y = (img_size - lh) // 2

            bg_box = Image.new(
                "RGBA", (lw + pad * 2, lh + pad * 2), back_rgb + (255,))
            draw_bg = ImageDraw.Draw(bg_box)
            draw_bg.rounded_rectangle(
                [0, 0, lw + pad * 2, lh + pad * 2], radius=box_size * 0.5, fill=back_rgb)

            img.paste(bg_box, (pos_x - pad, pos_y - pad), bg_box)
            img.paste(logo, (pos_x, pos_y), logo)
        except Exception as e:
            print(f"Error al cargar/incrustar el logo: {e}")

    return img


def copy_image_to_clipboard(pil_img: Image.Image) -> bool:
    """Copia la imagen PIL directamente al portapapeles de Windows / MacOS"""
    try:
        if sys.platform == "darwin":
            # MacOS usando pngpaste / AppleScript pbcopy
            output = BytesIO()
            pil_img.save(output, format="PNG")
            data = output.getvalue()
            process = subprocess.Popen(
                ["pbcopy", "-Device", "clipboard"], stdin=subprocess.PIPE)
            process.communicate(data)
            return True
        elif sys.platform == "win32":
            # Windows usando Win32 API o PowerShell
            output = BytesIO()
            pil_img.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]  # Remover encabezado BMP
            import win32clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
            return True
    except Exception as e:
        print(f"No se pudo copiar al portapapeles: {e}")
        # Intentar fallback alternativo en caso de no tener pywin32 instalada
        try:
            temp_path = os.path.join(
                os.path.expanduser("~"), ".temp_qr_clip.png")
            pil_img.save(temp_path)
            if sys.platform == "darwin":
                os.system(
                    f"osascript -e 'set the clipboard to (read (POSIX file \"{temp_path}\") as «class PNGf»)'")
                return True
        except Exception:
            pass
    return False


def save_qr_as_svg(data: str, save_path: str, back_color: tuple, module_color: tuple) -> bool:
    """Exporta el código QR en formato vectorial SVG verdadero"""
    try:
        import qrcode.image.svg
        factory = qrcode.image.svg.SvgPathImage
        qr = qrcode.QRCode(image_factory=factory,
                           error_correction=ERROR_CORRECT_H)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color=module_color, back_color=back_color)
        img.save(save_path)
        return True
    except Exception as e:
        print(f"Error guardando SVG: {e}")
        return False
