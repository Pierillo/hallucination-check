import os
import json
import asyncio
import datetime
import shutil
from config import logger, DATA_DIR, PROJECT_ROOT
from agents.curator import run_curator
from agents.writer import run_writer
from agents.renderer import run_renderer
from agents.podcast import run_podcast
from utils.notion import save_to_notion
from utils.email_sender import send_email
from utils.dedup import save_history

# ---------------------------------------------------------
# UTILIDADES DE CHECKPOINT
# ---------------------------------------------------------
def get_checkpoint_path(name):
    return os.path.join(DATA_DIR, f"{name}.json")

def save_checkpoint(name, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(get_checkpoint_path(name), "w") as f:
        json.dump(data, f)

def load_checkpoint(name):
    path = get_checkpoint_path(name)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None

def clear_checkpoints():
    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)
        os.makedirs(DATA_DIR, exist_ok=True)

# ---------------------------------------------------------
# ORQUESTADOR PRINCIPAL
# ---------------------------------------------------------
async def main():
    logger.info("🚀 Iniciando motor agéntico Hallucination Check (Modular)...")
    
    try:
        # 1. Curación (Agente Curator)
        curated_news = load_checkpoint("curator")
        if not curated_news:
            curated_news = run_curator()
            save_checkpoint("curator", curated_news)
        else:
            logger.info("⏭️ Cargando noticias desde checkpoint (Curator).")

        # 2. Redacción (Agente Writer)
        editorial = load_checkpoint("writer")
        if not editorial:
            editorial = run_writer(curated_news)
            save_checkpoint("writer", editorial)
        else:
            logger.info("⏭️ Cargando editorial desde checkpoint (Writer).")

        # 3. Diseño HTML (Agente Renderer)
        html_output = run_renderer(editorial, curated_news)
        
        # 4. Generación Podcast (Agente Podcast)
        audio_file = await run_podcast(curated_news)
        
        # 5. Registro Notion (Utilidad Notion)
        # No bloqueante para el flujo principal
        try:
            save_to_notion(f"Edición {datetime.date.today()}", editorial["so_what"])
        except Exception:
            pass
        
        # 6. Envío Email (Utilidad Email)
        send_email(html_output, audio_file)
        
        # 7. Persistencia de Memoria e Historial
        new_urls = [n['url'] for n in curated_news]
        save_history(new_urls)
        
        # Limpiar podcast y checkpoints tras éxito total
        if audio_file and os.path.exists(audio_file):
            os.remove(audio_file)
        clear_checkpoints()
        
        logger.info("✨ Proceso completado exitosamente.")
        
    except Exception as e:
        logger.critical(f"💥 Error fatal en el flujo: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
