import json
from SPARQLWrapper import SPARQLWrapper

flg = True

page = 0

map = {}

while (flg):

    print(page)

    sparql = SPARQLWrapper(endpoint='https://jpsearch.go.jp/rdf/sparql', returnFormat='json')
    sparql.setQuery("""
        SELECT DISTINCT ?url ?label ?provider_label WHERE {
      ?s rdfs:label ?label .
      ?s jps:accessInfo ?ai. ?ai schema:url ?url . ?url rdf:type <http://iiif.io/api/presentation/2#Manifest> .
      ?ai schema:provider ?provider . ?provider rdfs:label ?provider_label .
    } limit 10000 offset """ + str(10000 * page) + """
    """)

    results = sparql.query().convert()

    if len(results["results"]["bindings"]) == 0:
        flg = False

    page += 1

    for obj in results["results"]["bindings"]:
        manifest = obj["url"]["value"]
        label = obj["label"]["value"]
        attribution = obj["provider_label"]["value"]

        if attribution not in map:
            map[attribution] = []

        manifest_obj = {}
        manifest_obj["@id"] = manifest
        manifest_obj["@type"] = "sc:Manifest"
        manifest_obj["label"] = label

        map[attribution].append(manifest_obj)

collection = {}
collection["@context"] = "http://iiif.io/api/presentation/2/context.json"
collection["@id"] = "https://nakamura196.github.io/jpsearch/data/collection.json"
collection["@type"] = "sc:Collection"
collection["label"] = "Japan Search IIIF Collection"

collections = []

collection["collections"] = collections

for attribution in map:
    all = {}
    all["@context"] = "http://iiif.io/api/presentation/2/context.json"
    all["@id"] = "https://nakamura196.github.io/jpsearch/data/collections/" + attribution + ".json"
    all["@type"] = "sc:Collection"
    all["manifests"] = map[attribution]

    c = {}
    collections.append(c)
    c["@id"] = all["@id"]
    c["@type"] = "sc:Collection"
    c["label"] = attribution

    fw = open("../docs/data/collections/" + attribution + ".json", 'w')
    json.dump(all, fw, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))

fw2 = open("../docs/data/collection.json", 'w')
json.dump(collection, fw2, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
