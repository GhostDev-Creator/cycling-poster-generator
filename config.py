import json
import os
from typing import Any, Dict, Tuple

DEFAULT_CONFIG: Dict[str, Any] = {
    "paleta": {
        "texto_principal": [255, 255, 255, 255],
        "texto_secundario": [228, 234, 240, 200],
        "destaque": [252, 82, 0, 255],
        "gradiente_base": [5, 5, 5, 0]
    },
    "layout": {
        "gradiente_altura": 0.65,
        "gradiente_opacidade_max": 240
    },
    "preferencias": {
        "qualidade_exportacao": 95,
        "pasta_saida": "saida"
    }
}

def carregar_configuracoes(caminho: str = "config.json") -> Dict[str, Any]:
    """
    Carrega as configurações de interface e layout do projeto.
    Garante resiliência retornando um fallback seguro caso o arquivo falte ou esteja corrompido.
    """
    if not os.path.exists(caminho):
        try:
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
        except IOError:
            pass
        return DEFAULT_CONFIG

    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return DEFAULT_CONFIG

def tuplo_cor(cor_lista: list[int]) -> Tuple[int, int, int, int]:
    return tuple(cor_lista)