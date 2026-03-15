from config import call_llm, logger

def run_renderer(editorial_content, curated_news):
    """Agente Diseñador: Convierte el contenido en un email HTML profesional."""
    logger.info("🎨 Agente HTML activado: Renderizando diseño final...")
    
    combined_content = ""
    for i, item in enumerate(editorial_content["news"]):
        img_url = curated_news[i].get("image")
        img_html = f"<img src='{img_url}' style='width:100%; border-radius:8px; margin-bottom:10px;'>" if img_url else ""
        combined_content += f"""
        <div class="card" style="background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; margin-bottom: 20px;">
            {img_html}
            <h3 style="color: #3b82f6; margin-top: 0;">{item['headline']}</h3>
            <p style="color: #334155; line-height: 1.5;">{item['summary']}</p>
            <a href="{item['url']}" style="color: #3b82f6; font-weight: bold; text-decoration: none;">Leer realidad →</a>
        </div>
        """

    prompt = f"""
    Eres un diseñador web experto en Email Marketing. Toma el contenido y construye un email HTML completo.
    
    DISEÑO:
    - Nombre: Hallucination Check
    - Bajada: "Tu dosis matutina de realidad para filtrar el hype de la IA antes del primer café."
    - Colores: Fondo gris muy claro (#f4f4f5), tarjetas blancas, azul corporativo (#3b82f6).
    
    ORDEN OBLIGATORIO:
    1. Header con logo/título.
    2. Podcast (Sección destacada indicando que hay audio adjunto).
    3. Bloque de 10 noticias.
    4. 🎯 SO WHAT: {editorial_content['so_what']}
    5. 🎧 RECOMENDACIÓN DEL DÍA: {editorial_content['recommendation']}
    
    Noticias:
    {combined_content}
    
    Responde solo con HTML puro y CSS inline.
    """
    
    return call_llm(prompt)
