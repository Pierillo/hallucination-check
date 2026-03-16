# Changelog

## [1.1.0] - 2026-03-16

### Added
- **Arquitectura Modular:** El sistema ahora se divide en agentes especializados (`agents/`) y utilidades (`utils/`), facilitando el mantenimiento y la escalabilidad.
- **Orquestador Principal (`main.py`):** Nuevo punto de entrada que maneja checkpoints para permitir reanudar el flujo en caso de fallos intermedios.
- **Integración con OpenRouter:** Soporte para utilizar **DeepSeek V3** como modelo de lenguaje principal, ofreciendo mayor precisión estratégica.
- **Lógica de Fallback Inteligente:** Implementación de respaldo automático a **Gemini 2.5 Flash** si el proveedor principal falla.
- **Persistencia Atómica:** Mejora en la gestión del historial de URLs y checkpoints para evitar corrupción de datos.

### Fixed
- Corregido error de importación (`NameError`) en la función de recuperación de LLM.
- Solucionado error 404 al llamar a versiones de modelos Gemini obsoletas o no disponibles.
- Mejorada la gestión de excepciones en la integración con Notion.

## [1.0.0] - 2026-03-14

### Added
- Configuración inicial y estructura del proyecto.
- Integración con Gemini 2.5 Flash para generación de contenido.
- Integración con Tavily API para búsqueda y filtrado de noticias.
- Integración con Edge TTS para generación de podcasts en español.
- Integración con Notion para registro histórico.