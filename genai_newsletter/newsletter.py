import os
import datetime
import smtplib
import asyncio
import edge_tts
import requests
import logging
import time
import json
import re
import tempfile
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
from tavily import TavilyClient
import google.generativeai as genai
from notion_client import Client
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# ---------------------------------------------------------
# CONFIGURACIÓN DE LOGGING ESTRUCTURADO
# ---------------------------------------------------------
LOG_FILE = os.path.join(os.path.dirname(__file__), "newsletter.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# VALIDACIÓN DE VARIABLES DE ENTORNO
# ---------------------------------------------------------
load_dotenv()
REQUIRED_VARS = [
    "TAVILY_API_KEY", "GEMINI_API_KEY", "GMAIL_USER", 
    "GMAIL_PASSWORD", "EMAILS", "NOTION_TOKEN", "NOTION_DATABASE_ID"
]
missing_vars = [var for var in REQUIRED_VARS if not os.getenv(var)]
if missing_vars:
    logger.error(f"❌ Faltan las siguientes variables en el .env: {', '.join(missing_vars)}")
    exit(1)

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
EMAILS = [e.strip() for e in os.getenv("EMAILS").split(",")]
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Configuración de Clientes
tavily = TavilyClient(api_key=TAVILY_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)
notion = Client(auth=NOTION_TOKEN)

# ---------------------------------------------------------
# UTILS: Llamadas a LLM y Reintentos
# ---------------------------------------------------------
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((requests.exceptions.RequestException, Exception))
)
def call_llm(prompt, model_name="gemini-2.0-flash"):
    """Función centralizada para llamadas al LLM con reintentos."""
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return response.text

# ---------------------------------------------------------
# MEMORIA: Evitar duplicados (Escritura Atómica)
# ---------------------------------------------------------
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "processed_urls.json")

def load_history():
    """Carga el historial de URLs procesadas desde un archivo JSON local."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(new_urls):
    """Guarda nuevas URLs en el historial local de forma atómica."""
    try:
        history = load_history()
        history.extend(new_urls)
        history = list(set(history))[-500:]
        
        # Escritura atómica usando archivo temporal
        with tempfile.NamedTemporaryFile('w', delete=False, dir=os.path.dirname(HISTORY_FILE)) as tf:
            json.dump(history, tf)
            temp_name = tf.name
        os.replace(temp_name, HISTORY_FILE)
    except Exception as e:
        logger.error(f"❌ Error guardando historial: {e}")

# ---------------------------------------------------------
# AGENTE CURATOR: Búsqueda y Selección (Tavily + Gemini)
# ---------------------------------------------------------
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def get_og_image(url):
    """Extrae la imagen meta og:image de una URL de noticia."""
    try:
        response = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            og_image = soup.find("meta", property="og:image")
            if og_image:
                return og_image["content"]
    except Exception:
        pass
    return None

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_tavily(query):
    """Realiza búsquedas en Tavily con reintentos automáticos."""
    return tavily.search(query=query, search_depth="advanced", max_results=10, time_range="week")

def agent_curator():
    """
    Agente 1: Curador. 
    Busca noticias, filtra duplicados históricos y usa Gemini para seleccionar las 10 mejores.
    """
    logger.info("🕵️ Agente Curator activado: Lanzando búsquedas en 5 frentes...")
    history = load_history()
    
    queries = [
        "latest LLM releases benchmarks generative AI today",
        "generative AI in banking finance use cases 2024",
        "trending AI developer tools github frameworks this week",
        "impactful AI research papers summary arxiv",
        "top generative AI business strategy and ROI news"
    ]
    
    raw_results = []
    for q in queries:
        resp = fetch_tavily(q)
        results = resp.get("results", [])
        filtered = [r for r in results if r['url'] not in history]
        raw_results.extend(filtered)
    
    if not raw_results:
        logger.warning("⚠️ No se encontraron noticias nuevas. Usando fallback.")
        for q in queries:
            resp = fetch_tavily(q)
            raw_results.extend(resp.get("results", []))

    logger.info(f"📊 {len(raw_results)} noticias nuevas encontradas. Evaluando relevancia...")
    
    eval_text = "\n".join([f"ID: {idx} | Título: {r['title']} | URL: {r['url']}" for idx, r in enumerate(raw_results)])
    
    prompt = f"""
    Actúa como un Curador Senior de Noticias de IA para un equipo bancario.
    Evalúa estos {len(raw_results)} artículos y selecciona los 10 mejores.
    
    CRITERIO ELIMINATORIO: Toda la información DEBE tener máximo 3 semanas de antigüedad.
    EVITA REPETICIONES: Asegúrate de que las noticias cubran temas variados (modelos, banca, tech, research).
    
    Criterios de puntuación (Score 0-10):
    - Impacto real (no hype vacío).
    - Novedad (frescura extrema).
    - Aplicabilidad en estrategia bancaria o tech.
    
    Devuelve un JSON con el siguiente formato EXACTO:
    {{"selected": [
        {{"id": 0, "score": 9.5, "reason": "descripción breve del porqué"}},
        ... (total 10)
    ]}}
    
    Artículos:
    {eval_text}
    """
    
    response_text = call_llm(prompt)
    try:
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            selections = json.loads(json_str)["selected"]
        else:
            raise ValueError("No se encontró JSON en la respuesta")
    except Exception as e:
        logger.error(f"❌ Error al parsear selección del Curator: {e}")
        selections = [{"id": i, "score": 5.0, "reason": "fallback"} for i in range(min(10, len(raw_results)))]

    curated_news = []
    for sel in selections:
        idx = sel["id"]
        if idx < len(raw_results):
            article = raw_results[idx]
            article["score"] = sel["score"]
            article["image"] = get_og_image(article["url"])
            curated_news.append(article)
            logger.info(f"✅ Seleccionado [{article['score']}/10]: {article['title']}")
        
    return curated_news

# ---------------------------------------------------------
# AGENTE REDACTOR: Contenido Editorial
# ---------------------------------------------------------
def agent_redactor(curated_news):
    """
    Agente 2: Redactor.
    Genera el contenido editorial (titulares, resúmenes, So What).
    """
    logger.info("✍️ Agente Redactor activado: Generando contenido editorial...")
    
    context = ""
    for idx, n in enumerate(curated_news):
        context += f"News #{idx+1}\nTítulo: {n['title']}\nContent: {n['content']}\nURL: {n['url']}\n\n"
        
    prompt = f"""
    Eres el editor jefe de 'Hallucination Check'. Tu tono es relajado, amigable y directo.
    
    Recibes estas 10 noticias. Redacta las siguientes secciones para el newsletter:
    - Para cada noticia: Un titular ameno y un resumen de 3-4 líneas (usar emojis).
    - Sección 'So What': Una síntesis estratégica global de lo que esto implica para el negocio.
    - Sección 'Recomendación del Día': Inventa o resalta un recurso top basado en las noticias.

    REGLA DE ORO: No repitas ideas entre las noticias. Cada una debe aportar un ángulo distinto.

    Devuelve un JSON con el siguiente formato:
    {{
      "news": [
        {{"headline": "Titular con emoji", "summary": "Resumen ameno...", "url": "URL original"}},
        ...
      ],
      "so_what": "Resumen estratégico...",
      "recommendation": "Recomendación del día..."
    }}

    Contexto:
    {context}
    """
    
    response_text = call_llm(prompt)
    try:
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        else:
            raise ValueError("No se encontró JSON en la respuesta del Redactor")
    except Exception as e:
        logger.error(f"❌ Error crítico en Redactor: {e}")
        raise e

# ---------------------------------------------------------
# AGENTE HTML: Renderizado de Diseño
# ---------------------------------------------------------
def agent_html(editorial_content, curated_news):
    """
    Agente 3: Diseñador HTML.
    Convierte el contenido editorial en un documento HTML profesional.
    """
    logger.info("🎨 Agente HTML activado: Renderizando diseño final...")
    
    combined_content = ""
    for i, item in enumerate(editorial_content["news"]):
        img_html = f"<img src='{curated_news[i]['image']}' style='width:100%; border-radius:8px; margin-bottom:10px;'>" if curated_news[i].get("image") else ""
        combined_content += f"""
        <div class="card" style="background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; margin-bottom: 20px;">
            {img_html}
            <h3 style="color: #3b82f6; margin-top: 0;">{item['headline']}</h3>
            <p style="color: #334155; line-height: 1.5;">{item['summary']}</p>
            <a href="{item['url']}" style="color: #3b82f6; font-weight: bold; text-decoration: none;">Leer realidad →</a>
        </div>
        """

    prompt = f"""
    Eres un diseñador web experto en Email Marketing. Toma el contenido y construye un email HTML completo.
    
    DISEÑO:
    - Nombre: Hallucination Check
    - Bajada: "Tu dosis matutina de realidad para filtrar el hype de la IA antes del primer café."
    - Colores: Fondo gris muy claro (#f4f4f5), tarjetas blancas, azul corporativo (#3b82f6).
    
    ORDEN OBLIGATORIO:
    1. Header con logo/título.
    2. Podcast (Sección destacada indicando que hay audio adjunto).
    3. Bloque de 10 noticias.
    4. 🎯 SO WHAT: {editorial_content['so_what']}
    5. 🎧 RECOMENDACIÓN DEL DÍA: {editorial_content['recommendation']}
    
    Noticias:
    {combined_content}
    
    Responde solo con HTML puro y CSS inline.
    """
    
    return call_llm(prompt)

# ---------------------------------------------------------
# PODCAST: Generación de Audio Extendido
# ---------------------------------------------------------
async def generate_long_podcast(curated_news):
    """
    Genera un script de podcast y lo convierte a audio MP3.
    """
    logger.info("🎙️ Generando Podcast Extendido (~10 min)...")
    context = "\n".join([f"Noticia: {n['title']}. Detalle: {n['content']}" for n in curated_news])
    
    prompt = f"""
    Eres un experto en IA ameno. Escribe un monólogo de podcast de 1300 palabras en ESPAÑOL.
    Repasa las 10 noticias del día de forma conversacional. Explica por qué importan.
    Empieza: '¡Muy buenas! Soy tu resumen de Hallucination Check...'
    Contexto: {context}
    """
    
    script = call_llm(prompt)
    
    output_file = "hallucination_podcast.mp3"
    communicate = edge_tts.Communicate(script, "es-ES-AlvaroNeural")
    await communicate.save(output_file)
    logger.info(f"✅ Podcast generado exitosamente.")
    return output_file

# ---------------------------------------------------------
# NOTION: Registro Histórico
# ---------------------------------------------------------
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def save_to_notion(title, so_what):
    """Guarda un registro en Notion con reintentos."""
    try:
        logger.info("📓 Guardando registro en Notion...")
        notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties={
                "Título": {"title": [{"text": {"content": title}}]},
                "Fecha": {"date": {"start": datetime.date.today().isoformat()}},
                "So What": {"rich_text": [{"text": {"content": so_what[:2000]}}]}
            }
        )
        logger.info("✅ Registro en Notion completado.")
    except Exception as e:
        logger.warning(f"⚠️ No se pudo guardar en Notion: {e}")
        raise e

# ---------------------------------------------------------
# ENVÍO DE EMAIL
# ---------------------------------------------------------
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=5, max=20))
def send_email(html_body, audio_path):
    """Envía el email final con reintentos."""
    logger.info(f"📧 Enviando newsletter a {len(EMAILS)} destinatarios...")
    today = datetime.date.today().strftime("%d/%m/%Y")
    
    msg = MIMEMultipart()
    msg['From'] = f"Hallucination Check <{GMAIL_USER}>"
    msg['To'] = ", ".join(EMAILS)
    msg['Subject'] = f"Hallucination Check: Tu dosis diaria de GenAI - {today}"
    msg.attach(MIMEText(html_body, 'html'))

    if audio_path and os.path.exists(audio_path):
        with open(audio_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename=Podcast_HC.mp3")
            msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(GMAIL_USER, GMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()
    logger.info("🚀 Newsletter enviado con éxito.")

# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
async def main():
    """Orquestador principal."""
    start_time = time.time()
    logger.info("🚀 Iniciando motor de Hallucination Check...")
    
    try:
        # 1. Curación
        curated_news = agent_curator()
        
        # 2. Redacción
        editorial = agent_redactor(curated_news)
        
        # 3. Diseño HTML
        html_output = agent_html(editorial, curated_news)
        
        # 4. Generación Podcast
        audio_file = await generate_long_podcast(curated_news)
        
        # 5. Registro Notion (opcional en fallo)
        try:
            save_to_notion(f"Edición {datetime.date.today()}", editorial["so_what"])
        except Exception:
            pass
        
        # 6. Envío Email
        send_email(html_output, audio_file)
        
        # 7. Memoria
        new_urls = [n['url'] for n in curated_news]
        save_history(new_urls)
        
        if os.path.exists(audio_file):
            os.remove(audio_file)
            
        duration = time.time() - start_time
        logger.info(f"✨ Proceso completado en {duration:.2f} segundos.")
        
    except Exception as e:
        logger.critical(f"💥 Error fatal en el flujo: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
