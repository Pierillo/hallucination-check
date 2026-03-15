import re
import json
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
from config import tavily_client, call_llm, logger
from utils.dedup import load_history

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
    if not tavily_client:
        return {"results": []}
    return tavily_client.search(query=query, search_depth="advanced", max_results=10, time_range="week")

def run_curator():
    """Agente Curador: Busca y selecciona las 10 mejores noticias."""
    logger.info("🕵️ Agente Curator activado: Lanzando búsquedas...")
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

    logger.info(f"📊 {len(raw_results)} noticias encontradas. Evaluando relevancia...")
    
    eval_text = "\n".join([f"ID: {idx} | Título: {r['title']} | URL: {r['url']}" for idx, r in enumerate(raw_results)])
    
    prompt = f"""
    Actúa como un Curador Senior de Noticias de IA para un equipo bancario.
    Evalúa estos {len(raw_results)} artículos y selecciona los 10 mejores.
    
    CRITERIO ELIMINATORIO: Toda la información DEBE tener máximo 3 semanas de antigüedad.
    EVITA REPETICIONES: Asegúrate de que las noticias cubran temas variados (modelos, banca, tech, research).
    
    Devuelve un JSON con el siguiente formato EXACTO:
    {{"selected": [
        {{"id": 0, "score": 9.5, "reason": "descripción breve"}},
        ... (total 10)
    ]}}
    
    Artículos:
    {eval_text}
    """
    
    response_text = call_llm(prompt)
    try:
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if json_match:
            selections = json.loads(json_match.group(0))["selected"]
        else:
            raise ValueError("No se encontró JSON")
    except Exception as e:
        logger.error(f"❌ Error al parsear selección: {e}")
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
