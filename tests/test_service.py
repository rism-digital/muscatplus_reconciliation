from reconciliation_server.server import app


def test_get_service_document():
    req, resp = app.test_client.get("/reconciliation/")
    js_resp = resp.json

    assert resp.status == 200  # noqa: S101
    assert js_resp["versions"] == ["0.2"]  # noqa: S101
