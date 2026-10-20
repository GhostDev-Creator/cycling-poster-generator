import os
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from strava_client import StravaClient
from poster_service import generate_poster

load_dotenv()

STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID", "")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET", "")
STRAVA_REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI", "http://127.0.0.1:8000/strava/callback")

strava_client = StravaClient(STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REDIRECT_URI)

# Inicialização de diretórios requeridos em tempo de boot
for folder in ["saida", "assets/icons", "assets/fonts", "assets/presets"]:
    os.makedirs(folder, exist_ok=True)

app = FastAPI(title="Cycling Poster API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def serve_index():
    return FileResponse("index.html")

@app.get("/strava/login")
async def login_strava():
    return RedirectResponse(strava_client.get_authorization_url())

@app.get("/strava/callback")
async def strava_callback(code: str):
    try:
        token = strava_client.exchange_code_for_token(code)
        return RedirectResponse(f"/?token={token}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/strava/activities")
async def get_activities(token: str):
    try:
        activities = strava_client.fetch_recent_activities(token)
        return JSONResponse(content={"activities": activities})
    except PermissionError as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/presets")
async def listar_presets():
    presets = []
    presets_dir = "assets/presets"
    if os.path.exists(presets_dir):
        for filename in os.listdir(presets_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                friendly_name = os.path.splitext(filename)[0].replace("_", " ").title()
                presets.append({"id": filename, "nome": friendly_name})
    return JSONResponse(content={"presets": presets})

@app.post("/gerar")
async def endpoint_gerar_poster(
        foto_base: UploadFile = File(...),
        hald_file: UploadFile = File(None),
        preset_id: str = Form(None),
        gpx_file: UploadFile = File(None),
        polyline_data: str = Form(None),
        start_loc: str = Form(...),
        end_loc: str = Form(...),
        cyclists: str = Form(...),
        mensagem_rodape: str = Form(""),
        distance: float = Form(...),
        time_str: str = Form(...),
        elevation: int = Form(...),
        speed: float = Form(...),
        format_choice: int = Form(...)
):
    try:
        foto_bytes = await foto_base.read()
        hald_bytes = await hald_file.read() if hald_file and hald_file.filename else None
        gpx_bytes = await gpx_file.read() if gpx_file and gpx_file.filename else None

        output_path = generate_poster(
            foto_bytes=foto_bytes,
            hald_bytes=hald_bytes,
            preset_id=preset_id,
            gpx_bytes=gpx_bytes,
            polyline_data=polyline_data,
            start_loc=start_loc,
            end_loc=end_loc,
            cyclists=cyclists,
            mensagem_rodape=mensagem_rodape,
            distance=distance,
            time_str=time_str,
            elevation=elevation,
            speed=speed,
            format_choice=format_choice
        )

        return FileResponse(output_path, media_type="image/jpeg", filename="poster_strava.jpg")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao gerar poster: {str(e)}")