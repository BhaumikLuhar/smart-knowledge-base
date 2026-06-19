from abc import ABC, abstractmethod


class DocumentLoader(ABC):
    """
    Base class for all document loaders.
    """

    @abstractmethod
    def load(self, file_path: str) -> str:
        """
        Read file from disk and return raw text.
        """
        pass

    @abstractmethod
    def supported_extension(self) -> str:
        """
        Return supported extension.
        Example: .pdf
        """
        pass