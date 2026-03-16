# Hallucination Check 🗞️

[![Python version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/release/python-3120/) [![DeepSeek V3](https://img.shields.io/badge/AI%20Model-DeepSeek%20V3%20(OpenRouter)-blue.svg)](https://openrouter.ai/) [![Gemini 2.5 Flash](https://img.shields.io/badge/Fallback-Gemini%202.5%20Flash-orange.svg)](https://ai.google.dev/models/gemini) [![Tavily API](https://img.shields.io/badge/Search%20API-Tavily-green.svg)](https://tavily.com/)

> "Tu dosis matutina de realidad para filtrar el hype de la IA antes del primer café."

**Hallucination Check** es un motor agéntico modular diseñado para equipos bancarios y de estrategia que necesitan mantenerse al día con el vertiginoso mundo de la IA Generativa, filtrando el ruido irrelevante.

---

## 🏗️ Arquitectura Modular

El sistema utiliza una arquitectura de agentes especializados encadenados, coordinados por un orquestador central:

1.  **🕵️ Agente Curator (`agents/curator.py`):** Lanza búsquedas con **Tavily API**, filtra duplicados históricos y evalúa relevancia (0-10).
2.  **✍️ Agente Writer (`agents/writer.py`):** Genera contenido editorial con un tono ameno y directo.
3.  **🎨 Agente Renderer (`agents/renderer.py`):** Diseña el newsletter en HTML profesional y optimizado.
4.  **🎙️ Agente Podcast (`agents/podcast.py`):** Crea un monólogo ejecutivo de ~10 min (Edge TTS) adjunto como MP3.

**Modelos:**
- **Primario:** `DeepSeek V3` (vía OpenRouter) para máxima precisión y razonamiento.
- **Fallback:** `Gemini 2.5 Flash` (vía Google API) en caso de fallos o límites de cuota.

---

## 🚀 Instalación y Uso

1.  **Entorno Virtual:** Se recomienda usar el entorno preconfigurado `venv_newsletter`.
    ```bash
    source venv_newsletter/bin/activate
    pip install -r requirements.txt
    ```

2.  **Configuración:** Copia `.env.example` a `.env` y añade tus claves (OpenRouter, Gemini, Tavily, Gmail, Notion).

3.  **Ejecución:**
    ```bash
    python3 genai_newsletter/main.py
    ```

---

## 🆘 Troubleshooting

- **Error 429 (Quota Exceeded):** El sistema intentará automáticamente el fallback a Gemini si OpenRouter falla.
- **Notion 401 Unauthorized:** Verifica tu token de integración. El flujo continuará aunque Notion falle para asegurar el envío del email.

---

## 🤝 Contribución

¡Agradecemos tus contribuciones! El flujo modular facilita añadir nuevos agentes o utilidades en las carpetas `agents/` y `utils/`.
