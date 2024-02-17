import hashlib
import logging
import os

import requests
from requests.exceptions import HTTPError
from requests.exceptions import Timeout
from flask import Flask, request

from parsing_service.implementation.parser_factory import parse_file
from parsing_service.logger import init_logger

logger = logging.getLogger(__name__)


def create_app():
    init_logger()
    app = Flask(__name__, instance_relative_config=True)
    app.resource_path = os.environ.get("RESOURCE_PATH", "/tmp")
    try:
        os.mkdir(app.resource_path)
    except FileExistsError:
        pass

    @app.route("/extract-text", methods=["POST"])
    def text_extract_endpoint():

        logger.info("Received parse request")

        if not request.json:
            logger.warning("No json found in request")
            return {"message": "No json found in request", "code": 422, "type": "Unprocessable Entity"}, 422
        if not request.json.get("url"):
            logger.warning("No file found in request")
            return {"message": "No url found in request", "code": 422, "type": "Unprocessable Entity"}, 422
        if not request.json.get("mime_type"):
            logger.warning("No mime_type found in request")
            return {"message": "No mime_type found in request", "code": 422, "type": "Unprocessable Entity"}, 422
        
        if request.json.get("mime_type") != 'application/pdf':
            mime = request.json.get("mime_type")
            logger.warning(f"Unsupported format [{mime}]")
            return {"message": f"Unsupported mime type. Expecting application/pdf received [{mime}]", "code": 422, "type": "Unprocessable Entity"}, 422
        
        filename = hashlib.sha256(request.json.get("url").encode()).hexdigest()
        extension = request.json.get("mime_type").split("/")[-1]
        filename = f"{filename}.{extension}"
        logger.info(f"Parsing {filename}")
        
        try:
            resp = requests.get(request.json.get("url"), allow_redirects=True, timeout=120)

            resp.raise_for_status()

            open(os.path.join(app.resource_path, filename), 'wb').write(resp.content)
        except HTTPError as http_err:
            logger.exception("Error while downloading file", exc_info=True)
            return {"message": f"Error while downloading file [{http_err}]", "code": 500, "type": "Internal Server Error"}, 500
        except Timeout as http_timeout:
            logger.exception("Timeout while downloading file", exc_info=True)
            return {"message": f"File download not completed [{http_timeout}]", "code": 500, "type": "Internal Server Error"}, 500
        except Exception as requestError:
            logger.exception("Error while downloading file", exc_info=True)
            return {"message": "Error while saving file", "code": 500, "type": "Internal Server Error"}, 500
        
        try:
            doc_parsed = parse_file(os.path.join(app.resource_path, filename), extension)
            os.remove(os.path.join(app.resource_path, filename))
        except ValueError as ve:
            logger.exception("Unsupported file type", exc_info=True)
            return {"message": "Unsupported file type", "code": 422, "type": "Unprocessable Entity"}, 422
        except Exception as err:
            logger.exception("Error while parsing file", exc_info=True)
            return {"message": "Error while parsing file", "code": 500, "type": "Internal Server Error"}, 500
        
        logger.info(f"Parse done for file {filename}")
        
        return {"status": "ok", "content": [chunk.to_dict() for chunk in doc_parsed]}, 200

    return app
