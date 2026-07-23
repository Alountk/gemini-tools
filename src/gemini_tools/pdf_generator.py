import os
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from gemini_tools.ai_provider import get_ai_provider

load_dotenv()

def create_local_pdf(filename: str, title: str, markdown_content: str) -> str:
    """Create and save a styled PDF file on the local filesystem."""
    if not filename.endswith('.pdf'):
        filename += '.pdf'
        
    doc = SimpleDocTemplate(
        filename,
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
    
    story = [Paragraph(title, title_style), Spacer(1, 10)]
    
    for line in markdown_content.split('\n'):
        clean_line = line.strip()
        if not clean_line:
            continue
        formatted_line = clean_line.replace('**', '<b>', 1)
        while '**' in formatted_line:
            formatted_line = formatted_line.replace('**', '</b>', 1)
            
        story.append(Paragraph(formatted_line, body_style))
        story.append(Spacer(1, 4))
        
    doc.build(story)
    return f"PDF created successfully at: {os.path.abspath(filename)}"

def process_pdf_request(prompt: str):
    """Process the request using the configured AI provider."""
    try:
        # Get the provider (Gemini or Local based on .env)
        ai_provider = get_ai_provider()
        
        print("🤖 Processing request...")
        # Send the request and the PDF generation tool
        response = ai_provider.run_with_tools(prompt, tools=[create_local_pdf])
        print(f"\n✨ Result:\n{response}")
        
    except Exception as e:
        print(f"❌ Error while processing the request: {str(e)}")


# Backward-compatible aliases
crear_pdf_local = create_local_pdf
procesar_peticion_pdf = process_pdf_request