import json
import os
import tempfile
from config import HISTORY_FILE, logger

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
        # Deduplicar y mantener los últimos 500 registros
        history = list(set(history))[-500:]
        
        # Escritura atómica usando archivo temporal
        with tempfile.NamedTemporaryFile('w', delete=False, dir=os.path.dirname(HISTORY_FILE)) as tf:
            json.dump(history, tf)
            temp_name = tf.name
        os.replace(temp_name, HISTORY_FILE)
    except Exception as e:
        logger.error(f"❌ Error guardando historial: {e}")
