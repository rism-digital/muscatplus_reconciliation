import sanic

SOLR_TO_RECONCILIATION_PREFIX: dict[str, str] = {
    "person": "people",
    "source": "sources",
    "institution": "institutions",
    "subject": "subjects",
}
RECONCILIATION_TO_SOLR_PREFIX: dict[str, str] = {
    reconciliation_prefix: solr_prefix
    for solr_prefix, reconciliation_prefix in SOLR_TO_RECONCILIATION_PREFIX.items()
}


def strip_prefix(ident: str) -> str:
    # Returns the last component of a solr document identifier,
    # the actual ID number.
    return ident.split("_")[-1]


def transform_solr_id(doc_id, doc_type) -> str | None:
    """
    Transforms a Solr ID into a reconciliation service ID

    :param doc_id: The Solr document id
    :param doc_type: The Solr document type
    :return: An ID string, or None if it was not successful
    """
    ident: str = strip_prefix(doc_id)
    prefix = SOLR_TO_RECONCILIATION_PREFIX.get(doc_type)
    return f"{prefix}/{ident}" if prefix is not None else None


def transform_query_id(q_id: str) -> str | None:
    """
    Transform an incoming Reconciliation service ID into a Solr ID.
    :param q_id: Query ID
    :return: A Solr ID string, or None if not successful.
    """
    parts = q_id.strip("/").split("/")
    if len(parts) != 2:
        return None

    collection, doc_id = parts
    doc_type = RECONCILIATION_TO_SOLR_PREFIX.get(collection)
    if not doc_type or not doc_id or not doc_id.isdigit():
        return None

    return f"{doc_type}_{doc_id}"


def get_identifier(request: sanic.Request, viewname: str, **kwargs) -> str:
    """
    Takes a request object, parses it out, and returns a templated identifier suitable
    for use in an "id" field, including the incoming request information on host and scheme (http/https).

    :param request: A Sanic request object
    :param viewname: A string of the view for which we will retrieve the URL. Matches the function name in server.py.
    :param kwargs: A set of keywords matching the template formatting variables
    :return: A templated string
    """
    fwd_scheme_header = request.headers.get("X-Forwarded-Proto")
    fwd_host_header = request.headers.get("X-Forwarded-Host")

    scheme: str = fwd_scheme_header if fwd_scheme_header else request.scheme
    server: str = fwd_host_header if fwd_host_header else request.host

    return request.app.url_for(
        viewname, _external=True, _scheme=scheme, _server=server, **kwargs
    )
