import json
from SPARQLWrapper import SPARQLWrapper

'''
sparql = SPARQLWrapper(endpoint='https://jpsearch.go.jp/rdf/sparql', returnFormat='json')
sparql.setQuery("""
    select distinct ?v where {?s ?v ?o . ?s <https://jpsearch.go.jp/term/property#sourceInfo> ?k } limit 50
""")
results = sparql.query().convert()
'''

map = {}

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

for v in properties:

    print(v)

    map[v] = {}

    sparql2 = SPARQLWrapper(endpoint='https://jpsearch.go.jp/rdf/sparql', returnFormat='json')
    sparql2.setQuery("""
        prefix rdf: <https://jpsearch.go.jp/term/type/>
        prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix schema: <http://schema.org/>
        prefix jps: <https://jpsearch.go.jp/term/property#>
        select distinct count(?s) as ?c ?o where {?s """ + v + """ ?o } order by desc(?c) limit 20
    """)
    results2 = sparql2.query().convert()

    for row2 in results2["results"]["bindings"]:
        c = int(row2["c"]["value"])
        if c > 1:
            map[v][row2["o"]["value"]] = c

    print(map[v])

fw = open("../docs/data/properties.json", 'w')
json.dump(map, fw, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
