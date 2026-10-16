import json
import os

CONFIG_PADRAO = {
    "paleta": {
        "texto_principal": [255, 255, 255, 255],
        "texto_secundario": [228, 234, 240, 200],
        "destaque": [252, 82, 0, 255],
        "gradiente_base": [10, 15, 20, 0]
    },
    "layout": {
        "gradiente_altura": 0.6,
        "gradiente_opacidade_max": 170
    },
    "preferencias": {
        "qualidade_exportacao": 95,
        "pasta_saida": "saida"
    }
}

def carregar_configuracoes(caminho: str = "config.json") -> dict:
    """Lê as configurações do ficheiro JSON. Cria um novo se não existir."""
    if not os.path.exists(caminho):
        print(f"Aviso: '{caminho}' não encontrado. A criar ficheiro com definições predefinidas...")
        try:
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(CONFIG_PADRAO, f, indent=4)
        except Exception as e:
            print(f"Erro ao criar {caminho}: {e}. A usar definições em memória.")
        return CONFIG_PADRAO

    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config
    except json.JSONDecodeError:
        print(f"Erro: O ficheiro '{caminho}' está corrompido ou mal formatado. A usar definições predefinidas.")
        return CONFIG_PADRAO
    except Exception as e:
        print(f"Erro inesperado ao ler configurações: {e}")
        return CONFIG_PADRAO

def tuplo_cor(cor_lista: list) -> tuple:
    """Converte uma lista do JSON [R, G, B, A] para um tuplo que o Pillow entende."""
    return tuple(cor_lista)