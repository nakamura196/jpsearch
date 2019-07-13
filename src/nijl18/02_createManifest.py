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
import copy

'''
collection = "masukagami"
col_id = "200010997"
key = "増鏡"

collection = "imakagami"
col_id = "200017351"
key = "今鏡"

collection = "okagami"
col_id = "200019161"
key = "大鏡"

collection = "mizukagami"
col_id = "200008370"
key = "水鏡"

'''

collection = "azumakagami"
col_id = "200005040"
key = "吾妻鏡"

odir = "../../docs/data/"+collection+"/manifest"

os.makedirs(odir, exist_ok=True)

def read_list(key):
    result = {}
    with open('data/'+collection+'/01_list.csv', 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # ヘッダーを読み飛ばしたい時

        for row in reader:
            uri = row[0]
            text = row[1]
            v = int(row[2])
            p = int(row[3])
            l = int(row[4])
            c = row[5]

            if key not in c:
                continue

            if v not in result:
                result[v] = {}

            obj = result[v]
            if p not in obj:
                obj[p] = {}

            obj[p][l] = {
                "text": text,
                "uri": uri
            }
    return result


texts = read_list(key)


url = "https://kotenseki.nijl.ac.jp/biblio/"+col_id+"/manifest"

# ----

request = urllib.request.Request(url)
response = urllib.request.urlopen(request)

response_body = response.read().decode("utf-8")
temp = json.loads(response_body)

with open('data/'+collection+'/range.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)  # ヘッダーを読み飛ばしたい時

    for row in reader:
        v = row[0]
        cover = int(row[1])
        start = int(row[2])
        end = int(row[3])
        back = int(row[4])
        
        data = copy.deepcopy(temp)

        manifest = "https://nakamura196.github.io/jpsearch/data/"+collection+"/manifest/" + \
            str(v).zfill(2)+".json"
        data["@id"] = manifest
        data["label"] = data["label"]+" 第"+str(v)+"冊"

        data["service"] = {
            "@context": "http://iiif.io/api/search/0/context.json",
            "@id": "https://iiif.dl.itc.u-tokyo.ac.jp/api/iiif-search/get.php/https://nakamura196.github.io/jpsearch/data/"+collection+"/tei/"+str(v).zfill(2)+".xml",
            "profile": "http://iiif.io/api/search/0/search",
            "label": "Search within this manifest"
        }

        canvases_old = data["sequences"][0]["canvases"]

        st = []
        data["structures"] = st

        # ----

        full = []
        st.append({
            "@id": "https://kotenseki.nijl.ac.jp/biblio/"+col_id+"/range/r"+v+".json",
            "@type": "sc:Range",
            "label": "第"+str(v)+"冊",
            "canvases": full
        })
        full.append(
            "https://kotenseki.nijl.ac.jp/biblio/"+col_id+"/canvas/"+str(cover))

        for i in list(range(cover + 1, start)):
            full.append(
                "https://kotenseki.nijl.ac.jp/biblio/"+col_id+"/canvas/"+str(i))

        body = []
        for i in list(range(start, end+1)):
            c = "https://kotenseki.nijl.ac.jp/biblio/"+col_id+"/canvas/"+str(i)
            body.append(c)
            full.append(c)

        for i in list(range(end+1, back)):
            full.append(
                "https://kotenseki.nijl.ac.jp/biblio/"+col_id+"/canvas/"+str(i))

        full.append(
            "https://kotenseki.nijl.ac.jp/biblio/"+col_id+"/canvas/"+str(back))

        st.append({
            "@id": "https://kotenseki.nijl.ac.jp/biblio/"+col_id+"/range/r"+v+"_cover.json",
            "@type": "sc:Range",
            "label": "表紙",
            "within": "https://kotenseki.nijl.ac.jp/biblio/"+col_id+"/range/r"+v+".json",
            "canvases": [
                "https://kotenseki.nijl.ac.jp/biblio/"+col_id+"/canvas/" +
                str(cover)
            ]
        })

        # ---

        st.append({
            "@id": "https://kotenseki.nijl.ac.jp/biblio/"+col_id+"/range/r"+v+"_body.json",
            "@type": "sc:Range",
            "label": "本文",
            "within": "https://kotenseki.nijl.ac.jp/biblio/"+col_id+"/range/r"+v+".json",
            "canvases": body
        })

        '''

        data_v = texts[int(v)]
        pmax = max(data_v)
        pmin = min(data_v)

        count_pics = 1

        for i in range(pmin, pmax):
            if i not in data_v:
                p = int(i/2) + (1 + cover)
                st.append({
                    "@id": "https://kotenseki.nijl.ac.jp/biblio/"+col_id+"/range/r"+v+"_pic"+str(count_pics)+".json",
                    "@type": "sc:Range",
                    "label": "挿絵["+str(count_pics)+"]",
                    "within": "https://kotenseki.nijl.ac.jp/biblio/"+col_id+"/range/r"+v+".json",
                    "canvases": ["https://kotenseki.nijl.ac.jp/biblio/"+col_id+"/canvas/"+str(p)]
                })
                count_pics += 1

        '''

        # ---

        st.append({
            "@id": "https://kotenseki.nijl.ac.jp/biblio/"+col_id+"/range/r"+v+"_backcover.json",
            "@type": "sc:Range",
            "label": "裏表紙",
            "within": "https://kotenseki.nijl.ac.jp/biblio/"+col_id+"/range/r"+v+".json",
            "canvases": [
                "https://kotenseki.nijl.ac.jp/biblio/"+col_id+"/canvas/" +
                str(back)
            ]
        })

        canvases = []
        for canvas in canvases_old:
            if canvas["@id"] in full:
                canvases.append(canvas)

        data["sequences"][0]["canvases"] = canvases

        fw = open(odir+"/" +
                  str(v).zfill(2)+".json", 'w')
        json.dump(data, fw, ensure_ascii=False, indent=4,
                  sort_keys=True, separators=(',', ': '))
