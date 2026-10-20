from typing import Union, BinaryIO
from PIL import Image, ImageOps

def prepare_background(image_source: Union[str, BinaryIO], target_width: int, target_height: int) -> Image.Image:
    """
    Processa a imagem de fundo enviada pelo usuário.
    Resolve a orientação EXIF (comum em uploads de dispositivos móveis) e 
    realiza o crop centralizado para evitar distorção nas dimensões do poster.
    """
    img = Image.open(image_source)
    img = ImageOps.exif_transpose(img)

    return ImageOps.fit(
        img,
        (target_width, target_height),
        method=Image.Resampling.LANCZOS
    )