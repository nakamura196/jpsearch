import json
from SPARQLWrapper import SPARQLWrapper
import csv

rows = []

page = 0

flg = True

row = ["URI", "LABEL", "V", "P"]
rows.append(row)

d = 10000

while(flg):

        print(page+1)

        sparql2 = SPARQLWrapper(
        endpoint='https://jpsearch.go.jp/rdf/sparql', returnFormat='json')
        sparql2.setQuery("""
        prefix rdf: <https://jpsearch.go.jp/term/type/>
        prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix schema: <http://schema.org/>
        prefix jps: <https://jpsearch.go.jp/term/property#>
        select distinct ?s ?label ?part {
                ?s rdfs:label ?label . 
                ?s schema:isPartOf ?part . 
                ?s jps:sourceInfo ?info . 
                ?info schema:provider chname:絵入源氏物語 . 
                } limit """+str(d)+""" offset """+str(page * d)+"""
        """)
        results2 = sparql2.query().convert()

        if len(results2["results"]["bindings"]) == 0:
                flg = False

        for row2 in results2["results"]["bindings"]:
                s = row2["s"]["value"]
                label = row2["label"]["value"]
                part = row2["part"]["value"]
                # print(part)
                part = part.split("v")
                if len(part) < 2:
                        continue
                part = part[1].split("p")
                v = part[0]
                p = str(int(part[1]))

                row = [s, label, v, p]
                rows.append(row)

        page += 1

with open('01_list.csv', 'w') as f:
    writer = csv.writer(f, lineterminator='\n')  # 改行コード（\n）を指定しておく
    writer.writerows(rows)  # 2次元配列も書き込める
