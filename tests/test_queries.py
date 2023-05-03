import pytest
import json
from urllib.parse import quote_plus

from reconciliation_server.server import app


def test_basic_get_query():
    q_doc = {"q0": {"query": "Beethoven", "type": "Person"}}
    q_str: str = json.dumps(q_doc)
    encoded_q = quote_plus(q_str)

    req, resp = app.test_client.get(f"/reconcile/?queries={encoded_q}")

    assert resp.status == 200


def test_basic_post_query():
    q_doc = {"q0": {"query": "Beethoven", "type": "Person"}}
    q_str: str = json.dumps(q_doc)
    encoded_q = f"{q_str}"

    req, resp = app.test_client.post(f"/reconcile/", json=encoded_q)
    assert resp.status == 200
