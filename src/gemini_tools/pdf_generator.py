import os
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from gemini_tools.ai_provider import get_ai_provider

load_dotenv()

def crear_pdf_local(nombre_archivo: str, titulo: str, contenido_markdown: str) -> str:
    """Crea y guarda un archivo PDF estilizado en el sistema de archivos local."""
    if not nombre_archivo.endswith('.pdf'):
        nombre_archivo += '.pdf'
        
    doc = SimpleDocTemplate(
        nombre_archivo,
        pagesize=letter,
        rightMargin=40, leftMargin=40,
        topMargin=40, bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Title'],
        fontSize=20, textColor=colors.HexColor('#1A73E8'),
        spaceAfter=15, alignment=0
    )
    body_style = ParagraphStyle(
        'CustomBody', parent=styles['Normal'],
        fontSize=10, leading=15,
        textColor=colors.HexColor('#202124'), spaceAfter=10
    )
    
    story = [Paragraph(titulo, title_style), Spacer(1, 10)]
    
    for linea in contenido_markdown.split('\n'):
        linea_limpia = linea.strip()
        if not linea_limpia:
            continue
        linea_fmt = linea_limpia.replace('**', '<b>', 1)
        while '**' in linea_fmt:
            linea_fmt = linea_fmt.replace('**', '</b>', 1)
            
        story.append(Paragraph(linea_fmt, body_style))
        story.append(Spacer(1, 4))
        
    doc.build(story)
    return f"PDF creado exitosamente en: {os.path.abspath(nombre_archivo)}"

def procesar_peticion_pdf(prompt: str):
    """Procesa la petición delegando en el proveedor de IA configurado."""
    try:
        # Obtiene el proveedor (Gemini o Local según el .env)
        ai = get_ai_provider()
        
        print("🤖 Procesando solicitud...")
        # Se envían la solicitud y la herramienta de creación de PDF
        respuesta = ai.run_with_tools(prompt, tools=[crear_pdf_local])
        print(f"\n✨ Resultado:\n{respuesta}")
        
    except Exception as e:
        print(f"❌ Error al procesar la solicitud: {str(e)}")