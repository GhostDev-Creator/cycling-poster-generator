import os
from PIL import Image, ImageOps

def prepare_background(image_path: str, target_width: int, target_height: int) -> Image.Image:
    """
    Carrega a fotografia, corrige a orientação do EXIF e aplica um recorte 
    proporcional (crop) para preencher as dimensões desejadas sem distorcer.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Erro: A imagem '{image_path}' não foi encontrada.")

    img = Image.open(image_path)

    img = ImageOps.exif_transpose(img)

    img_cropped = ImageOps.fit(
        img, 
        (target_width, target_height), 
        method=Image.Resampling.LANCZOS
    )

    return img_cropped