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


def read_list():
    result = {}
    with open('data/01_list.csv', 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # ヘッダーを読み飛ばしたい時

        for row in reader:
            uri = row[0]
            text = row[1]
            v = int(row[2])
            p = int(row[3])

            if v not in result:
                result[v] = {}

            obj = result[v]
            if p not in obj:
                obj[p] = {}

            obj[p][uri] = text
    return result


texts = read_list()

# ローカルJSONファイルの読み込み
with open('data/manifest.json', 'r') as f:
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

count_pics = 1
pics = []

with open('data/genji.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)  # ヘッダーを読み飛ばしたい時

    for row in reader:
        v = row[0]
        cover = int(row[1])
        back = int(row[4])

        full = []
        st.append({
            "@id": "https://kotenseki.nijl.ac.jp/biblio/200003803/range/r"+v+".json",
            "@type": "sc:Range",
            "label": "第"+str(v)+"冊",
            "canvases": full
        })
        full.append(
            "https://kotenseki.nijl.ac.jp/biblio/200003803/canvas/"+str(cover))

        body = []
        for i in list(range(cover+1, back)):
            c = "https://kotenseki.nijl.ac.jp/biblio/200003803/canvas/"+str(i)
            body.append(c)
            full.append(c)

        full.append(
            "https://kotenseki.nijl.ac.jp/biblio/200003803/canvas/"+str(back))

        st.append({
            "@id": "https://kotenseki.nijl.ac.jp/biblio/200003803/range/r"+v+"_cover.json",
            "@type": "sc:Range",
            "label": "表紙",
            "within": "https://kotenseki.nijl.ac.jp/biblio/200003803/range/r"+v+".json",
            "canvases": [
                "https://kotenseki.nijl.ac.jp/biblio/200003803/canvas/" +
                str(cover)
            ]
        })

        # ---

        data_v = texts[int(v)]
        pmax = max(data_v)
        pmin = min(data_v)

        

        for i in range(pmin, pmax):
            if i not in data_v:

                p = int(i/2) + (1 + cover)
                
                st.append({
                    "@id": "https://kotenseki.nijl.ac.jp/biblio/200003803/range/r"+v+"_pic"+str(count_pics)+".json",
                    "@type": "sc:Range",
                    "label": "挿絵["+str(count_pics)+"]",
                    "within": "https://kotenseki.nijl.ac.jp/biblio/200003803/range/r"+v+".json",
                    "canvases": ["https://kotenseki.nijl.ac.jp/biblio/200003803/canvas/"+str(p)]
                })
                

                canvas = data["sequences"][0]["canvases"][p-1]
                width = canvas["width"]
                height = canvas["height"]

                

                if i % 2 == 0:
                    x = int(width / 2)
                    y = 0
                    w = int(width / 2)
                    h = height
                else:
                    x = 0
                    y = 0
                    w = int(width / 2)
                    h = height

                xywh = str(x)+","+str(y)+","+str(w)+","+str(h)

                pics.append({
                    "@id": "https://kotenseki.nijl.ac.jp/biblio/200003803/canvas/"+str(p)+"#xywh="+xywh,
                    "@type": "sc:Canvas",
                    "label": "挿絵["+str(count_pics)+"]"
                })

                count_pics += 1

        # ---

        st.append({
            "@id": "https://kotenseki.nijl.ac.jp/biblio/200003803/range/r"+v+"_backcover.json",
            "@type": "sc:Range",
            "label": "裏表紙",
            "within": "https://kotenseki.nijl.ac.jp/biblio/200003803/range/r"+v+".json",
            "canvases": [
                "https://kotenseki.nijl.ac.jp/biblio/200003803/canvas/" +
                str(back)
            ]
        })

fw = open("../../docs/data/genji/manifest.json", 'w')
json.dump(data, fw, ensure_ascii=False, indent=4,
            sort_keys=True, separators=(',', ': '))


curation = {
    "@context": [
        "http://iiif.io/api/presentation/2/context.json",
        "http://codh.rois.ac.jp/iiif/curation/1/context.json"
    ],
    "@type": "cr:Curation",
    "@id": "https://nakamura196.github.io/jpsearch/data/genji/curation.json",
    "label": "挿絵キュレーション",
    "selections": [
        {
            "@id": "https://nakamura196.github.io/jpsearch/data/genji/curation.json#1",
            "@type": "sc:Range",
            "label": "Automaic curation by IIIF Converter",
            "members": pics,
            "within": {
                "@id": "https://nakamura196.github.io/jpsearch/data/genji/manifest.json",
                "@type": "sc:Manifest",
                "label": "源氏物語"
            }
        }
    ]
}

fw = open("../../docs/data/genji/curation.json", 'w')
json.dump(curation, fw, ensure_ascii=False, indent=4,
            sort_keys=True, separators=(',', ': '))
