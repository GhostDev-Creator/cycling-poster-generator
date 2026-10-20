from PIL import Image, ImageDraw

class PosterCanvas:
    """
    Gerencia a camada base e as composições visuais do poster.
    O motor ImageDraw é recriado automaticamente após cada alpha_composite
    para garantir que os novos desenhos afetem a camada mesclada atual.
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.image = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)

    def set_background(self, background_image: Image.Image) -> None:
        if background_image.size != (self.width, self.height):
            raise ValueError("As dimensões do background devem corresponder exatamente ao canvas.")

        bg_rgba = background_image.convert("RGBA")
        self.image = Image.alpha_composite(self.image, bg_rgba)
        self.draw = ImageDraw.Draw(self.image)

    def get_y(self, percentage: float) -> int:
        return int(self.height * percentage)

    def get_x(self, percentage: float) -> int:
        return int(self.width * percentage)

    def export(self, file_path: str, format_type: str = "JPEG", quality: int = 95) -> None:
        export_img = self.image

        if format_type.upper() in ["JPG", "JPEG"]:
            export_img = self.image.convert("RGB")
            export_img.save(file_path, format=format_type, quality=quality)
        else:
            export_img.save(file_path, format=format_type)