import yaml
from small_asc.client import Solr

config: dict = yaml.safe_load(open('configuration.yml', 'r'))

solr_url = config['solr']['server']

SolrConnection: Solr = Solr(solr_url)
