from sanic import response


async def get_service_document(req) -> response.HTTPResponse:
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
        "documentation": "",
        "logo": "",
    }
    return response.json(service_document)
