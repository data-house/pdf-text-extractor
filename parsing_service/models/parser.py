from abc import ABC, abstractmethod
from typing import List

from parsing_service.models.chunck import AChunk


class Parser(ABC):
    """
    Abstract class to implement a generic document parser (.pdf, .doc, etc.)
    """

    @abstractmethod
    def parse(self, filename: str) -> List[AChunk]:
        """
        Read and extract the text from a document into a list of chunks.

        :param filename: a string representing the path to access the document.
        :return: a list of chunk extracted from the document.
        """
        pass
