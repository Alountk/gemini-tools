import sys
from gemini_tools.pdf_generator import procesar_peticion_pdf

def main():
    prompt_args = " ".join(sys.argv[1:])
    
    # Check for input piped through stdin (|)
    prompt_stdin = ""
    if not sys.stdin.isatty():
        prompt_stdin = sys.stdin.read().strip()
        
    if prompt_stdin and prompt_args:
        # Combine extracted PDF text with the user instruction
        prompt_final = f"Document content:\n\n{prompt_stdin}\n\nUser request:\n{prompt_args}"
    elif prompt_stdin:
        prompt_final = f"Document content:\n\n{prompt_stdin}\n\nPlease generate a structured PDF using this information."
    elif prompt_args:
        prompt_final = prompt_args
    else:
        print("Usage: gemini-pdf \"Request\" or: gemini-read-pdf doc.pdf | gemini-pdf \"Request\"")
        return

    procesar_peticion_pdf(prompt_final)

if __name__ == "__main__":
    main()