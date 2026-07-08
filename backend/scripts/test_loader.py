# from core.knowledge.loaders.factory import get_loader
# from pathlib import Path

# from core.knowledge.file_service import FileService

# loader = get_loader("sample.pdf")

# print(type(loader).__name__)



## Test registering a new loader and retrieving it from the registry

from core.knowledge.loaders.base import DocumentLoader
from core.knowledge.loaders.factory import (
    get_loader,
    register_loader,
)


class CsvLoader(DocumentLoader):

    def load(self, file_path: str) -> str:
        return "csv"

    def supported_extension(self) -> str:
        return ".csv"


register_loader(
    ".csv",
    CsvLoader,
)

loader = get_loader("test.csv")

assert isinstance(loader, CsvLoader)

print("✓ Loader registry extension test passed")