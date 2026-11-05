"""Generación de códigos QR del enlace corto.

El QR codifica exclusivamente la URL corta emitida por UniShort QR; nunca la
URL de destino ni datos personales.
"""

import io
from typing import Optional

import qrcode
from qrcode.constants import ERROR_CORRECT_M

from .config import Settings, get_settings


def generate_qr_png(content: str, settings: Optional[Settings] = None) -> bytes:
    """Genera una imagen PNG con el contenido indicado.

    Parameters
    ----------
    content:
        Texto a codificar; en el servicio siempre es la URL corta.
    settings:
        Configuración de tamaño y zona de silencio del QR.

    Returns
    -------
    bytes
        Contenido binario de una imagen PNG.

    Raises
    ------
    ValueError
        Si el contenido está vacío.
    """

    if not content or not content.strip():
        raise ValueError("El contenido del QR no puede estar vacío")

    config = settings or get_settings()
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_M,
        box_size=config.qr_box_size,
        border=config.qr_border,
    )
    qr.add_data(content)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
