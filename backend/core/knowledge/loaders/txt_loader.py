from core.knowledge.loaders.base import DocumentLoader


class TxtLoader(DocumentLoader):
    """
    TXT document loader.
    """

    def load(self, file_path: str) -> str:
        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="replace"
        ) as file:
            return file.read()

    def supported_extension(self) -> str:
        return ".txt"