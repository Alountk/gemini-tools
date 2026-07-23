import sys
from gemini_tools.pdf_generator import procesar_peticion_pdf

def main():
    prompt_args = " ".join(sys.argv[1:])
    
    # Comprobar si hay entrada enviada a través de un Pipe (|)
    prompt_stdin = ""
    if not sys.stdin.isatty():
        prompt_stdin = sys.stdin.read().strip()
        
    if prompt_stdin and prompt_args:
        # Combinar el texto del PDF leído con la instrucción dada
        prompt_final = f"Contenido del documento:\n\n{prompt_stdin}\n\nPetición del usuario:\n{prompt_args}"
    elif prompt_stdin:
        prompt_final = f"Contenido del documento:\n\n{prompt_stdin}\n\nPor favor, genera un PDF estructurado con esta información."
    elif prompt_args:
        prompt_final = prompt_args
    else:
        print("Uso: gemini-pdf \"Petición\" o bien: gemini-read-pdf doc.pdf | gemini-pdf \"Petición\"")
        return

    procesar_peticion_pdf(prompt_final)

if __name__ == "__main__":
    main()