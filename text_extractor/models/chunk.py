import json


class Chunk:
    """
    A chunk of text
    """

    def __init__(self, text: str, metadata: dict = None):
        """
        :param text: the text contained in the chunk.
        :param metadata: additional data to identify the chunk in a document.
        """
        self.text = text
        self.metadata = metadata

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
