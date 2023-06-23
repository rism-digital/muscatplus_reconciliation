from sanic import response
from reconciliation_server.identifiers import get_identifier


async def get_service_document(req, cfg: dict) -> response.HTTPResponse:
    service_document: dict = {
        "versions": [
            "0.2"
        ],
        "name": "RISM Online Reconciliation Service",
        "identifierSpace": "https://rism.online/",
        "schemaSpace": "https://rism.online/api/v1#",
        "defaultTypes": [{
                "id": "Person",
                "name": "People authorities"
            }, {
                "id": "Institution",
                "name": "Institution authorities",
            }, {
                "id": "Source",
                "name": "Source authorities"
            }, {
                "id": "Subject",
                "name": "Subject authorities"
            }],
        "documentation": f"RISM Online Reconciliation Service ({cfg['common']['version']})",
        "suggest": {
            "entity": {
                "service_path": "/suggest/entity",
                "service_url": get_identifier(req, "reconciliation.service")
            }
        },
        "view": {
            "url": "https://rism.online/{{id}}"
        },
        "preview": {
            "height": 100,
            "width": 400,
            "url": f"{get_identifier(req, 'reconciliation.preview')}?id={{{{id}}}}"
        },
        "logo": "",
    }
    return response.json(service_document)
