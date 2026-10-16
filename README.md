<div align="center">

# 🚴 Cycling Poster Generator

### Uma aplicação web e API REST para transformar as métricas das suas pedaladas em arte épica.

**Registe a sua rota. Aplique os seus filtros. Partilhe a sua conquista.**

[![Python Requirements](https://img.shields.io/badge/Python->=3.10-339933?style=flat-square&logo=python&logoColor=white)](#o-que-o-sistema-processa)
[![FastAPI Backend](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square&logo=fastapi&logoColor=white)](#como-funciona)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-Frontend-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)](#quick-start)
[![MIT license](https://img.shields.io/badge/license-MIT-f4c430?style=flat-square)](LICENSE)
<div align="center">
  <a href="https://ghostdev-poster-generator-v2.onrender.com" target="_blank">
    <img src="https://img.shields.io/badge/🚀_Acessar_Web_Service-000000?style=for-the-badge&logo=vercel&logoColor=white" alt="Acessar Web Service">
  </a>
</div>

<br />

<img width="1536" height="1024" src="https://github.com/user-attachments/assets/d0a6bf12-6c1f-4bf5-b9a8-22585c5de3de" alt="Demonstração da Interface do Cycling Poster Generator"/>

<br /><br />

</div>

---

Fez uma pedalada épica e quer partilhar os dados no Instagram com qualidade profissional? O **Cycling Poster Generator** é uma aplicação web completa e independente que funde fotografias, dados geoespaciais (GPX) e telemetria, renderizando posters de alta qualidade diretamente no seu navegador. Tudo processado de forma local ou no seu servidor cloud gratuito.

## 🚀 Quick Start

### 1. Iniciar o Servidor (Localmente)

Com o Python 3.10+ instalado, faça o clone e inicie o ambiente:

```bash
git clone https://github.com/Ghost-Do-While/cycling-poster-generator.git
cd cycling-poster-generator

# Instalar dependências
pip install -r requirements.txt

# Iniciar a API
uvicorn server:app --reload
```

### 2. Aceder à Aplicação

Abra o seu navegador em `http://127.0.0.1:8000`. 
Preencha os dados da sua corrida, anexe a fotografia e clique em "Gerar Poster". A imagem final será processada e devolvida instantaneamente sem recarregar a página.

---

## ⚙️ Como Funciona

A arquitetura do sistema foi desenhada em duas camadas desacopladas: um **Frontend SPA (Single Page Application)** construído com HTML5 Vanilla e Tailwind CSS, e um **Backend REST API** suportado por FastAPI.

Quando pede um poster, o sistema executa o seguinte *pipeline*:

1. **Upload Assíncrono:** A imagem, o ficheiro GPX e o LUT de cor são enviados via `FormData` e guardados temporariamente usando UUIDs para evitar colisões.
2. **Processamento (Motor Python):** O `photo.py` corrige o EXIF e recorta a imagem proporcionalmente (algoritmo Lanczos). O `effects.py` aplica filtros 3D LUT (Lightroom) convertendo a matriz usando NumPy.
3. **Geometria Espacial:** O ficheiro `.gpx` é lido. As coordenadas geográficas reais são convertidas matematicamente em eixos X/Y proporcionais à tela da imagem.
4. **Devolução:** O servidor devolve os binários da imagem processada e apaga os ficheiros temporários em frações de segundo.

---

## 📊 O que o sistema processa

O motor de renderização suporta vários formatos de entrada e algoritmos. Abaixo estão os recursos baseados nas camadas de processamento:

| Alvo de Análise | O que o sistema devolve / faz | Motor / Tecnologia Utilizada |
| :--- | :--- | :--- |
| **Fotografias Base (JPG/PNG)** | Orientação EXIF corrigida e Crop (recorte) inteligente sem distorção. | Pillow (`ImageOps.exif_transpose`, `ImageOps.fit`), Algoritmo *Lanczos*. |
| **Ficheiros Geoespaciais (.gpx)** | Desenho matemático do trajeto da pedalada com escala dinâmica baseada em limites geográficos (Bounding Box). | *Python Standard Library* (`xml.etree.ElementTree`). |
| **Filtros de Cor (HaldCLUT)** | Aplicação de presets profissionais tipo Adobe Lightroom na foto original. | Pillow e Matrizes `NumPy` 3D (Cubo de conversão de cores). |
| **Dados de Telemetria** | Renderização de tipografia vetorial de alta definição com sombras de contraste e formatação inteligente. | Fontes TrueType (`.ttf`) geridas de forma dinâmica por `components.py`. |

---

## 🌟 Showcases & Formatos

O sistema suporta exportações precisas projetadas para as restrições algorítmicas das redes sociais:

* **Stories do Instagram (9:16):** Resolução nativa de 1080x1920.
* **Feed do Instagram (4:5):** Resolução nativa de 1080x1350, ideal para retratos.
* **Formato Original:** Preserva a proporção exata da fotografia da sua câmara.

---

## ❓ FAQ (Perguntas Frequentes)

<details>
<summary><strong>Preciso de conectar à API do Strava?</strong></summary>

Não. Para manter a simplicidade e contornar os limites técnicos e de autorização da API do Strava, os dados são inseridos manualmente pelo utilizador no frontend. O ficheiro GPX da rota pode ser exportado livremente de qualquer dispositivo GPS ou app.
</details>

<details>
<summary><strong>Porque usar HaldCLUTs em vez de filtros nativos?</strong></summary>

Os ficheiros HaldCLUT permitem-lhe criar um "preset" complexo no Lightroom (mexendo em curvas, saturação, sombras) e guardar essa matemática numa pequena imagem PNG. O motor do nosso sistema lê essa imagem e replica o efeito exato em segundos, sem necessidade do Lightroom no servidor.
</details>

<details>
<summary><strong>Os ficheiros que envio ficam guardados no servidor?</strong></summary>

Não. O sistema tem uma arquitetura *Stateless*. Os ficheiros são guardados num diretório temporário apenas durante os milissegundos do processamento. Assim que o poster é devolvido, o servidor executa a limpeza dos dados.
</details>

---

## 🤝 Como Contribuir

Adoraríamos ter a sua ajuda para evoluir o *Cycling Poster Generator*! Pode:
* Reportar bugs ou sugerir novas tipografias em *Issues*.
* Enviar um *Pull Request* para adicionar suporte direto ao Strava OAuth.
* Partilhar novos ficheiros HaldCLUT na pasta `assets`.

## 📜 Licença

[MIT](LICENSE)

Sinta-se livre para utilizar, clonar, alterar ou integrar este código noutros projetos comerciais ou recreativos.
