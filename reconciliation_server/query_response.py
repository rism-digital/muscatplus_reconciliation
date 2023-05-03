import ypres


class QueryResponse(ypres.AsyncDictSerializer):
    qid = ypres.MethodField(label="id")
    name = ypres.StrField(attr="name_s")

    def get_qid(self, obj) -> str:
        return "person"



