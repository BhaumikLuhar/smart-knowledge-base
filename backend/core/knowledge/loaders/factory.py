from pathlib import Path

from core.knowledge.loaders.base import DocumentLoader
from core.knowledge.loaders.docx_loader import DocxLoader
from core.knowledge.loaders.exceptions import (
    UnsupportedFileTypeError,
)
from core.knowledge.loaders.markdown_loader import (
    MarkdownLoader,
)
from core.knowledge.loaders.pdf_loader import PDFLoader
from core.knowledge.loaders.txt_loader import TxtLoader

LOADER_REGISTRY: dict[str, type[DocumentLoader]] = {}


def register_loader(extension: str, loader_class: type[DocumentLoader]):
    """
    Register loader for extension.
    """

    LOADER_REGISTRY[extension.lower()] = loader_class


def get_loader(file_path: str)-> DocumentLoader:
    """
    Return loader instance for file.
    """

    extension=Path(file_path).suffix.lower()

    if extension not in LOADER_REGISTRY:
         raise UnsupportedFileTypeError(
            f"No loader for '{extension}'. "
            f"Supported: "
            f"{list(LOADER_REGISTRY.keys())}"
        )
    
    return LOADER_REGISTRY[extension]()

register_loader(".pdf", PDFLoader)
register_loader(".docx", DocxLoader)
register_loader(".txt", TxtLoader)
register_loader(".md", MarkdownLoader)