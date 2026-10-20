import requests
from typing import List, Dict, Any

class StravaClient:
    """
    Cliente HTTP dedicado para comunicação com a API do Strava.
    Encapsula as regras de autenticação OAuth2 e as chamadas de endpoints,
    isolando a lógica de rede da camada de roteamento da nossa API.
    """

    AUTH_URL = "https://www.strava.com/oauth/mobile/authorize"
    TOKEN_URL = "https://www.strava.com/oauth/token"
    API_BASE_URL = "https://www.strava.com/api/v3"

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_authorization_url(self) -> str:
        return (
            f"{self.AUTH_URL}"
            f"?client_id={self.client_id}"
            f"&response_type=code"
            f"&redirect_uri={self.redirect_uri}"
            f"&scope=read,activity:read_all"
            f"&approval_prompt=force"
        )

    def exchange_code_for_token(self, code: str) -> str:
        """Troca o código de autorização temporário por um token de acesso de curto prazo."""
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code"
        }

        response = requests.post(self.TOKEN_URL, data=payload, timeout=10)

        if response.status_code != 200:
            raise ValueError(f"Falha na autenticação do Strava. Detalhes: {response.text}")

        data = response.json()
        return data.get("access_token")

    def fetch_recent_activities(self, token: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Busca o histórico recente e normaliza as métricas (distância para km,
        velocidade para km/h, tempo para H:MM:SS) para consumo imediato do frontend.
        """
        headers = {"Authorization": f"Bearer {token}"}
        endpoint = f"{self.API_BASE_URL}/athlete/activities?per_page={limit}"

        response = requests.get(endpoint, headers=headers, timeout=15)
        if response.status_code != 200:
            raise PermissionError("Token do Strava inválido ou expirado.")

        raw_activities = response.json()
        return [self._normalize_activity(act) for act in raw_activities]

    def _normalize_activity(self, act: Dict[str, Any]) -> Dict[str, Any]:
        distancia_km = act.get("distance", 0) / 1000

        tempo_seg = act.get("moving_time", 0)
        horas = tempo_seg // 3600
        minutos = (tempo_seg % 3600) // 60
        segundos = tempo_seg % 60

        velocidade_kmh = act.get("average_speed", 0) * 3.6

        return {
            "id": act.get("id"),
            "nome": act.get("name"),
            "data": act.get("start_date_local", "")[:10],
            "distancia": round(distancia_km, 2),
            "tempo": f"{horas}:{minutos:02d}:{segundos:02d}",
            "elevacao": int(act.get("total_elevation_gain", 0)),
            "velocidade": round(velocidade_kmh, 1),
            "polyline": act.get("map", {}).get("summary_polyline", "")
        }