from PIL import Image, ImageDraw

class PosterCanvas:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.image = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)

    def set_background(self, background_image: Image.Image):
        if background_image.size != (self.width, self.height):
             raise ValueError("As dimensões do fundo não correspondem ao Canvas.")
        bg_rgba = background_image.convert("RGBA")
        self.image = Image.alpha_composite(self.image, bg_rgba)
        self.draw = ImageDraw.Draw(self.image)

    def get_y(self, percentage: float) -> int:
        return int(self.height * percentage)

    def get_x(self, percentage: float) -> int:
        return int(self.width * percentage)

    def export(self, file_path: str, format="JPEG", quality=95):
        export_img = self.image
        if format.upper() in ["JPG", "JPEG"]:
            export_img = self.image.convert("RGB")
            export_img.save(file_path, format=format, quality=quality)
        else:
            export_img.save(file_path, format=format)