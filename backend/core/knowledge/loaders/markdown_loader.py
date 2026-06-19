from core.knowledge.loaders.base import DocumentLoader


class MarkdownLoader(DocumentLoader):
    """
    Markdown loader.

    Future:
    Strip markdown syntax for cleaner embeddings,
    or keep it for LLM readability.
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
        return ".md"