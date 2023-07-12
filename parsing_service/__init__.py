import hashlib
import logging
import os

import requests
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
        filename = hashlib.sha256(request.json.get("url").encode()).hexdigest()
        extension = request.json.get("mime_type").split("/")[-1]
        filename = f"{filename}.{extension}"
        try:
            resp = requests.get(request.json.get("url"), allow_redirects=True)
            open(os.path.join(app.resource_path, filename), 'wb').write(resp.content)
        except Exception:
            logger.exception("Error while saving file")
            return {"message": "Error while saving file", "code": 500, "type": "Internal Server Error"}, 500
        try:
            doc_parsed = parse_file(os.path.join(app.resource_path, filename), extension)
            os.remove(os.path.join(app.resource_path, filename))
        except ValueError:
            logger.exception("Unsupported file type")
            return {"message": "Unsupported file type", "code": 422, "type": "Unprocessable Entity"}, 422
        except Exception:
            logger.exception("Error while parsing file")
            return {"message": "Error while parsing file", "code": 500, "type": "Internal Server Error"}, 500
        logger.info(f"Parse done for file {filename}")
        return {"status": "ok", "content": [chunk.to_dict() for chunk in doc_parsed]}, 200

    return app
