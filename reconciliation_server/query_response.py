import re

import ypres

ID_SUB = re.compile(r"(?:person|source|institution|subject)_(\d+)")


class QueryResponse(ypres.AsyncDictSerializer):
    qid = ypres.MethodField(label="id")
    name = ypres.MethodField()
    qtype = ypres.MethodField(label="type")
    score = ypres.FloatField(attr="score")

    def get_qid(self, obj: dict) -> str:
        recid: str = obj["id"]
        obj_type: str = obj["type"]
        if obj_type == "person":
            return re.sub(ID_SUB, r"people/\1", recid)
        elif obj_type == "source":
            return re.sub(ID_SUB, r"sources/\1", recid)
        elif obj_type == "institution":
            return re.sub(ID_SUB, r"institutions/\1", recid)
        elif obj_type == "subject":
            return re.sub(ID_SUB, r"subjects/\1", recid)
        else:
            return "[unknown identifier]"

    def get_name(self, obj: dict) -> str:
        obj_type = obj.get("type")
        if obj_type == "person":
            date_statement = f" ({obj['date_statement_s']})" if "date_statement_s" in obj else ""
            name = f"{obj['name_s']}{date_statement}"

            return name
        elif obj_type == "institution":
            return obj["name_s"]
        elif obj_type == "source":
            smark: str = f" ({obj['shelfmark_s']})" if "shelfmark_s" in obj else ""
            return f"{obj['main_title_s']}{smark}"
        elif obj_type == "subject":
            return f"{obj['term_s']}"
        else:
            return "[Unknown]"

    def get_qtype(self, obj: dict) -> list:
        return [obj["type"].title()]
