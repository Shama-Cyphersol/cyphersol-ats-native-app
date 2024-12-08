import pdfplumber
import re
import spacy


def clean_line(line: str) -> str:
    """Clean a single line of text while preserving important information."""
    line = re.sub(r"^\s*(?:\d+\.|\(\d+\)|\d+)\s*", "", line)
    line = re.sub(r"\(cid:\d+\)", " ", line)
    line = line.replace("??", " ")
    line = "".join(char if char.isprintable() else " " for char in line)
    line = re.sub(r"\s+", " ", line)
    return line.strip()


def extract_entities(pdf_path: str, num_lines: int = 10):
    """Extract entities from PDF file and return only the entity texts."""
    try:
        nlp = spacy.load("src/utils/trained_model_lg_v2_final")

        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""

            lines = [clean_line(line) for line in text.split("\n") if clean_line(line)]
            processed_text = "\n".join(lines[:num_lines])

            doc = nlp(processed_text)
            entities = [
                ent.text for ent in doc.ents if ent.text
            ]  # Only collect entity texts
            return entities if entities else None

    except Exception as e:
        return None


# Example usage
if __name__ == "__main__":
    pdf_path = "kotak.pdf"
    entities = extract_entities(pdf_path)
    if entities:
        for entity in entities:
            print(f"Detected entity: {entity}")
