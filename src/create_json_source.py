import rdflib
import rdfextras
import json
from SPARQLWrapper import SPARQLWrapper

names = ["sources_all", "sources"]
# names = ["sources"]

oms = ["国立国会図書館", "国立科学博物館", "国立公文書館"]

sparql = SPARQLWrapper(endpoint='https://jpsearch.go.jp/rdf/sparql', returnFormat='json')

for name in names:

    sparql.setQuery("""
        SELECT DISTINCT count(?s) as ?c ?sourceInfoLabel ?sourceOrganizationLabel ?type WHERE {
        ?sourceInfo <http://schema.org/provider> ?sp .
        ?sp <http://www.w3.org/2000/01/rdf-schema#label>  ?sourceInfoLabel .
        ?sp <http://schema.org/sourceOrganization> ?so .
        ?so <http://www.w3.org/2000/01/rdf-schema#label>  ?sourceOrganizationLabel .
        ?s <https://jpsearch.go.jp/term/property#sourceInfo> ?sourceInfo .
        optional { ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?type }
        }
    """)
    
    '''

    if name == "sources_all":
        sparql.setQuery("""
            SELECT DISTINCT count(?s) as ?c ?sourceInfoLabel ?sourceOrganizationLabel ?type WHERE {
            ?sourceInfo <http://schema.org/provider> ?sp .
            ?sp <http://www.w3.org/2000/01/rdf-schema#label>  ?sourceInfoLabel .
            ?sp <http://schema.org/sourceOrganization> ?so .
            ?so <http://www.w3.org/2000/01/rdf-schema#label>  ?sourceOrganizationLabel .
            ?s <https://jpsearch.go.jp/term/property#sourceInfo> ?sourceInfo .
            optional { ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?type }
            }
        """)


    elif name == "sources":
        sparql.setQuery("""
            SELECT DISTINCT count(?s) as ?c ?sourceInfoLabel ?sourceOrganizationLabel ?type WHERE {
            ?sourceInfo <http://schema.org/provider> ?sp .
            ?sp <http://www.w3.org/2000/01/rdf-schema#label>  ?sourceInfoLabel .
            ?sp <http://schema.org/sourceOrganization> ?so .
            ?so <http://www.w3.org/2000/01/rdf-schema#label>  ?sourceOrganizationLabel .
            filter (
                ?sourceOrganizationLabel != "国立国会図書館" &&
                ?sourceOrganizationLabel != "国立科学博物館" &&
                ?sourceOrganizationLabel != "国立公文書館"
            )
            ?s <https://jpsearch.go.jp/term/property#sourceInfo> ?sourceInfo .
            optional { ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?type }
            }
        """)

    '''

    results = sparql.query().convert()

    map = {}

    for obj in results["results"]["bindings"]:
        print(obj)

        c = int(obj["c"]["value"])
        sourceInfoLabel = obj["sourceInfoLabel"]["value"]

        sourceOrganizationLabel = obj["sourceOrganizationLabel"]["value"]

        if name == "sources" and sourceOrganizationLabel in oms:
            continue

        type = ""
        if "type" in obj:
            type = obj["type"]["value"]

        if sourceOrganizationLabel not in map:
            map[sourceOrganizationLabel] = {}

        tmp = map[sourceOrganizationLabel]
        if sourceInfoLabel not in tmp:
            tmp[sourceInfoLabel] = {}

        tmp = tmp[sourceInfoLabel]
        tmp[type.replace("https://jpsearch.go.jp/term/type/", "")] = c

    fw = open("../docs/data/" + name + ".json", 'w')
    json.dump(map, fw, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))

    data = {}
    data["name"] = "jpsearch"
    children = []
    data["children"] = children
    for org in map:
        databases = map[org]
        obj_org = {}
        children.append(obj_org)
        obj_org["name"] = org
        children_org = []
        obj_org["children"] = children_org

        for database in databases:
            types = databases[database]
            obj_db = {}
            children_org.append(obj_db)
            obj_db["name"] = database
            children_db = []
            obj_db["children"] = children_db

            for type in types:
                obj_type = {}
                children_db.append(obj_type)
                obj_type["name"] = type
                obj_type["value"] = types[type]

    fw = open("../docs/data/" + name + "_formated.json", 'w')
    json.dump(data, fw, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
