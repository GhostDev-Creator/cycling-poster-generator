import numpy as np
from typing import Union, BinaryIO
from PIL import Image, ImageDraw, ImageFilter

def load_hald_clut(hald_source: Union[str, BinaryIO], level: int = 8) -> ImageFilter.Color3DLUT:
    """
    Converte uma imagem HaldCLUT 2D padrão em um mapeamento de cor 3D (Color3DLUT).
    Aplica Gaussian/BoxBlur em JPEGs para mitigar artefatos de compressão que
    causariam distorções de cor direcional indesejadas na imagem final.
    """
    hald_img = Image.open(hald_source).convert("RGB")

    if hald_img.size != (512, 512):
        hald_img = hald_img.resize((512, 512), Image.Resampling.LANCZOS)

    # Verifica se a origem foi lida via string (caminho em disco) ou arquivo em memória e checa a extensão
    is_jpeg = False
    if isinstance(hald_source, str) and hald_source.lower().endswith(('.jpg', '.jpeg')):
        is_jpeg = True
    elif hasattr(hald_source, 'name') and hald_source.name.lower().endswith(('.jpg', '.jpeg')):
        is_jpeg = True

    if is_jpeg:
        hald_img = hald_img.filter(ImageFilter.BoxBlur(0.5))

    table_size = level * level
    arr = np.array(hald_img, dtype=np.float32) / 255.0

    grid = arr.reshape(level, table_size, level, table_size, 3)
    lut_array = grid.transpose(0, 2, 1, 3, 4).reshape(table_size, table_size, table_size, 3)

    return ImageFilter.Color3DLUT(table_size, lut_array.reshape(-1, 3))


def apply_preset_lut(photo: Image.Image, hald_source: Union[str, BinaryIO]) -> Image.Image:
    lut_filter = load_hald_clut(hald_source)
    return photo.filter(lut_filter)


def apply_top_gradient(canvas, height_percentage: float = 0.65, max_opacity: int = 240) -> None:
    """
    Renderiza um overlay de gradiente direcional (topo -> baixo) via Numpy,
    otimizando a performance visual sem comprometer a legibilidade dos textos claros.
    """
    width = canvas.width
    grad_height = int(canvas.height * height_percentage)

    alpha_1d = np.linspace(max_opacity, 0, grad_height, dtype=np.uint8)
    alpha_2d = np.tile(alpha_1d.reshape(-1, 1), (1, width))

    gradient_layer = Image.new("RGBA", (width, grad_height), (5, 5, 5, 0))
    alpha_channel = Image.fromarray(alpha_2d, mode="L")
    gradient_layer.putalpha(alpha_channel)

    overlay = Image.new("RGBA", (canvas.width, canvas.height), (0, 0, 0, 0))
    overlay.paste(gradient_layer, (0, 0))

    canvas.image = Image.alpha_composite(canvas.image, overlay)
    canvas.draw = ImageDraw.Draw(canvas.image)