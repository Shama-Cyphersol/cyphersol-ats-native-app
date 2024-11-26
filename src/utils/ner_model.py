import spacy
import fitz  # PyMuPDF
from pathlib import Path
import json
from typing import Dict, List, Any
import re
import os

class BankStatementExtractor:
    def __init__(self, model_path: str):  # Fixed constructor name
        print(f"\n=== Loading NER model from {model_path} ===")
        self.nlp = spacy.load(model_path)
        print("✓ Model loaded successfully")

    def extract_text(self, pdf_path: str) -> str:
        """Extract only header information from first page"""
        print(f"\nExtracting text from: {pdf_path}")

        try:
            with fitz.open(pdf_path) as doc:
                # Only process first page
                page = doc.load_page(0)
                blocks = page.get_text("blocks")
                blocks.sort(key=lambda b: (b[1], b[0]))  # Sort by vertical then horizontal position

                # Define transaction markers to stop extraction
                transaction_markers = [
                    r'\d{2}-\d{2}-\d{4}',
                    r'Opening Balance',
                    r'Closing Balance',
                    r'Transaction Description',
                    r'UPI/',
                    r'NEFT/',
                    r'IMPS/'
                ]

                # Extract only header text
                header_text = []
                for block in blocks:
                    text = block[4].strip()
                    if any(re.search(marker, text) for marker in transaction_markers):
                        break
                    if text:
                        header_text.append(text)

                text = '\n'.join(header_text)
                print(f"✓ Extracted {len(text)} characters")
                return text
        except Exception as e:
            print(f"❌ Error extracting text: {str(e)}")
            return ""

    def process_statement(self, pdf_path: str) -> Dict[str, Any]:
        """Process a single bank statement"""
        # Extract text
        text = self.extract_text(pdf_path)
        if not text:
            return {"error": "Failed to extract text"}

        print("\nProcessing text with NER model...")
        doc = self.nlp(text)

        # Extract entities with positions
        entities = []
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "start": ent.start_char,
                "end": ent.end_char,
                "label": ent.label_
            })

        # Format results to match process_multiple_pdfs.py
        results = {
            "text": text,
            "entities": entities,
            "metadata": {
                "filename": Path(pdf_path).name,
                "path": pdf_path,
            }
        }

        print("\nExtracted Entities:")
        print(entities)
        for entity in entities:
            print(f"{entity['label']}: {entity['text']}")

        return results

def test_single_pdf(model_path: str, pdf_path: str) -> None:
    """Test model on a single PDF"""
    extractor = BankStatementExtractor(model_path)
    results = extractor.process_statement(pdf_path)
    results = results["entities"]
    # Save results
    # output_file = Path(pdf_path).stem + "_extraction.json"
    # with open(output_file, 'w', encoding='utf-8') as f:
    #     json.dump(results, f, indent=2, ensure_ascii=False)
    # print(f"\nResults saved to: {output_file}")
   
    return results

def pdf_to_name(pdf_path: str):
    model_path = "src/utils/trained_model"
    print("pdf_path ", pdf_path)
    result = test_single_pdf(model_path, pdf_path)
    return result

def main():
    # Paths
    # current_dir = os.getcwd()
    # print("curr", current_dir)
    # model_path = os.path.join(current_dir, "trained_model")
    model_path = "src/utils/trained_model"
    pdf_path= "aiya.pdf"
    test_single_pdf(model_path, pdf_path)

if __name__ == "__main__":
    main()