# Hallucination Check 🗞️

[![Python version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/release/python-3120/) [![Gemini 2.5 Flash](https://img.shields.io/badge/AI%20Model-Gemini%202.5%20Flash-orange.svg)](https://ai.google.dev/models/gemini) [![Tavily API](https://img.shields.io/badge/Search%20API-Tavily-green.svg)](https://tavily.com/) [![Edge TTS](https://img.shields.io/badge/Speech%20Synthesis-Edge%20TTS-purple.svg)](https://developer.microsoft.com/en-us/microsoft-edge/whats-new/community-toolkit/text-to-speech) [![Notion API](https://img.shields.io/badge/Database-Notion%20API-pink.svg)](https://developers.notion.com/)

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
  - Notion (Opcional, para registro histórico) - *Configurable en `.env`*

---

## 🛠️ Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/Pierillo/hallucination-check.git
    cd hallucination-check
    ```

2.  **Crear entorno virtual e instalar dependencias:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Configurar variables de entorno:**
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

---

### 📊 Tabla Comparativa de Modelos de IA

| Model           | Cost         | Speed (Tokens/sec) | Context Window | Fine-tunability | Notes                                     |
| :-------------- | :----------- | :----------------- | :-------------- | :---------------------------------------- | ------------- |
| Gemini 2.5 Flash | Free Tier    | High               | 1M tokens       | Recommended for cost-effectiveness        |
| GPT-4           | $0.01/100k   | Moderate           | 128k tokens     | Powerful; higher cost                     |
| Claude 3 Opus   | $15/M tokens | High               | 200k tokens     | Strong reasoning, excels at long context |

*Disclaimer: Costs and specifications are approximate and may change. Always refer to official documentation for the latest information.*

---

### ❓ Preguntas Frecuentes (FAQs)

- **¿De qué trata el proyecto?**
  El proyecto es un agregador automatizado de noticias de IA para profesionales bancarios. El objetivo es filtrar el hype y mantenerlos informados sobre tendencias relevantes en IA, ahorrándoles tiempo.

- **¿Qué modelos de IA se utilizan?**
  Se utiliza Gemini 2.5 Flash para la generación de contenido y la API de Tavily para la búsqueda de noticias.

- **¿Cuál es el propósito de los agentes?**
  Los agentes están diseñados para curar noticias, redactar el contenido en un formato editorial, renderizar el newsletter final en HTML, y generar un resumen en podcast.

- **¿Cuáles son los beneficios principales para el usuario?**
  Los beneficios clave incluyen ahorro de tiempo, filtrado de información irrelevante, mantenerse al día con las tendencias de IA para profesionales bancarios, y recibir un newsletter y podcast resumidos diariamente.

---

### 🤝 Contribución

¡Agradecemos tus contribuciones para mejorar **Hallucination Check**!

#### Configuración del proyecto para contribuir
1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/Pierillo/hallucination-check.git
    ```
2.  **Navega al directorio:** `cd hallucination-check`
3.  **Configura el entorno virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
4.  **Instala dependencias:** `pip install -r requirements.txt`
5.  **Configura variables de entorno:** Copia `.env.example` a `.env` y completa con tus credenciales.

#### Flujo de desarrollo
1.  **Crea una nueva rama:** `git checkout -b feature/tu-feature`
2.  **Realiza tus cambios**
3.  **Añade y commitea tus cambios:** `git add .` y `git commit -m "feat: Add feature X"`
4.  **Sube tu rama:** `git push origin feature/your-feature-name`
5.  **Crea un Pull Request** en GitHub.

---

### 📄 Licencia

---------------------------------------------------------------------------
MIT License

Copyright (c) 2026 Piero Villalobos

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is 
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION 
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
---------------------------------------------------------------------------

---

## 📜 Changelog

Refer to the `changelog.md` file for detailed version history.
