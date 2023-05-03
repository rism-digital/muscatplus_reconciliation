from collections import defaultdict
from typing import Optional

import orjson
from sanic import response
from small_asc.client import Solr

from reconciliation_server.query_response import QueryResponse


async def handle_incoming_queries(req) -> response.HTTPResponse:
    if req.method == "POST":
        res = await handle_post_query(req)
    else:
        res = await handle_get_query(req)

    if not res:
        return response.text("Bad response", status=500)

    print(res)

    return response.json(res)


async def handle_get_query(req) -> Optional[dict]:
    qdocs: Optional[str] = req.args.get("queries")
    if not qdocs:
        return None

    parsed_q: dict = orjson.loads(qdocs)

    return await _assemble_response(parsed_q)


async def handle_post_query(req) -> dict:
    qdocs = req.json
    return await _assemble_response(qdocs)


async def _assemble_response(qdocs: dict) -> dict:
    resp = defaultdict(dict)
    for qnum, qdoc in qdocs.items():
        resp[qnum]["result"] = await _do_query(qdoc)

    return dict(resp)


async def _do_query(qdoc) -> list:
    qstr = qdoc.get("query", "")
    type_filt = qdoc.get("type", [])

    solr_q = qstr
    fq = [f"type:{s.lower()}" for s in type_filt]

    s = Solr("http://localhost:8983/solr/muscatplus_live/")
    resp = await s.search({"query": solr_q, "filter": fq}, cursor=True)

    print(resp.hits)

    return await QueryResponse(resp,
                               many=True).data

