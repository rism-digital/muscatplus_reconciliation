import yaml
from small_asc.client import Solr

with open("configuration.yml") as cfile:
    config: dict = yaml.safe_load(cfile)

solr_url = config["solr"]["server"]
SolrConnection: Solr = Solr(solr_url, expand_json_fields=True)
