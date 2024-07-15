import logging

from fastapi import FastAPI

from text_extractor import init_logger
from text_extractor_api.routers import parser

init_logger()
logger = logging.getLogger(__name__)
app = FastAPI()
app.include_router(parser.router)


async def root():
    logger.info("Welcome to text extractor!")
    return {"message": "Welcome to text extractor!"}
