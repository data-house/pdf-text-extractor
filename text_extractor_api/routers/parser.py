import hashlib
import logging
import os

import requests
from fastapi import APIRouter, HTTPException
from requests.exceptions import HTTPError, Timeout

from parsing_service.parser.pdfact_parser import PdfactParser
from parsing_service.parser.pymupdf_parser import PymupdfParser
from text_extractor_api.models import ExtractTextRequest
from parsing_service.models import Document

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/extract-test", response_model=Document)
async def parse_pdf(request: ExtractTextRequest) -> Document:
    logger.info("Received parse request.")
    resource_path: str = os.environ.get("RESOURCE_PATH", "/tmp")

    try:
        os.mkdir(resource_path)
    except FileExistsError:
        pass

    if request.mime_type != 'application/pdf':
        mime = request.mime_type
        logger.warning(f"Unsupported format [{mime}]")
        raise HTTPException(status_code=422,
                            detail=f"Unsupported mime type. Expecting application/pdf received [{mime}].")

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
        logger.exception("Error while downloading file.", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error while downloading file [{http_err}]")
    except Timeout as http_timeout:
        logger.exception("Timeout while downloading file.", exc_info=True)
        raise HTTPException(status_code=500, detail=f"File download not completed [{http_timeout}]")
    except Exception as requestError:
        logger.exception(f"Error while downloading file. {str(requestError)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error while saving file")

    try:
        document = None
        if request.driver.lower() == "pdfact":
            parser = PdfactParser()
            document = parser.parse(filename=request.path, unit=request.unit, roles=request.roles)
        elif request.driver.lower() == "pymupdf":
            parser = PymupdfParser()
            document = parser.parse(filename=file_path)
    except Exception as err:
        logger.exception(f"Error while parsing file. {str(err)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error while parsing file")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
    if document is None:
        raise HTTPException(status_code=422, detail="Error unsupported driver")
    return document
