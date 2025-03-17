import qrcode

from PIL import Image
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask

import os


def makeQRDinamico(data: str, logoURL:str, back_color:tuple, edge_color:tuple, center_color:tuple):
    """Genera un QR dinámico con un logo en el centro y un color de fondo y borde"""

    color_back = back_color
    color_edge = edge_color
    color_center = center_color

    print(edge_color)
    print(center_color)
    print(back_color)


    # Obtenemos el logo que ira en el centro del QR
    # ogoURL = os.path.join(os.getcwd(), 'media', 'InfoBanner.jpg')
    # logoPath = os.path.relpath(logoURL)
    logo = Image.open(logoURL)
    print(logoURL)
    # Le damos el tamaño a logo del centro
    baseWidth = 200
    wpercent = (baseWidth/float(logo.size[0]))
    hsize = int((float(logo.size[1]) * float(wpercent)))

    # Redimenciona el logo con base el tamaño estipulado
    logo = logo.resize((baseWidth, hsize), Image.Resampling.LANCZOS)

    # genera la  version del QR, tamaño y la correccion de errores
    QRcode = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=18,
        border=1
    )

    # se añade la información que contendra el QR
    QRcode.add_data(data)

    QRcode.make()

    # Se genera el formato del QR, así como los colores
    QRImg = QRcode.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer(
    ),  color_mask=RadialGradiantColorMask(back_color=color_back, edge_color=color_edge, center_color=color_center))

    # Pega la imagen del logo en el centro del QR
    QRImg.paste(logo, ((QRImg.size[0] - logo.size[0]) //
                2, (QRImg.size[1] - logo.size[1])//2))

    # Guarda el QR en la carpeta Exported en el escritorio, dependiendo del sistema operativo
    if os.name != 'nt':
        save = os.path.join(os.path.join(
            os.path.expanduser('~')), 'Desktop', 'exported')
    else:
        save = os.path.join(os.path.join(
            os.environ['USERPROFILE']), 'Desktop', 'exported')

    os.makedirs(save, exist_ok=True)

    QRImg.save(os.path.join(save, 'qrv4.png'))
    print("QR generado con éxito, en la direccion:", save)



if __name__ == "__main__":
    makeQRDinamico()
