from typing import Optional

import ypres

from reconciliation_server.identifiers import transform_solr_id


def _format_name(obj: dict) -> Optional[str]:
    obj_type = obj.get("type")
    if obj_type == "person":
        date_statement = f" ({obj['date_statement_s']})" if "date_statement_s" in obj else ""
        name = f"{obj['name_s']}{date_statement}"
        return name
    elif obj_type == "institution":
        return f"{obj['name_s']}"
    elif obj_type == "source":
        smark: str = f"{obj['shelfmark_s']}: " if "shelfmark_s" in obj else ""
        sigl: str = f"{obj['siglum_s']} " if "siglum_s" in obj else ""
        title: str = f"{obj['main_title_s']}" if "main_title_s" in obj else ""
        return f"{sigl}{smark}{title}"
    elif obj_type == "subject":
        return f"{obj['term_s']}"
    else:
        return None


def _format_desc(obj: dict) -> Optional[str]:
    if obj['type'] == "source":
        return f"{obj['type']}: {obj.get('record_type_s')}, {obj.get('source_type_s')}"
    elif obj['type'] == "institution":
        city = f", {obj['city_s']}" if 'city_s' in obj else ""
        sigl: str = f" ({obj['siglum_s']})" if "siglum_s" in obj else ""
        return f"{obj['type']}{city}{sigl}"
    else:
        return obj["type"]


class QueryResponse(ypres.AsyncDictSerializer):
    qid: str = ypres.MethodField(label="id")
    name: str = ypres.MethodField()
    qtype: list = ypres.MethodField(label="type")
    description: str = ypres.MethodField()
    score: float = ypres.FloatField(attr="score")

    def get_qid(self, obj: dict) -> str:
        recid: str = obj["id"]
        obj_type: str = obj["type"]
        return transform_solr_id(recid, obj_type) or "[Unknown Type]"

    def get_name(self, obj: dict) -> str:
        return _format_name(obj) or "[Unknown name]"

    def get_qtype(self, obj: dict) -> list:
        return [obj["type"].title()]

    def get_description(self, obj: dict) -> str:
        return _format_desc(obj)


HTML_TMPL = """
<html>
   <head><meta charset="utf-8" /></head>
   <style type="text/css">
        body {{
            font-family: "Helvetica", sans-serif;
        }}
   </style>
   <body>
      <h3>{doc_title}</h3>
      <a href="https://rism.online/{doc_id}" target="_blank">View on RISM Online</a>
      <p>{doc_desc}</p>
   </body>
</html>
"""


def html_preview(obj) -> str:
    doc_title: str = _format_name(obj) or "[Unknown name]"
    doc_desc: str = _format_desc(obj) or "[No description]"
    doc_id: str = transform_solr_id(obj["id"], obj["type"]) or "/"

    return HTML_TMPL.format(doc_title=doc_title,
                            doc_desc=doc_desc,
                            doc_id=doc_id)


class SuggestResponse(ypres.AsyncDictSerializer):
    qid: str = ypres.MethodField(label="id")
    name: str = ypres.MethodField()
    description: str = ypres.MethodField()

    def get_qid(self, obj: dict) -> str:
        recid: str = obj["id"]
        obj_type: str = obj["type"]
        return transform_solr_id(recid, obj_type) or "[Unknown Type]"

    def get_name(self, obj: dict) -> str:
        return _format_name(obj) or "[Unknown name]"

    def get_description(self, obj: dict) -> str:
        return _format_desc(obj)
