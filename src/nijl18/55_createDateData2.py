import sys
import urllib
import json
import argparse
import urllib.request
import unicodedata
import collections
import os
import xml.etree.ElementTree as ET
import csv
from rdflib import URIRef, BNode, Literal, Graph
from rdflib.namespace import RDF, RDFS, FOAF, XSD
from rdflib import Namespace
import glob

collection = "azumakagami"

# ローカルJSONファイルの読み込み
with open('data/'+collection+'/data.json', 'r') as f:
    json_data = json.load(f)

manifest_map = {}

files = glob.glob("../../docs/data/"+collection+"/manifest/*.json")
for file in files:
    with open(file, 'r') as f:
        manifest = json.load(f)
        uri = manifest["@id"]
        canvases = manifest["sequences"][0]["canvases"]
        for canvas in canvases:
            manifest_map[canvas["@id"]] = uri
    

with open('../../docs/data/'+collection+'/manifest_d.json', 'r') as f:
    manifest = json.load(f)

count_b = 0

st = manifest["structures"]
map = {}
for s in st:
    date = s["label"].split("(")[1].split(")")[0]
    canvases = s["canvases"]
    if len(canvases) > 0:
        map[date] = canvases[0]
    else:
        count_b += 1

print("canvases = null\t"+str(count_b))

count_a = 0

for obj in json_data:
    date = obj["http://purl.org/dc/terms/date"][0]["@value"]
    if date in map:
        canvas = map[date]

        obj["http://purl.org/dc/terms/relation"] = [
            {
                "@id" : canvas
            }
        ]

        obj["http://purl.org/dc/terms/isPartOf"] = [
            {
                "@id": manifest_map[canvas].replace("/manifest/", "/tei_d/").replace(".json", ".xml")
            }
        ]
    else:
        count_a += 1

print("date not in map\t"+str(count_a))

fw = open('data/'+collection+'/data_canvas.json', 'w')
json.dump(json_data, fw, ensure_ascii=False, indent=4,
          sort_keys=True, separators=(',', ': '))
