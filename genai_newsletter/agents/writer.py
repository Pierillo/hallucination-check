import re
import json
from config import call_llm, logger

def run_writer(curated_news):
    """Agente Redactor: Genera el contenido editorial y secciones del newsletter."""
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
