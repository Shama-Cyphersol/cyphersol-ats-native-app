import fitz
import spacy
import json
from datetime import datetime
from pathlib import Path
from typing import Union, Dict, List
from .data_models import ExtractedEntity, ProcessedDocument
import re

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
        try:
            pdf_path = Path(pdf_path)
            timestamp = datetime.now().isoformat()
            
            # Extract text from PDF
            extracted_data = self._extract_text_from_pdf(pdf_path)
            
            if "error" in extracted_data:
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
            entities = self._process_with_spacy(extracted_data["preprocessed_text"])
            
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
                },
                header_text=extracted_data.get("header_text"),
                header_file_path=extracted_data.get("header_file_path")
            )
            
            # Store processed document
            self.processed_documents.append(processed_doc)
            return processed_doc
            
        except Exception as e:
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
        try:
            # Extract full text
            text = ""
            with fitz.open(pdf_path) as doc:
                if doc.is_encrypted:
                    raise fitz.FileDataError("PDF is password protected")
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text += page.get_text("text") + "\n"

            # Find where the table starts
            table_patterns = [
                r"^\s*(Tran|Transaction|Date|Particulars|Value|Ref|Amount|Debit|Credit|Balance)",
                r"^\s*\d{1,2}-\d{1,2}-\d{2,4}",
                r"^-{3,}",
            ]

            # Find earliest table indicator
            split_position = len(text)
            for pattern in table_patterns:
                match = re.search(pattern, text, re.MULTILINE)
                if match and match.start() < split_position:
                    split_position = match.start()

            # Extract header content (pre-table text)
            header_content = text[:split_position].strip()

            # Extract account number and person name for metadata (but don't remove from text!)
            account_pattern = re.compile(r'\bAccount\s*(No|Number)?\s*[:\-]?\s*(\S+)', re.IGNORECASE)
            name_pattern = re.compile(r'\bName\s*[:\-]?\s*(.+)', re.IGNORECASE)
            
            account_match = account_pattern.search(header_content)
            name_match = name_pattern.search(header_content)
            
            account_number = account_match.group(2) if account_match else ""
            person_name = name_match.group(1).strip() if name_match else ""

            # Only clean extra whitespace and non-printable chars
            preprocessed_text = header_content
            preprocessed_text = re.sub(r'\s+', ' ', preprocessed_text).strip()
            preprocessed_text = re.sub(r'[^\x20-\x7E\n]', '', preprocessed_text)

            # Save the preprocessed text (with names and account numbers intact)
            output_dir = Path("extracted_text")
            output_dir.mkdir(exist_ok=True)
            text_file_path = output_dir / f"{pdf_path.stem}_header.txt"
            
            with open(text_file_path, 'w', encoding='utf-8') as f:
                f.write(preprocessed_text)

            return {
                "raw_text": header_content,
                "preprocessed_text": preprocessed_text,
                "account_number": account_number,
                "person_name": person_name,
                "header_text": preprocessed_text,
                "header_file_path": str(text_file_path)
            }

        except fitz.FileDataError as e:
            if "password protected" in str(e).lower():
                return {"error": "Password Protected"}
            return {"error": str(e)}
        except Exception as e:
            return {"error": f"Failed to extract text from PDF: {str(e)}"}