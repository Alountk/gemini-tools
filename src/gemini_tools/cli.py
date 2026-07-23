import sys
from gemini_tools.pdf_generator import procesar_peticion_pdf


def main():
    if len(sys.argv) < 2:
        print("Uso: gemini-pdf \"Descripción del PDF que deseas generar\"")
        sys.argv.append(input("Petición: "))

    prompt = " ".join(sys.argv[1:])
    procesar_peticion_pdf(prompt)


if __name__ == "__main__":
    main()
