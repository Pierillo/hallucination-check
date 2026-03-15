import datetime
from tenacity import retry, stop_after_attempt, wait_exponential
from config import notion_client, NOTION_DATABASE_ID, logger

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def save_to_notion(title, so_what):
    """Guarda un registro de la edición en una base de datos de Notion."""
    if not notion_client or not NOTION_DATABASE_ID:
        logger.warning("⚠️ Notion no configurado. Saltando registro.")
        return

    try:
        logger.info("📓 Guardando registro en Notion...")
        notion_client.pages.create(
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
