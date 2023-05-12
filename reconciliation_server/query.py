from collections import defaultdict
from typing import Optional

import orjson
from sanic import response

from reconciliation_server.query_response import QueryResponse
from reconciliation_server.solr import SolrConnection


async def handle_incoming_queries(req, cfg: dict) -> response.HTTPResponse:
    if req.method == "POST":
        res = await handle_post_query(req, cfg)
    else:
        res = await handle_get_query(req, cfg)

    if not res:
        return response.text("Bad response", status=500)

    return response.json(res, headers={"Access-Control-Allow-Origin": "*"})


async def handle_get_query(req, cfg: dict) -> Optional[dict]:
    qdocs: Optional[str] = req.args.get("queries")
    if not qdocs:
        return None

    parsed_q: dict = orjson.loads(qdocs)

    return await _assemble_response(parsed_q, cfg)


async def handle_post_query(req, cfg: dict) -> Optional[dict]:
    if "queries" not in req.form:
        return None

    qdocs: str = req.form.get("queries")
    parsed_q: dict = orjson.loads(qdocs)

    print(parsed_q)
    return await _assemble_response(parsed_q, cfg)


async def _assemble_response(qdocs: dict, cfg: dict) -> dict:
    resp = defaultdict(dict)
    for qnum, qdoc in qdocs.items():
        resp[qnum]["result"] = await _do_query(qdoc, cfg)

    return dict(resp)


async def _do_query(qdoc, cfg: dict) -> list:
    qstr = qdoc.get("query", "")
    type_filt = qdoc.get("type")
    limit = qdoc.get("limit")
    properties = qdoc.get("properties", [])

    solr_q = qstr
    fq = []
    if type_filt:
        fq.append(f"type:{type_filt.lower()}")
        if type_filt.lower() == "source":
            # Only get the "book" records for sources
            fq.append("is_collection_record_b:true")
    else:
        fq.append("type:person OR type:institution OR type:source OR type:subject")

    if properties:
        for prop in properties:
            if prop['pid'] == "siglum":
                fq.append(f"siglum_s:{prop['v']}")

    fl = ["name_s",
          "main_title_s",
          "shelfmark_s",
          "date_statement_s",
          "term_s",
          "type",
          "id",
          "score"]

    sort = "score desc"

    json_api_q = {
        "query": solr_q,
        "filter": fq,
        "fields": fl,
        "sort": sort,
    }

    if limit:
        json_api_q["limit"] = limit

    resp = await SolrConnection.search(json_api_q, handler="/query")

    ret = await QueryResponse(resp, many=True).data

    print(ret)

    return ret

