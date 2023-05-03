import logging

import orjson
from sanic import Sanic, response

from reconciliation_server.query import handle_incoming_queries
from reconciliation_server.service import get_service_document

app = Sanic("mp_reconciliation", dumps=orjson.dumps)
debug_mode = True

if debug_mode:
    LOGLEVEL = logging.DEBUG
else:
    LOGLEVEL = logging.ERROR

logging.basicConfig(format="[%(asctime)s] [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)",
                    level=LOGLEVEL)

log = logging.getLogger("mp_reconciliation")


@app.route("/reconcile", methods=["GET", "POST"])
async def reconcile(req) -> response.HTTPResponse:
    if "queries" not in req.args and req.method != "POST":
        return await get_service_document(req)

    return await handle_incoming_queries(req)
