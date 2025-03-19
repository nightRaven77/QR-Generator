import qrcode

from qrcode.image.styledpil import StyledPilImage

from qrcode.image.styles.moduledrawers.pil import *
from qrcode.image.styles.colormasks import RadialGradiantColorMask

import os

QRcode = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=18,
        border=1
    )

    # se añade la información que contendra el QR
QRcode.add_data("https://www.youtube.com/watch?v=IHNzOHi8sJs&list=RDphuiiNCxRMg&index=16")

QRcode.make()

QRImg = QRcode.make_image(image_factory=StyledPilImage, mmodule_drawer=RoundedModuleDrawer(),
        color_mask=RadialGradiantColorMask(
            back_color=(255, 255, 255), edge_color=(101, 101, 101), center_color=(98, 19, 51)),
embeded_image_path="./assets/logo.png", embeded_image_ratio=0.2) 


if os.name != 'nt':
	save = os.path.join(os.path.join(
		os.path.expanduser('~')), 'Desktop', 'exported')
else:
	save = os.path.join(os.path.join(
		os.environ['USERPROFILE']), 'Desktop', 'exported')

os.makedirs(save, exist_ok=True)

QRImg.save(os.path.join(save, 'qrv4.png'))
print("QR generado con éxito, en la direccion:", save)