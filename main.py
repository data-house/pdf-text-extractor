from fastapi import FastAPI, HTTPException, Request, UploadFile, File
import shutil
import os
import hashlib
from requests.exceptions import HTTPError, Timeout
from pydantic import BaseModel
import requests

from parsing_service.implementation.parser_factory import parse_file_to_json
from parsing_service.logger import init_logger
import logging

logger = logging.getLogger(__name__)


class ExtractTextRequest(BaseModel):
    path: str
    mime_type: str


def create_app():
    init_logger()
    app = FastAPI()

    app.resource_path = os.environ.get("RESOURCE_PATH", "/tmp")

    try:
        os.mkdir(app.resource_path)
    except FileExistsError:
        # pass?
        logger.info(f"{app.resource_path} already exists")

    @app.post("/parse-pdf")
    async def parse_pdf(request: ExtractTextRequest):
        logger.info("Received parse request")

        if request.mime_type != 'application/pdf':
            mime = request.mime_type
            logger.warning(f"Unsupported format [{mime}]")
            raise HTTPException(status_code=422,
                                detail=f"Unsupported mime type. Expecting application/pdf received [{mime}]")

        filename = hashlib.sha256(request.path.encode()).hexdigest()
        extension = request.mime_type.split("/")[-1]
        filename = f"{filename}.{extension}"
        logger.info(f"Parsing {filename}")

        file_path = os.path.join(app.resource_path, filename)

        if request.path.startswith("http://") or request.path.startswith("https://"):
            try:
                resp = requests.get(request.path, allow_redirects=True, timeout=120)
                resp.raise_for_status()

                with open(file_path, 'wb') as f:
                    f.write(resp.content)
            except HTTPError as http_err:
                logger.exception("Error while downloading file", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error while downloading file [{http_err}]")
            except Timeout as http_timeout:
                logger.exception("Timeout while downloading file", exc_info=True)
                raise HTTPException(status_code=500, detail=f"File download not completed [{http_timeout}]")
            except Exception as requestError:
                logger.exception("Error while downloading file", exc_info=True)
                raise HTTPException(status_code=500, detail="Error while saving file")
        else:
            if not os.path.exists(request.path):
                logger.warning("File not found")
                raise HTTPException(status_code=404, detail="File not found")
            shutil.copy(request.path, file_path)

        try:
            file_json = parse_file_to_json(file_path, extension)
        except ValueError as ve:
            logger.exception("Unsupported file type", exc_info=True)
            raise HTTPException(status_code=422, detail="Unsupported file type")
        except Exception as err:
            logger.exception("Error while parsing file", exc_info=True)
            raise HTTPException(status_code=500, detail="Error while parsing file")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

        return file_json

    return app


application = create_app()
