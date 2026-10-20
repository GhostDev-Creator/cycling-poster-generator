<div align="center">

# 🚴 Cycling Poster Generator v2.0

### Uma aplicação web e API REST para transformar as métricas das suas pedaladas em arte épica.

**Registre sua rota. Aplique seus filtros. Compartilhe sua conquista.**

[![Python Requirements](https://img.shields.io/badge/Python->=3.10-339933?style=flat-square&logo=python&logoColor=white)](#especificações-técnicas)
[![FastAPI Backend](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square&logo=fastapi&logoColor=white)](#como-funciona-pipeline-v2)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-Frontend-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)](#-quick-start)
[![Clean Architecture](https://img.shields.io/badge/Architecture-Clean_Code-8A2BE2?style=flat-square)](#-novidades-da-versão-20)
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

Fez uma pedalada épica e quer compartilhar os dados no Instagram com qualidade profissional? O **Cycling Poster Generator** é uma aplicação web completa e independente que funde fotografias, dados geoespaciais (Strava Polyline ou GPX) e telemetria, renderizando pôsteres de alta qualidade diretamente no seu navegador. 

A versão 2.0 foi totalmente reescrita sob os princípios de **Clean Architecture**, processamento **100% In-Memory** e **Integração OAuth2 com o Strava**.

## ✨ Novidades da Versão 2.0

*   **Integração Nativa com o Strava (OAuth2):** Conecte sua conta com um clique. O sistema importa automaticamente sua quilometragem, tempo, elevação e o mapa da rota (`summary_polyline`) sem a necessidade de arquivos manuais.
*   **Processamento 100% em Memória (Zero I/O):** Arquivos temporários no disco são coisas do passado. As imagens, matrizes LUT e mapas são processados na RAM utilizando `io.BytesIO`, reduzindo drasticamente a latência e protegendo o armazenamento do servidor.
*   **Tutorial Inteligente e Adaptativo:** A interface frontend detecta dinamicamente o método escolhido (Strava ou Upload Manual) e guia o usuário apenas pelos passos necessários, ocultando as complexidades.
*   **Detecção Dinâmica de Dispositivo:** O sistema reconhece se você está acessando via *Mobile* ou *Desktop* e adapta o botão de exportação de forma contextual ("Baixar no Celular" vs "Baixar no Computador").
*   **Arquitetura Desacoplada:** O código foi separado em domínios específicos (`strava_client.py`, `poster_service.py`, motor de imagem e rotas FastAPI), garantindo escalabilidade total.

---

## 🚀 Quick Start

### 1. Clonar e Configurar

Com o Python 3.10+ instalado, faça o clone do repositório e prepare o ambiente:

```bash
git clone https://github.com/Ghost-Do-While/cycling-poster-generator.git
cd cycling-poster-generator

# Instalar dependências
pip install fastapi uvicorn requests polyline pillow python-dotenv
```

### 2. Variáveis de Ambiente (.env)

Crie um arquivo `.env` na raiz do projeto e insira suas credenciais da API do Strava (necessárias para o login automático):

```env
STRAVA_CLIENT_ID=seu_client_id_aqui
STRAVA_CLIENT_SECRET=seu_client_secret_aqui
STRAVA_REDIRECT_URI=http://127.0.0.1:8000/strava/callback
```

### 3. Iniciar o Servidor

O sistema gera automaticamente as pastas de *assets* na primeira inicialização.

```bash
uvicorn server:app --reload
```

Abra o seu navegador em `http://127.0.0.1:8000`. A mágica acontece instantaneamente sem recarregar a página.

---

## ⚙️ Como Funciona (Pipeline V2)

A arquitetura do sistema foi desenhada em camadas estritamente isoladas:

1. **Camada de Rede (`strava_client.py` & `server.py`):** Gerencia a conexão OAuth2, converte os *Authorization Codes* em Tokens, normaliza as respostas JSON e fornece os *endpoints* REST estáticos e dinâmicos.
2. **Orquestração (`poster_service.py`):** Recebe o fluxo de bytes de imagens e parâmetros via HTTP e atua como o maestro do sistema, passando os dados entre as várias ferramentas matemáticas e visuais.
3. **Motor Gráfico e Geométrico (`photo.py`, `effects.py`, `route.py`):**
   * Corrige a orientação EXIF e executa o *Crop Lanczos*.
   * Transforma as polilinhas do Strava ou dados XML de um arquivo `.gpx` em arrays geográficos, transpondo as latitudes/longitudes perfeitamente escaladas para a Bounding Box de pixels do canvas.
   * Converte matrizes bidimensionais PNG (HaldCLUT) em Filtros LUT 3D matemáticos (`NumPy`) para coloração profissional.
4. **Exportação:** O arquivo `JPEG` final é renderizado e devolvido em uma única resposta assíncrona para o usuário.

---

## 📊 Especificações Técnicas

| Módulo | Responsabilidade Core | Stack / Motor Utilizado |
| :--- | :--- | :--- |
| **Integração Strava** | Autenticação OAuth2 e conversão em tempo real de `summary_polyline`. | `requests`, `polyline` |
| **Fotografias Base** | Orientação EXIF corrigida e Crop inteligente. Processamento *In-Memory*. | `Pillow`, `io.BytesIO` |
| **Geometria Espacial** | Desenho matemático do trajeto da pedalada com escala dinâmica baseada em limites geográficos. | Python *Standard Library* (`xml.etree.ElementTree`) |
| **Filtros de Cor (LUT)** | Modificação colorimétrica profunda na matriz RGB. | `Pillow` (Color3DLUT), `NumPy` |
| **Tipografia & UI** | Renderização vetorial com sombras dinâmicas e blocos de desfoque suave (Blur Box) orgânicos. | Fontes TrueType (`.ttf`), Filtros Gaussianos |

---

## 🌟 Showcases & Formatos

O sistema foi desenhado levando em conta os algoritmos de compressão e recorte do Meta/Instagram:

- **Stories do Instagram (9:16):** Resolução nativa de 1080x1920 pixels.
- **Feed do Instagram (4:5):** Resolução nativa de 1080x1350 pixels, ideal para maior retenção e área de tela.
- **Formato Original:** Preserva a proporção exata da fotografia original enviada pelo usuário.

---

## ❓ FAQ (Perguntas Frequentes)

<details>
<summary><strong>Sou obrigado a conectar a minha conta do Strava?</strong></summary>

Não! Embora a V2.0 traga uma integração perfeita com o Strava, o sistema continua a suportar rotas 100% manuais de forma independente. Basta ignorar o botão de Login, enviar o seu arquivo GPX e digitar os números livremente.
</details>

<details>
<summary><strong>Por que usar arquivos HaldCLUT em vez de filtros nativos?</strong></summary>

Os arquivos HaldCLUT permitem que você crie uma edição complexa no Lightroom (mexendo em dezenas de eixos, curvas e saturações) e exporte essa "matemática" em uma grade PNG (ex: 512x512). O servidor lê esse PNG com o `NumPy` e replica o efeito exato em uma fração de segundo na sua fotografia.
</details>

<details>
<summary><strong>O que acontece com a minha imagem ou token depois que a arte é gerada?</strong></summary>

Nada fica retido no servidor. A arquitetura atual é 100% focada na memória RAM (Stateless). As fotografias originais nunca chegam a tocar no disco rígido do servidor e desaparecem no momento em que a conexão HTTP termina. Não salvamos sessões ou senhas de usuários.
</details>

---

## 📜 Licença

[MIT](LICENSE)

Desenvolvido para amantes de ciclismo, código limpo e design profissional. Sinta-se livre para utilizar, clonar, alterar ou integrar este código em outros projetos comerciais ou recreativos.
