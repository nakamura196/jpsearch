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
import glob

'''
collection = "azumakagami"
col_id = "200005040"

collection = "mizukagami"
col_id = "200008370"

collection = "okagami"
col_id = "200019161"

collection = "imakagami"
col_id = "200017351"

collection = "masukagami"
col_id = "200010997"

'''
collection = "azumakagami"
col_id = "200005040"

url = "https://kotenseki.nijl.ac.jp/biblio/"+col_id+"/manifest"

# ----

request = urllib.request.Request(url)
response = urllib.request.urlopen(request)

response_body = response.read().decode("utf-8")
temp = json.loads(response_body)

data = temp

manifest = "https://nakamura196.github.io/jpsearch/data/"+collection+"/manifest.json"
data["@id"] = manifest
data["label"] = data["label"]

data["service"] = {
    "@context": "http://iiif.io/api/search/0/context.json",
    "@id": "https://iiif.dl.itc.u-tokyo.ac.jp/api/iiif-search/get.php/https://nakamura196.github.io/jpsearch/data/"+collection+"/tei.xml",
    "profile": "http://iiif.io/api/search/0/search",
    "label": "Search within this manifest"
}

st = []
data["structures"] = st

files = glob.glob("../../docs/data/"+collection+"/manifest/*.json")

for file in sorted(files):

    # ローカルJSONファイルの読み込み
    with open(file, 'r') as f:
        e = json.load(f)

    for s in e["structures"]:
        st.append(s)

fw = open("../../docs/data/"+collection+"/manifest.json", 'w')
json.dump(data, fw, ensure_ascii=False, indent=4,
          sort_keys=True, separators=(',', ': '))
