import fitz
import spacy
import json
from datetime import datetime
from pathlib import Path
from typing import Union, Dict, List
from .data_models import ExtractedEntity, ProcessedDocument

class PDFProcessor:
    def __init__(self, model_path: str = "output_ner_model"):
        """Initialize the PDF processor with the trained spaCy model"""
        try:
            # Disable GPU and use CPU only
            spacy.require_cpu()
            self.nlp = spacy.load(model_path)
            self.processed_documents = []
        except Exception as e:
            raise Exception(f"Failed to load spaCy model: {str(e)}")

    def process_single_pdf(self, pdf_path: Union[str, Path]) -> ProcessedDocument:
        """Process a single PDF file and return structured results"""
        print(f"\nPDFProcessor: Starting to process {pdf_path}")
        
        try:
            pdf_path = Path(pdf_path)
            timestamp = datetime.now().isoformat()
            
            # Extract text from PDF
            print("PDFProcessor: Extracting text from PDF...")
            extracted_data = self._extract_text_from_pdf(pdf_path)
            
            if "error" in extracted_data:
                print(f"PDFProcessor: Error in text extraction - {extracted_data['error']}")
                return ProcessedDocument(
                    filename=pdf_path.name,
                    timestamp=timestamp,
                    raw_text="",
                    preprocessed_text="",
                    entities=[],
                    metadata={},
                    error=extracted_data["error"]
                )
            
            # Process with spaCy
            print("PDFProcessor: Processing with spaCy model...")
            entities = self._process_with_spacy(extracted_data["preprocessed_text"])
            print(f"PDFProcessor: Found {len(entities)} entities")
            for entity in entities:
                print(f"PDFProcessor: Found entity - {entity.label}: {entity.text}")
            
            # Create processed document
            processed_doc = ProcessedDocument(
                filename=pdf_path.name,
                timestamp=timestamp,
                raw_text=extracted_data["raw_text"],
                preprocessed_text=extracted_data["preprocessed_text"],
                entities=entities,
                metadata={
                    "account_number": extracted_data["account_number"],
                    "person_name": extracted_data["person_name"],
                    "file_path": str(pdf_path.absolute())
                }
            )
            
            print("PDFProcessor: Document processing complete")
            return processed_doc
            
        except Exception as e:
            print(f"PDFProcessor: Error processing document - {str(e)}")
            import traceback
            print(traceback.format_exc())
            return ProcessedDocument(
                filename=pdf_path.name,
                timestamp=datetime.now().isoformat(),
                raw_text="",
                preprocessed_text="",
                entities=[],
                metadata={},
                error=str(e)
            )

    def _process_with_spacy(self, text: str) -> List[ExtractedEntity]:
        """Process text with spaCy model and return structured entities"""
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entity = ExtractedEntity(
                text=ent.text,
                label=ent.label_,
                start_char=ent.start_char,
                end_char=ent.end_char
            )
            entities.append(entity)
            
        return entities

    def process_multiple_pdfs(self, pdf_dir: Union[str, Path]) -> List[ProcessedDocument]:
        """Process all PDFs in a directory"""
        pdf_dir = Path(pdf_dir)
        results = []
        
        for pdf_file in pdf_dir.glob("**/*.pdf"):
            result = self.process_single_pdf(pdf_file)
            results.append(result)
            
        return results

    def export_results(self, output_path: Union[str, Path], format: str = "json"):
        """Export processing results to specified format"""
        output_path = Path(output_path)
        
        if format.lower() == "json":
            self._export_to_json(output_path)
        elif format.lower() == "excel":
            self._export_to_excel(output_path)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _export_to_json(self, output_path: Path):
        """Export results to JSON format"""
        results = []
        for doc in self.processed_documents:
            doc_dict = {
                "filename": doc.filename,
                "timestamp": doc.timestamp,
                "metadata": doc.metadata,
                "entities": [
                    {
                        "text": ent.text,
                        "label": ent.label,
                        "start_char": ent.start_char,
                        "end_char": ent.end_char
                    }
                    for ent in doc.entities
                ],
                "error": doc.error
            }
            results.append(doc_dict)
            
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

    def get_summary(self) -> Dict:
        """Get summary of processed documents"""
        return {
            "total_documents": len(self.processed_documents),
            "successful": len([doc for doc in self.processed_documents if not doc.error]),
            "failed": len([doc for doc in self.processed_documents if doc.error]),
            "total_entities": sum(len(doc.entities) for doc in self.processed_documents)
        }

    def _extract_text_from_pdf(self, pdf_path: Path) -> Dict:
        """Extract text from PDF and perform initial preprocessing"""
        try:
            # Open PDF with PyMuPDF (fitz)
            doc = fitz.open(pdf_path)
            raw_text = ""
            
            # Extract text from all pages
            for page in doc:
                raw_text += page.get_text()
            
            doc.close()
            
            # Basic preprocessing
            preprocessed_text = raw_text.strip()
            
            # Initialize default values
            account_number = ""
            person_name = ""
            
            # TODO: Add specific logic to extract account number and person name
            # This would depend on your bank statement format
            
            return {
                "raw_text": raw_text,
                "preprocessed_text": preprocessed_text,
                "account_number": account_number,
                "person_name": person_name
            }
            
        except Exception as e:
            return {"error": f"Failed to extract text from PDF: {str(e)}"}
