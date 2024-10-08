import hashlib
import logging
import os

import requests
from fastapi import APIRouter, HTTPException
from requests.exceptions import HTTPError, Timeout, RequestException

from parse_document_model import Document
from text_extractor.parser.pdfact_parser import PdfactParser
from text_extractor.parser.pymupdf_parser import PymupdfParser
from text_extractor_api.config import settings
from text_extractor_api.models import ExtractTextRequest

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/extract-text", response_model=Document)
async def parse_pdf(request: ExtractTextRequest) -> Document:
    logger.info("Received parse request.")
    resource_path: str = os.environ.get("RESOURCE_PATH", "/tmp")

    if request.mime_type != 'application/pdf':
        mime = request.mime_type
        raise HTTPException(status_code=422, detail=f"Unsupported mime type[{mime}]. Expecting application/pdf.")

    if request.driver.lower() not in ["pdfact", "pymupdf"]:
        raise HTTPException(status_code=400,
                            detail=f"Unsupported driver. Expecting 'pdfact' or 'pymupdf', received [{request.driver}].")

    try:
        os.mkdir(resource_path)
    except FileExistsError:
        pass

    if request.mime_type != 'application/pdf':
        mime = request.mime_type
        logger.warning(f"Unsupported format [{mime}]")
        raise HTTPException(status_code=422,
                            detail=f"Unsupported mime type. Expecting application/pdf received [{mime}].")

    filename = hashlib.sha256(request.url.encode()).hexdigest()
    extension = request.mime_type.split("/")[-1]
    filename = f"{filename}.{extension}"
    logger.info(f"Parsing {filename}")

    file_path = os.path.join(resource_path, filename)

    try:
        resp = requests.get(request.url, allow_redirects=True, timeout=120)
        resp.raise_for_status()
        with open(file_path, 'wb') as f:
            f.write(resp.content)
    except HTTPError as http_err:
        logger.exception("Error while downloading file.", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Error while downloading file [{http_err}]")
    except Timeout as http_timeout:
        logger.exception("Timeout while downloading file.", exc_info=True)
        raise HTTPException(status_code=408, detail=f"File download not completed [{http_timeout}]")

    try:
        document = None
        if request.driver.lower() == "pdfact":
            parser = PdfactParser(settings.pdfact_url)
            document = parser.parse(filename=request.url, unit=request.unit, roles=request.roles)
        elif request.driver.lower() == "pymupdf":
            parser = PymupdfParser()
            document = parser.parse(filename=file_path)
    except RequestException as e:
        logger.exception(f"Error while connecting to pdfact. {str(e)}", exc_info=True)
        raise HTTPException(status_code=503, detail="The pdfact service is not reachable")
    except Exception as err:
        logger.exception(f"Error while parsing file. {str(err)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Error while parsing file")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
    return document
