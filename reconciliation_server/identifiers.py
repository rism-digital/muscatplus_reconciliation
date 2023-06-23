import re
from typing import Optional

ID_SUB: re.Pattern = re.compile(r"(?:person|source|institution|subject)_(\d+)")
QUERY_ID_SUB: re.Pattern = re.compile(r"(?:people|sources|institutions)\/(?P<doc_id>\d+)")


def transform_solr_id(doc_id, doc_type) -> Optional[str]:
    """
    Transforms a Solr ID into a reconciliation service ID

    :param doc_id: The Solr document id
    :param doc_type: The Solr document type
    :return: An ID string, or None if it was not successful
    """
    if doc_type == "person":
        return re.sub(ID_SUB, r"people/\1", doc_id)
    elif doc_type == "source":
        return re.sub(ID_SUB, r"sources/\1", doc_id)
    elif doc_type == "institution":
        return re.sub(ID_SUB, r"institutions/\1", doc_id)
    elif doc_type == "subject":
        return re.sub(ID_SUB, r"subjects/\1", doc_id)
    else:
        return None


def transform_query_id(q_id: str) -> Optional[str]:
    """
    Transform an incoming Reconciliation service ID into a Solr ID.
    :param q_id: Query ID
    :return: A Solr ID string, or None if not successful.
    """
    doc_matcher: re.Match = re.match(QUERY_ID_SUB, q_id)
    if not doc_matcher:
        return None

    doc_num: str = doc_matcher["doc_id"]
    if "people" in q_id:
        return f"person_{doc_num}"
    elif "sources" in q_id:
        return f"source_{doc_num}"
    elif "institutions" in q_id:
        return f"institution_{doc_num}"
    else:
        return None


def get_identifier(request: "sanic.request.Request", viewname: str, **kwargs) -> str:
    """
    Takes a request object, parses it out, and returns a templated identifier suitable
    for use in an "id" field, including the incoming request information on host and scheme (http/https).

    :param request: A Sanic request object
    :param viewname: A string of the view for which we will retrieve the URL. Matches the function name in server.py.
    :param kwargs: A set of keywords matching the template formatting variables
    :return: A templated string
    """
    fwd_scheme_header = request.headers.get('X-Forwarded-Proto')
    fwd_host_header = request.headers.get('X-Forwarded-Host')

    scheme: str = fwd_scheme_header if fwd_scheme_header else request.scheme
    server: str = fwd_host_header if fwd_host_header else request.host

    return request.app.url_for(viewname, _external=True, _scheme=scheme, _server=server, **kwargs)