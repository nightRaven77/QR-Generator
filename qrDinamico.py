import qrcode

from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import CircleModuleDrawer, GappedSquareModuleDrawer, HorizontalBarsDrawer, VerticalBarsDrawer, RoundedModuleDrawer, SquareModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask

import os

# Dictionary of available module drawers
module_drawers = {
    'circle': CircleModuleDrawer(),
    'square': GappedSquareModuleDrawer(),
    'horizontal': HorizontalBarsDrawer(),
    'vertical': VerticalBarsDrawer(),
    'rounded': RoundedModuleDrawer(),
    'default': SquareModuleDrawer()
}


def makeQRDinamico(data: str, logoURL: str, back_color: tuple, edge_color: tuple, center_color: tuple, selected_drawer: str):
    """Genera un QR dinámico con un logo en el centro y un color de fondo y borde"""

    # genera la  version del QR, tamaño y la correccion de errores
    QRcode = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )

    # se añade la información que contendra el QR
    QRcode.add_data(data)

    QRcode.make()

    # Se genera el formato del QR, así como los colores
    QRImg = QRcode.make_image(
        image_factory=StyledPilImage,
        module_drawer=module_drawers.get(
            selected_drawer, module_drawers['default']),
        color_mask=RadialGradiantColorMask(
            back_color=back_color,
            edge_color=edge_color,
            center_color=center_color,
        ),
        embeded_image_path=logoURL,
        embeded_image_ratio=0.2
    )
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
