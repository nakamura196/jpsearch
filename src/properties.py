import json
from SPARQLWrapper import SPARQLWrapper

def get(q):

    import urllib.parse
    import requests

    url = "https://jpsearch.go.jp/rdf/sparql?query="+urllib.parse.quote(q)+"&format=json&output=json&results=json"

    # print(url)

    r = requests.get(url)
    # 結果はJSON形式なのでデコードする

    # print(r)

    results = json.loads(r.text)

    return results


sparql = SPARQLWrapper(endpoint='https://jpsearch.go.jp/rdf/sparql', returnFormat='json')
q = ("""
    select distinct ?v where {?s ?v ?o . ?s <https://jpsearch.go.jp/term/property#sourceInfo> ?k } limit 50
""")
# results = sparql.query().convert()

results = get(q)

properties = []

for obj in results["results"]["bindings"]:
    p = obj["v"]["value"]
    properties.append(p)

map = {}

'''
properties = [
    "rdf:type",
    "rdfs:label",
    "schema:name",
    "schema:contributor",
    "schema:creator",
    "schema:publisher",
    "schema:temporal",
    "schema:dateCreated",
    "schema:datePublished",
    "schema:spatial",
    "schema:about",
    "schema:identifier",
    "schema:isbn",
    "schema:issn",
    "schema:inLanguage",
    "schema:image",
    # "schema:description",
    "schema:isPartOf",
    "schema:relatedLink",
    "jps:agential",
    "jps:temporal",
    "jps:spatial",
    "jps:partOf",
    "jps:relatedLink",
    "jps:accessInfo",
    "jps:sourceInfo"
]
'''

for v in properties:

    try:
        print(v)

        map[v] = {}

        sparql2 = SPARQLWrapper(endpoint='https://jpsearch.go.jp/rdf/sparql', returnFormat='json')
        q2 = ("""
            prefix rdf: <https://jpsearch.go.jp/term/type/>
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            prefix schema: <http://schema.org/>
            prefix jps: <https://jpsearch.go.jp/term/property#>
            select distinct count(?s) as ?c ?o where {?s <""" + v + """> ?o } order by desc(?c) limit 20
        """)
        # results2 = sparql2.query().convert()
        results2 = get(q2)

        for row2 in results2["results"]["bindings"]:
            c = int(row2["c"]["value"])
            if c > 1:
                map[v][row2["o"]["value"]] = c

        print(map[v])
    except:
        continue

fw = open("../docs/data/properties.json", 'w')
json.dump(map, fw, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
