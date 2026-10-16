import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def load_hald_clut(hald_path: str, level: int = 8) -> ImageFilter.Color3DLUT:
    """
    Carrega o ficheiro HaldCLUT (aceita JPG e PNG).
    Ajusta a dimensão e suaviza os artefatos de compressão do JPG.
    """
    hald_img = Image.open(hald_path).convert("RGB")

    if hald_img.size != (512, 512):
        hald_img = hald_img.resize((512, 512), Image.Resampling.LANCZOS)

    if hald_path.lower().endswith(('.jpg', '.jpeg')):
        hald_img = hald_img.filter(ImageFilter.BoxBlur(0.5))

    table_size = level * level
    arr = np.array(hald_img, dtype=np.float32) / 255.0

    grid = arr.reshape(level, table_size, level, table_size, 3)
    lut_array = grid.transpose(0, 2, 1, 3, 4).reshape(table_size, table_size, table_size, 3)

    return ImageFilter.Color3DLUT(table_size, lut_array.reshape(-1, 3))

def apply_preset_lut(photo: Image.Image, hald_path: str) -> Image.Image:
    """Aplica o tratamento de cor do Lightroom à fotografia antes da montagem."""
    lut_filter = load_hald_clut(hald_path)
    return photo.filter(lut_filter)

def apply_top_gradient(canvas, height_percentage: float = 0.65, max_opacity: int = 240):
    """Cria o gradiente escuro no topo para destacar a tipografia."""
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