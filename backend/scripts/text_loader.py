from core.knowledge.loaders.factory import get_loader
from pathlib import Path

from core.knowledge.file_service import FileService

loader = get_loader("sample.pdf")

print(type(loader).__name__)
