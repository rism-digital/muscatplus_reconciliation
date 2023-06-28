from collections import defaultdict
from typing import Optional

import orjson
from sanic import response
from small_asc.client import Results

from reconciliation_server.identifiers import transform_query_id
from reconciliation_server.query_response import QueryResponse, html_preview, SuggestResponse
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
        "sort": sort
    }

    if limit:
        json_api_q["limit"] = limit

    resp = await SolrConnection.search(json_api_q, handler="/query")
    return await QueryResponse(resp, many=True).data


async def handle_preview_query(req, cfg) -> response.HTTPResponse:
    doc_id: Optional[str] = req.args.get("id")
    if not doc_id:
        return response.text("ID argument was not supplied.", status=400)

    # transform ID to Solr ID
    solr_id: Optional[str] = transform_query_id(doc_id)
    if not solr_id:
        return response.text("Could not determine the ID from the incoming request", status=400)

    resp: Optional[dict] = await SolrConnection.get(solr_id)
    if not resp:
        return response.text(f"Document with ID {doc_id} was not found", status=404)

    formatted_resp: str = html_preview(resp)
    return response.html(formatted_resp)


async def handle_entity_suggest_query(req, cfg) -> response.HTTPResponse:
    prefix = req.args.get("prefix")
    if not prefix:
        return response.text("Prefix argument was not supplied.", status=400)

    fl = ["name_s",
          "main_title_s",
          "shelfmark_s",
          "date_statement_s",
          "record_type_s",
          "source_type_s",
          "siglum_s",
          "city_s",
          "term_s",
          "type",
          "id",
          "score"]

    filters = ["type:source OR type:person OR type:institution"]

    resp: Optional[Results] = await SolrConnection.search({
        "query": prefix,
        "limit": 20,
        "fields": fl,
        "filter": filters,
        "params": {
            "bq": ["record_type_s:item^0",
                   "record_type_s:collection^100",
                   "type:person^50",
                   "type:institution^50"]
        }
    }, handler="/query")

    results: list[dict] = await SuggestResponse(resp, many=True).data
    return response.json({"result": results})
