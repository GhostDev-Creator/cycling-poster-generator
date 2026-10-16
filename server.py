import os
import uuid
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
from photo import prepare_background
from layout import PosterCanvas
from components import draw_header, draw_metrics, draw_footer
from effects import apply_top_gradient, apply_preset_lut
from route import draw_route
from config import carregar_configuracoes, tuplo_cor

app = FastAPI(title="Cycling Poster API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("saida", exist_ok=True)
os.makedirs("temp", exist_ok=True)
os.makedirs("assets/icons", exist_ok=True)
os.makedirs("assets/fonts", exist_ok=True)

@app.get("/")
async def pagina_inicial():
    return FileResponse("index.html")

@app.post("/gerar")
async def gerar_poster(
        foto_base: UploadFile = File(...),
        hald_file: UploadFile = File(None),
        gpx_file: UploadFile = File(None),
        start_loc: str = Form(...),
        end_loc: str = Form(...),
        cyclists: str = Form(...),
        mensagem_rodape: str = Form(...),
        distance: float = Form(...),
        time_str: str = Form(...),
        elevation: int = Form(...),
        speed: float = Form(...),
        format_choice: int = Form(...)
):
    temp_foto_path = os.path.join("temp", f"{uuid.uuid4()}_{foto_base.filename}")
    with open(temp_foto_path, "wb") as f:
        f.write(await foto_base.read())

    temp_hald_path = None
    if hald_file and hald_file.filename:
        temp_hald_path = os.path.join("temp", f"{uuid.uuid4()}_{hald_file.filename}")
        with open(temp_hald_path, "wb") as f:
            f.write(await hald_file.read())

    temp_gpx_path = None
    if gpx_file and gpx_file.filename:
        temp_gpx_path = os.path.join("temp", f"{uuid.uuid4()}_{gpx_file.filename}")
        with open(temp_gpx_path, "wb") as f:
            f.write(await gpx_file.read())

    try:
        cfg = carregar_configuracoes()

        fonts = {
            "bold": "assets/fonts/Montserrat-Bold.ttf",
            "light": "assets/fonts/Montserrat-Light.ttf",
            "medium": "assets/fonts/Montserrat-Medium.ttf",
            "regular": "assets/fonts/Montserrat-Regular.ttf",
            "footer": "assets/fonts/Allura-Regular.ttf"
        }

        if format_choice == 1:
            target_width, target_height = 1080, 1920
        elif format_choice == 2:
            target_width, target_height = 1080, 1350
        else:
            with Image.open(temp_foto_path) as temp_img:
                target_width, target_height = temp_img.size

        bg_image = prepare_background(temp_foto_path, target_width, target_height)

        if temp_hald_path:
            bg_image = apply_preset_lut(bg_image, temp_hald_path)

        canvas = PosterCanvas(target_width, target_height)
        canvas.set_background(bg_image)

        paleta_tuplos = {
            "texto_principal": tuplo_cor(cfg["paleta"]["texto_principal"]),
            "texto_secundario": tuplo_cor(cfg["paleta"]["texto_secundario"]),
            "destaque": tuplo_cor(cfg["paleta"]["destaque"])
        }

        grad_alt = cfg["layout"].get("gradiente_altura", 0.65)
        grad_opac = cfg["layout"].get("gradiente_opacidade_max", 240)

        apply_top_gradient(canvas, height_percentage=grad_alt, max_opacity=grad_opac)

        if temp_gpx_path:
            draw_route(canvas, temp_gpx_path, color=paleta_tuplos["destaque"])

        draw_header(canvas, start_loc, end_loc, cyclists, fonts, paleta_tuplos)
        draw_metrics(canvas, distance, time_str, elevation, speed, fonts, paleta_tuplos)
        draw_footer(canvas, mensagem_rodape, fonts["footer"], paleta_tuplos)

        output_filename = f"poster_{uuid.uuid4().hex[:8]}.jpg"
        output_path = os.path.join("saida", output_filename)

        canvas.export(output_path)

        os.remove(temp_foto_path)
        if temp_hald_path: os.remove(temp_hald_path)
        if temp_gpx_path: os.remove(temp_gpx_path)

        return FileResponse(output_path, media_type="image/jpeg", filename="poster_strava.jpg")

    except Exception as e:
        if os.path.exists(temp_foto_path): os.remove(temp_foto_path)
        if temp_hald_path and os.path.exists(temp_hald_path): os.remove(temp_hald_path)
        if temp_gpx_path and os.path.exists(temp_gpx_path): os.remove(temp_gpx_path)

        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
