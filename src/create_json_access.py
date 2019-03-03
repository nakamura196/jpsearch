import json
from SPARQLWrapper import SPARQLWrapper

sparql = SPARQLWrapper(endpoint='https://jpsearch.go.jp/rdf/sparql', returnFormat='json')
sparql.setQuery("""
    SELECT DISTINCT count(?s) as ?c ?sourceInfoLabel ?sourceOrganizationLabel ?target WHERE {
    ?sourceInfo <http://schema.org/provider> ?sp .
    ?sp <http://www.w3.org/2000/01/rdf-schema#label>  ?sourceInfoLabel .
    ?sp <http://schema.org/sourceOrganization> ?so .
    ?so <http://www.w3.org/2000/01/rdf-schema#label>  ?sourceOrganizationLabel .
    ?s <https://jpsearch.go.jp/term/property#sourceInfo> ?sourceInfo .
    ?s <https://jpsearch.go.jp/term/property#accessInfo> ?accessInfo .
    ?accessInfo <http://schema.org/provider> ?provider .
    ?provider <http://www.w3.org/2000/01/rdf-schema#label> ?target .
    }
""")
results = sparql.query().convert()

map = {}

for obj in results["results"]["bindings"]:
    print(obj)

    c = int(obj["c"]["value"])
    sourceInfoLabel = obj["sourceInfoLabel"]["value"]
    sourceOrganizationLabel = obj["sourceOrganizationLabel"]["value"]
    target = ""
    if "type" in obj:
        type = obj["target"]["value"]

    if sourceOrganizationLabel not in map:
        map[sourceOrganizationLabel] = {}

    tmp = map[sourceOrganizationLabel]
    if sourceInfoLabel not in tmp:
        tmp[sourceInfoLabel] = {}

    tmp = tmp[sourceInfoLabel]
    tmp[type] = c

fw = open("../docs/data/accessInfo.json", 'w')
json.dump(map, fw, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
