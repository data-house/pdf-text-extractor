from parsing_service.models.chunck import AChunk


class Chunk(AChunk):
    """
    A chunk of text.
    """

    def __init__(self, text: str, metadata: dict = None, embedded_vector: list = None):
        super().__init__(text, metadata, embedded_vector)
