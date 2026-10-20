import os
import uuid
import polyline
from io import BytesIO
from typing import Optional, Tuple
from photo import prepare_background
from layout import PosterCanvas
from components import draw_header, draw_metrics, draw_footer
from effects import apply_top_gradient, apply_preset_lut
from route import draw_route_from_points, draw_route
from config import carregar_configuracoes, tuplo_cor

class PosterGenerationError(Exception):
    pass

def determine_dimensions(format_choice: int, base_image_bytes: BytesIO) -> Tuple[int, int]:
    """Retorna largura e altura com base na proporção solicitada pelo usuário."""
    if format_choice == 1:
        return 1080, 1920
    elif format_choice == 2:
        return 1080, 1350

    from PIL import Image
    with Image.open(base_image_bytes) as img:
        return img.size

def generate_poster(
        foto_bytes: bytes,
        hald_bytes: Optional[bytes],
        preset_id: Optional[str],
        gpx_bytes: Optional[bytes],
        polyline_data: Optional[str],
        start_loc: str,
        end_loc: str,
        cyclists: str,
        mensagem_rodape: str,
        distance: float,
        time_str: str,
        elevation: int,
        speed: float,
        format_choice: int,
        output_dir: str = "saida"
) -> str:
    """
    Orquestra a montagem completa da imagem processando todos os dados em memória.
    Retorna o caminho físico do arquivo JPEG final gerado.
    """
    cfg = carregar_configuracoes()

    foto_io = BytesIO(foto_bytes)
    target_width, target_height = determine_dimensions(format_choice, foto_io)

    # É necessário reiniciar o ponteiro após verificar as dimensões
    foto_io.seek(0)
    bg_image = prepare_background(foto_io, target_width, target_height)

    # Aplicação de LUT
    if hald_bytes:
        bg_image = apply_preset_lut(bg_image, BytesIO(hald_bytes))
    elif preset_id and preset_id != "nenhum":
        preset_path = os.path.join("assets/presets", preset_id)
        if os.path.exists(preset_path):
            bg_image = apply_preset_lut(bg_image, preset_path)

    canvas = PosterCanvas(target_width, target_height)
    canvas.set_background(bg_image)

    paleta = {
        "texto_principal": tuplo_cor(cfg["paleta"]["texto_principal"]),
        "texto_secundario": tuplo_cor(cfg["paleta"]["texto_secundario"]),
        "destaque": tuplo_cor(cfg["paleta"]["destaque"])
    }

    apply_top_gradient(
        canvas,
        height_percentage=cfg["layout"].get("gradiente_altura", 0.65),
        max_opacity=cfg["layout"].get("gradiente_opacidade_max", 240)
    )

    # Renderização de Mapa (Strava Polyline tem prioridade sobre GPX)
    if polyline_data and polyline_data.strip():
        coordenadas = polyline.decode(polyline_data)
        draw_route_from_points(canvas, coordenadas, color=paleta["destaque"])
    elif gpx_bytes:
        draw_route(canvas, BytesIO(gpx_bytes), color=paleta["destaque"])

    fonts = {
        "bold": "assets/fonts/Montserrat-Bold.ttf",
        "medium": "assets/fonts/Montserrat-Medium.ttf",
        "regular": "assets/fonts/Montserrat-Regular.ttf",
        "footer": "assets/fonts/Allura-Regular.ttf"
    }

    draw_header(canvas, start_loc, end_loc, cyclists, fonts, paleta)
    draw_metrics(canvas, distance, time_str, elevation, speed, fonts, paleta)

    if mensagem_rodape and str(mensagem_rodape).strip() != "":
        draw_footer(canvas, mensagem_rodape, fonts["footer"], paleta)

    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"poster_{uuid.uuid4().hex[:8]}.jpg"
    output_path = os.path.join(output_dir, output_filename)

    canvas.export(output_path, format_type="JPEG", quality=cfg["preferencias"].get("qualidade_exportacao", 95))

    return output_path