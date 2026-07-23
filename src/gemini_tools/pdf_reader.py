import sys
import os
from pypdf import PdfReader


def extraer_texto_pdf(ruta_pdf: str) -> str:
    """Extrae todo el texto seleccionable de un archivo PDF local."""
    if not os.path.exists(ruta_pdf):
        return f"❌ Error: El archivo '{ruta_pdf}' no existe."

    try:
        reader = PdfReader(ruta_pdf)
        num_paginas = len(reader.pages)
        texto_completo = []

        texto_completo.append(
            f"--- Documento: {os.path.basename(ruta_pdf)} ({num_paginas} páginas) ---\n")

        for i, pagina in enumerate(reader.pages):
            texto_pagina = pagina.extract_text()
            if texto_pagina:
                texto_completo.append(f"--- Página {i + 1} ---")
                texto_completo.append(texto_pagina.strip())
                texto_completo.append("")  # Línea en blanco entre páginas

        return "\n".join(texto_completo)

    except Exception as e:
        return f"❌ Error al leer el archivo PDF: {str(e)}"


def main():
    if len(sys.argv) < 2:
        print("Uso: gemini-read-pdf /ruta/al/archivo.pdf")
        ruta = input("Introduce la ruta del PDF: ").strip()
    else:
        ruta = sys.argv[1]

    # Eliminar comillas escapadas por la terminal si se arrastra el archivo
    ruta = ruta.strip("'\"")

    print("📖 Leyendo archivo localmente...")
    resultado = extraer_texto_pdf(ruta)
    print("\n" + resultado)


if __name__ == "__main__":
    main()
