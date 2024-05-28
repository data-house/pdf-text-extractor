from abc import ABC, abstractmethod
from typing import List

from parsing_service.models.chunk import AChunk


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

    @abstractmethod
    def parse_to_json(self, filename: str, unit: str = None, roles: list = None):
        pass
