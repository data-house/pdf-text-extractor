import json
from abc import ABC
from typing import List


class AChunk(ABC):
    """
    Abstract class to represent a chunk of a document
    """

    def __init__(self, text: str, metadata: dict = None, embedded_vector: List[float] = None):
        """
        :param text: the text contained in the chunk.
        :param metadata: additional data to identify the chunk in a document.
        :param embedded_vector: the embedding of text.
        """
        self.text = text
        self.metadata = metadata
        self.embedded_vector = embedded_vector

    def __str__(self) -> str:
        """
        Get a string representation of the chunk.
        :return: a string containing text and metadata of the chunk.
        """
        return json.dumps(self.to_dict())

    def __repr__(self):
        return self.__str__()

    def to_dict(self) -> dict:
        """
        Get a dict representation of the chunk.

        :return: a dictionary containing text and metadata of the chunk.
        """
        return {"text": self.text, "metadata": self.metadata}
