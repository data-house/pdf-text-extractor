from fastapi import FastAPI
from parsing_service import init_logger
import logging

from text_extractor_api.routers import parser


def create_app():
    init_logger()
    logger = logging.getLogger(__name__)
    app = FastAPI()
    app.include_router(parser.router)

    @app.get("/")
    async def root():
        logger.info("Welcome to text extractor!")
        return {"message": "Welcome to text extractor!"}
    return app


application = create_app()


