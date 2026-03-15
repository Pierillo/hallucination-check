import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai
from tavily import TavilyClient
from notion_client import Client
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# ---------------------------------------------------------
# CONFIGURACIÓN DE LOGGING ESTRUCTURADO
# ---------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(PROJECT_ROOT, "newsletter.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("hallucination-check")

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
    # No salimos aquí para permitir que los módulos se importen, 
    # pero el orquestador fallará si intenta usarlas.

# Variables globales
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
EMAILS = [e.strip() for e in os.getenv("EMAILS", "").split(",") if e.strip()]
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# ---------------------------------------------------------
# CLIENTES GLOBALES
# ---------------------------------------------------------
tavily_client = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None
genai.configure(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
notion_client = Client(auth=NOTION_TOKEN) if NOTION_TOKEN else None

# ---------------------------------------------------------
# UTILS COMPARTIDOS
# ---------------------------------------------------------
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((requests.exceptions.RequestException, Exception))
)
def call_llm(prompt, model_name="gemini-2.0-flash"):
    """Llamada centralizada al LLM con reintentos."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY no configurada.")
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return response.text

# Rutas de datos
HISTORY_FILE = os.path.join(PROJECT_ROOT, "processed_urls.json")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
