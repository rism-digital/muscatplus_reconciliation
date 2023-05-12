import logging

import orjson
import yaml
from sanic import Sanic, response

from reconciliation_server.query import handle_incoming_queries
from reconciliation_server.service import get_service_document


config: dict = yaml.safe_load(open('configuration.yml', 'r'))
debug_mode: bool = config['common']['debug']
version_string: str = config['common']['version']
release: str = ""

app = Sanic("mp_reconciliation", dumps=orjson.dumps)
app.config.FORWARDED_SECRET = config['common']['secret']
app.ctx.config = config

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
        return await get_service_document(req, config)

    return await handle_incoming_queries(req, config)
