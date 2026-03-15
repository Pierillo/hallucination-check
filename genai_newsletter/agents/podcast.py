import os
import edge_tts
from config import call_llm, logger

async def run_podcast(curated_news, output_file="hallucination_podcast.mp3"):
    """Agente Podcast: Genera script y sintetiza audio MP3."""
    logger.info("🎙️ Generando Podcast Extendido (~10 min)...")
    context = "\n".join([f"Noticia: {n['title']}. Detalle: {n['content']}" for n in curated_news])
    
    prompt = f"""
    Eres un experto en IA ameno. Escribe un monólogo de podcast de 1300 palabras en ESPAÑOL.
    Repasa las 10 noticias del día de forma conversacional. Explica por qué importan.
    Empieza: '¡Muy buenas! Soy tu resumen de Hallucination Check...'
    Contexto: {context}
    """
    
    script = call_llm(prompt)
    
    # Sintetizar audio
    try:
        communicate = edge_tts.Communicate(script, "es-ES-AlvaroNeural")
        await communicate.save(output_file)
        logger.info(f"✅ Podcast generado exitosamente: {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"❌ Error al generar audio del podcast: {e}")
        return None
