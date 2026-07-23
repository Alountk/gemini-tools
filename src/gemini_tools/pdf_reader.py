import sys
import os
from pypdf import PdfReader


def extraer_texto_pdf(ruta_pdf: str) -> str:
    """Extract all selectable text from a local PDF file."""
    if not os.path.exists(ruta_pdf):
        return f"❌ Error: File '{ruta_pdf}' does not exist."

    try:
        reader = PdfReader(ruta_pdf)
        num_paginas = len(reader.pages)
        texto_completo = []

        texto_completo.append(
            f"--- Document: {os.path.basename(ruta_pdf)} ({num_paginas} pages) ---\n")

        for i, pagina in enumerate(reader.pages):
            texto_pagina = pagina.extract_text()
            if texto_pagina:
                texto_completo.append(f"--- Page {i + 1} ---")
                texto_completo.append(texto_pagina.strip())
                texto_completo.append("")  # Blank line between pages

        return "\n".join(texto_completo)

    except Exception as e:
        return f"❌ Error reading the PDF file: {str(e)}"


def main():
    if len(sys.argv) < 2:
        print("Usage: gemini-read-pdf /path/to/file.pdf")
        ruta = input("Enter the PDF path: ").strip()
    else:
        ruta = sys.argv[1]

    # Remove terminal-escaped quotes when the file is dragged into shell
    ruta = ruta.strip("'\"")

    print("📖 Reading local file...")
    resultado = extraer_texto_pdf(ruta)
    print("\n" + resultado)


if __name__ == "__main__":
    main()
