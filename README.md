# PDF Text extraction service for Data House

Extract text from PDFs keeping page information.

## Getting started

_to be documented_

## Usage

The PDF Text Extract service expose a web application on port `5000`. The available API receive a PDF file via a URL and return the extracted text as a JSON response.

The exposed service is unauthenticated therefore consider exposing it only within a trusted network. If you plan to make it available publicly consider adding a reverse proxy with authentication in front.

### Text extraction endpoint

The service expose only one endpoint `/extract-text` that accepts a `POST` request
with the following input as a `json` body:

- `url` the URL of the PDF file to process
- `mime_type` the mime type of the file (it is expected to be `application/pdf`)

> **warning** The processing is performed synchronously


The response will be a JSON containing:

- `status` the status of the operation. Usually `ok`.
- `content` a list of objects describing the chunked content with the page reference. Each object contains a `text` property with the part of the PDF text and a `metadata` object with the `page_number` property representing the page of the PDF from which the `text` was extracted.

The following code block shows a possible output:

```json
{
  "status": "ok",
  "content": [
    {
      "text": "This is a test PDF to be used as input in unit tests",
      "metadata": {
        "page_number": 1
      }
    }
  ]
}
```

### Error handling

The service can return the following errors

| code | message | description |
|------|---------|-------------|
| `422` | No url found in request | In case the `url` field in the request is missing |
| `422` | No mime_type found in request | In case the `mime_type` field in the request is missing |
| `422` | Unsupported file type | In case the file is not a PDF |
| `500` | Error while saving file | In case it was not possible to download the file from the specified URL |
| `500` | Error while parsing file | In case it was not possible to open the file after download |


The body of the response can contain a JSON with the following fields:

- `code` the error code
- `message` the error description
- `type` the type of the error

```json
{
  "code": 500,
  "message": "Error while parsing file",
  "type": "Internal Server Error",
}
```

## Development

The PDF text extract service is built using [Flask](https://flask.palletsprojects.com/) on Python 3.9.

Given the selected stack the development requires:

- [Python 3.9](https://www.python.org/) with PIP
- [Docker](https://www.docker.com/) (optional) to test the build


Install all the required dependencies:

```bash
pip install -r requirements.txt
```

Run the local development application using:

```bash
python -m flask --app parsing_service run
```


### Testing

_to be documented_


## Contributing

Thank you for considering contributing to the PDF text extract service! The contribution guide can be found in the [CONTRIBUTING.md](./.github/CONTRIBUTING.md) file.


## Supporters

The project is supported by [OneOff-Tech (UG)](https://oneofftech.de) and [Oaks S.r.l](https://www.oaks.cloud/).

<p align="left"><a href="https://oneofftech.de" target="_blank"><img src="https://raw.githubusercontent.com/OneOffTech/.github/main/art/oneofftech-logo.svg" width="200"></a></p>

<p align="left"><a href="https://www.oaks.cloud" target="_blank"><img src="https://raw.githubusercontent.com/data-house/pdf-text-extractor/main/.github/art/oaks-logo.svg" width="200"></a></p>


## Security Vulnerabilities

If you discover a security vulnerability within PDF Text Extract, please send an e-mail to OneOff-Tech team via [security@oneofftech.xyz](mailto:security@oneofftech.xyz). All security vulnerabilities will be promptly addressed.
