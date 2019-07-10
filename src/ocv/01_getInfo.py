import json
from SPARQLWrapper import SPARQLWrapper
import csv

rows = []

sparql2 = SPARQLWrapper(
    endpoint='https://jpsearch.go.jp/rdf/sparql', returnFormat='json')
sparql2.setQuery("""
prefix rdf: <https://jpsearch.go.jp/term/type/>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix schema: <http://schema.org/>
prefix jps: <https://jpsearch.go.jp/term/property#>
select distinct ?s ?o2 ?id ?title where {
        ?s jps:sourceInfo ?o . 
        ?o schema:provider chname:歴史人物画像データベース .
        ?s jps:accessInfo ?a . 
        ?a schema:url ?o2 . 
        ?a jps:contentId ?id . 
        ?s jps:relatedLink ?l . 
        ?l schema:description ?title . 
        ?l jps:relationType <https://jpsearch.go.jp/term/role/関連.出典> . 
        }
""")
results2 = sparql2.query().convert()

row = ["URI", "URL", "ID", "TITLE"]
rows.append(row)

for row2 in results2["results"]["bindings"]:
    s = row2["s"]["value"]
    url = row2["o2"]["value"]
    id = row2["id"]["value"]
    title = row2["title"]["value"]

    row = [s, url, id, title]
    rows.append(row)

with open('01_list.csv', 'w') as f:
    writer = csv.writer(f, lineterminator='\n')  # 改行コード（\n）を指定しておく
    writer.writerows(rows)  # 2次元配列も書き込める
