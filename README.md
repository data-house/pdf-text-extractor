# PDF Text extraction service for Data House







# PRE-REQUISITES

## Local-environment

Before running the project, you need to have installed Python > 3.8.0 and pip.

Install all the required dependencies

```
pip install -r requirements.txt
```

## Docker-environment

Before running the project, you need to have installed Docker and Docker-compose.

# Running the project

## Local-environment

To run the project, just run the following command:

```
 python.exe -m flask --app parsing_service run
```

## Docker-environment

A [docker-compose.yaml](docker-compose.yaml)docker-compose file is provided to run the project in a docker environment.

# Usage
The following endpoint is available:
```http
POST /extract-text
```
The body of the request must be a JSON with the following structure:
```json
{
    "url": "string",
    "mime_type": "string"
}
```
The response will be a JSON with the following structure:
```json
{
    "status": "string",
    "content": {
      "text": "string",
      "metadata": "object"
    }
}
```