from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class ExtractedEntity:
    text: str
    label: str
    start_char: int
    end_char: int

@dataclass
class ProcessedDocument:
    filename: str
    timestamp: str
    raw_text: str
    preprocessed_text: str
    entities: List[ExtractedEntity]
    metadata: Dict
    error: Optional[str] = None