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

# collection = "masukagami"

collection = "imakagami"

# ローカルJSONファイルの読み込み
with open('data/'+collection+'/manifest.json', 'r') as f:
    temp = json.load(f)

data = temp

manifest = "https://nakamura196.github.io/jpsearch/data/genji/manifest.json"
data["@id"] = manifest
data["label"] = data["label"]

data["service"] = {
    "@context": "http://iiif.io/api/search/0/context.json",
    "@id": "https://iiif.dl.itc.u-tokyo.ac.jp/api/iiif-search/get.php/https://nakamura196.github.io/jpsearch/data/genji/tei.xml",
    "profile": "http://iiif.io/api/search/0/search",
    "label": "Search within this manifest"
}

st = []
data["structures"] = st

files = glob.glob("../../docs/data/"+collection+"/tei/*.xml")

for file in files:

    # ローカルJSONファイルの読み込み
    with open(file, 'r') as f:
        e = json.load(f)

    for s in e["structures"]:
        st.append(s)

fw = open("../../docs/data/"+collection+"/manifest.json", 'w')
json.dump(data, fw, ensure_ascii=False, indent=4,
          sort_keys=True, separators=(',', ': '))