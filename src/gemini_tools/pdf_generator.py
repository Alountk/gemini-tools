import os
import google.generativeai as genai
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

load_dotenv()

def crear_pdf_local(nombre_archivo: str, titulo: str, contenido_markdown: str) -> str:
    """Genera un archivo PDF estructurado localmente."""
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
        'CustomTitle',
        parent=styles['Title'],
        fontSize=20,
        textColor=colors.HexColor('#1A73E8'),
        spaceAfter=15,
        alignment=0
    )
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#202124'),
        spaceAfter=10
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
    return f"PDF creado exitosamente: {os.path.abspath(nombre_archivo)}"


def procesar_peticion_pdf(prompt: str):
    """Inicializa Gemini con la herramienta de PDF y procesa el prompt."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: No se encontró GEMINI_API_KEY en el archivo .env ni en el entorno.")
        return

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        tools=[crear_pdf_local]
    )

    chat = model.start_chat(enable_automatic_function_calling=True)
    print("🤖 Procesando solicitud con Gemini...")
    respuesta = chat.send_message(prompt)
    print(f"\n✨ Respuesta de Gemini:\n{respuesta.text}")
