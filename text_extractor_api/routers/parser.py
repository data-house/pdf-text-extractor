import hashlib
import logging
import os

from fastapi import APIRouter, HTTPException, requests
from requests.exceptions import HTTPError, Timeout
import requests

from text_extractor_api.models import Document, ExtractTextRequest
from parsing_service.implementation.parser_factory import parse_file_to_json, parse_file
from text_extractor_api.routers.parser_utils import convert_json_to_document, convert_to_document

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/extract-test", response_model=Document)
async def parse_pdf(request: ExtractTextRequest) -> Document:
    logger.info("Received parse request")
    resource_path: str = os.environ.get("RESOURCE_PATH", "/tmp")

    try:
        os.mkdir(resource_path)
    except FileExistsError:
        pass

    if request.mime_type != 'application/pdf':
        mime = request.mime_type
        logger.warning(f"Unsupported format [{mime}]")
        raise HTTPException(status_code=422,
                            detail=f"Unsupported mime type. Expecting application/pdf received [{mime}]")

    filename = hashlib.sha256(request.path.encode()).hexdigest()
    extension = request.mime_type.split("/")[-1]
    filename = f"{filename}.{extension}"
    logger.info(f"Parsing {filename}")

    file_path = os.path.join(resource_path, filename)

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

    try:
        if request.driver.lower() == "Pdfact".lower():
            file_json = parse_file_to_json(filename=request.path, filetype=extension, unit=request.unit,
                                           roles=request.roles)
            document = convert_json_to_document(file_json)
        elif request.driver.lower() == "Pymupdf".lower():
            doc_parsed = parse_file(filename=file_path, filetype=extension)
            doc_parsed = {"status": "ok", "content": [chunk.to_dict() for chunk in doc_parsed]}
            document = convert_to_document(doc_parsed)
        else:
            raise HTTPException(status_code=422, detail="Error unsupported driver")
    except ValueError as ve:
        logger.exception("Unsupported file type", exc_info=True)
        raise HTTPException(status_code=422, detail="Unsupported file type")
    except Exception as err:
        logger.exception("Error while parsing file", exc_info=True)
        raise HTTPException(status_code=500, detail="Error while parsing file")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

    return document
