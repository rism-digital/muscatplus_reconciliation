import json
from urllib.parse import quote_plus

from reconciliation_server.server import app


def test_basic_get_query():
    q_doc = {"q0": {"query": "Beethoven", "type": "Person"}}
    q_str: str = json.dumps(q_doc)
    encoded_q = quote_plus(q_str)

    req, resp = app.test_client.get(
        f"/reconciliation/reconcile?queries={encoded_q}"
    )

    assert resp.status == 200  # noqa: S101


def test_basic_post_query():
    q_doc = {"q0": {"query": "Beethoven", "type": "Person"}}
    q_str: str = json.dumps(q_doc)

    req, resp = app.test_client.post(
        "/reconciliation/reconcile",
        data={"queries": q_str},
    )
    assert resp.status == 200  # noqa: S101
