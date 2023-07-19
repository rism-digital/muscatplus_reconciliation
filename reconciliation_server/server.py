import logging

import orjson
import yaml
from sanic import Sanic, response, Blueprint

from reconciliation_server.query import handle_incoming_queries, handle_preview_query, handle_entity_suggest_query
from reconciliation_server.service import get_service_document


config: dict = yaml.safe_load(open('configuration.yml', 'r'))
debug_mode: bool = config['common']['debug']
version_string: str = config['common']['version']
release: str = ""

if debug_mode is False:
    import sentry_sdk
    from sentry_sdk.integrations.sanic import SanicIntegration
    sentry_sdk.init(
        dsn=config["sentry"]["dsn"],
        integrations=[SanicIntegration()],
        environment=config["sentry"]["environment"],
        release=f"muscatplus_reconciliation@{release}"
    )


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

reconcile_bp: Blueprint = Blueprint("reconciliation", url_prefix="/reconciliation")
app.blueprint(reconcile_bp)


@reconcile_bp.route("/", methods=["GET"])
async def service(req) -> response.HTTPResponse:
    return await get_service_document(req, config)


@reconcile_bp.route("/reconcile", methods=["GET", "POST"])
async def reconcile(req) -> response.HTTPResponse:
    # Legacy services only differentiate the service response
    # if "queries" are not in the URL, or it's not a POST request.
    if "queries" not in req.args and req.method != "POST":
        return await get_service_document(req, config)

    return await handle_incoming_queries(req, config)


@reconcile_bp.route("/suggest/entity", methods=["GET"])
async def suggest(req) -> response.HTTPResponse:
    return await handle_entity_suggest_query(req, config)


@reconcile_bp.route("/preview", methods=["GET"])
async def preview(req) -> response.HTTPResponse:
    return await handle_preview_query(req, config)
