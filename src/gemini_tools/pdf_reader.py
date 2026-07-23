import sys
import os
from pypdf import PdfReader


def extract_pdf_text(pdf_path: str) -> str:
    """Extract all selectable text from a local PDF file."""
    if not os.path.exists(pdf_path):
        return f"❌ Error: File '{pdf_path}' does not exist."

    try:
        reader = PdfReader(pdf_path)
        page_count = len(reader.pages)
        full_text = []

        full_text.append(
            f"--- Document: {os.path.basename(pdf_path)} ({page_count} pages) ---\n")

        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                full_text.append(f"--- Page {i + 1} ---")
                full_text.append(page_text.strip())
                full_text.append("")  # Blank line between pages

        return "\n".join(full_text)

    except Exception as e:
        return f"❌ Error reading the PDF file: {str(e)}"


def main():
    if len(sys.argv) < 2:
        print("Usage: gemini-read-pdf /path/to/file.pdf")
        pdf_path = input("Enter the PDF path: ").strip()
    else:
        pdf_path = sys.argv[1]

    # Remove terminal-escaped quotes when the file is dragged into shell
    pdf_path = pdf_path.strip("'\"")

    print("📖 Reading local file...")
    result = extract_pdf_text(pdf_path)
    print("\n" + result)


# Backward-compatible alias
extraer_texto_pdf = extract_pdf_text


if __name__ == "__main__":
    main()
