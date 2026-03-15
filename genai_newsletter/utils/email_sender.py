import os
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from tenacity import retry, stop_after_attempt, wait_exponential
from config import GMAIL_USER, GMAIL_PASSWORD, EMAILS, logger

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=5, max=20))
def send_email(html_body, audio_path=None):
    """Envía el email final con el newsletter HTML y el podcast MP3 adjunto."""
    if not GMAIL_USER or not GMAIL_PASSWORD:
        logger.error("❌ Credenciales de Gmail no configuradas. Abortando envío.")
        return

    logger.info(f"📧 Enviando newsletter a {len(EMAILS)} destinatarios...")
    today = datetime.date.today().strftime("%d/%m/%Y")
    
    msg = MIMEMultipart()
    msg['From'] = f"Hallucination Check <{GMAIL_USER}>"
    msg['To'] = ", ".join(EMAILS)
    msg['Subject'] = f"Hallucination Check: Tu dosis diaria de GenAI - {today}"
    msg.attach(MIMEText(html_body, 'html'))

    if audio_path and os.path.exists(audio_path):
        try:
            with open(audio_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename=Podcast_HC.mp3")
                msg.attach(part)
        except Exception as e:
            logger.warning(f"⚠️ No se pudo adjuntar el podcast: {e}")

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        logger.info("🚀 Newsletter enviado con éxito.")
    except Exception as e:
        logger.error(f"❌ Error al enviar email: {e}")
        raise e
