import logging
import pdfplumber

from core.config import settings
from core.knowledge.loaders.base import DocumentLoader

logger = logging.getLogger(__name__)

class PDFLoader(DocumentLoader):
    """
    PDF document loader.
    """

    def __init__(self):
        self.page_count=0

    def load(self, file_path: str)->str:
        text_parts=[]

        with pdfplumber.open(file_path) as pdf:
            pages=pdf.pages[:settings.MAX_PAGES_PER_DOC]

            self.page_count=len(pages)

            for index, page in enumerate(pages):
                page_text=page.extract_text()

                if not page_text:
                    logger.warning(
                        f"Skipping empty/image-only page "
                        f"{index} in {file_path}"
                    )
                    continue

                text_parts.append(page_text)
            
        return "\n\n".join(text_parts)
    

    def supported_extension(self)->str:
        return ".pdf"