# Hallucination Check 🗞️

> "Tu dosis matutina de realidad para filtrar el hype de la IA antes del primer café."

**Hallucination Check** es un motor agéntico automatizado diseñado para equipos bancarios y de estrategia que necesitan mantenerse al día con el vertiginoso mundo de la IA Generativa, sin perder tiempo en noticias irrelevantes o "hype" corporativo.

---

## 🏗️ Arquitectura del Flujo Agéntico

El sistema utiliza una arquitectura de tres agentes encadenados impulsados por **Gemini 2.5 Flash** para garantizar calidad y relevancia:

1.  **🕵️ Agente Curator:** Lanza búsquedas masivas con **Tavily API**, filtra duplicados históricos y evalúa cada noticia con un score de relevancia (0-10) según su impacto bancario y novedad (máx. 3 semanas).
2.  **✍️ Agente Redactor:** Toma las 10 mejores noticias y genera el contenido editorial con un tono relajado, amigable y directo.
3.  **🎨 Agente HTML:** Renderiza el newsletter final con un diseño profesional, limpio y optimizado para lectura rápida.
4.  **🎙️ Podcast Generator:** Crea un monólogo ejecutivo de ~10 minutos en español (voz neuronal de Microsoft) y lo adjunta como MP3.

---

## 🚀 Requisitos del Sistema

- **Python 3.12+**
- Cuentas y API Keys de:
  - Google Gemini (AI Studio)
  - Tavily (Search)
  - Gmail (App Password para SMTP)
  - Notion (Opcional, para registro histórico)

---

## 🛠️ Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone <url-del-repo>
   cd hallucination-check
   ```

2. **Crear entorno virtual e instalar dependencias:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno:**
   ```bash
   cp .env.example .env
   # Edita el archivo .env con tus credenciales reales
   nano .env
   ```

---

## 💻 Uso

### Ejecución Manual
```bash
python3 genai_newsletter/newsletter.py
```

### Configuración en VPS (Cron Job)
Para recibirlo todos los días a las 8:00 AM:
```bash
0 8 * * * /ruta/al/venv/bin/python3 /ruta/al/proyecto/genai_newsletter/newsletter.py >> /ruta/al/proyecto/genai_newsletter/newsletter.log 2>&1
```

---

## 📓 Integración con Notion
El script guarda cada edición en una base de datos de Notion. Asegúrate de:
1. Crear una integración en [Notion Developers](https://www.notion.so/my-integrations).
2. Compartir tu base de datos con la integración.
3. Configurar `NOTION_TOKEN` y `NOTION_DATABASE_ID` en tu `.env`.

---

## 🆘 Troubleshooting

- **Error 429 (Quota Exceeded):** Estás usando el nivel gratuito de Gemini y has superado el límite diario (20 peticiones). Espera al reseteo de cuota.
- **Gmail SMTP Error:** Asegúrate de tener la "Verificación en 2 pasos" activa y estar usando una "App Password", no tu contraseña normal.
- **Notion 401 Unauthorized:** Tu token de Notion es incorrecto o no has compartido la base de datos con la integración.
