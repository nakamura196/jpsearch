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

st = []

with open('data/genji.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)  # ヘッダーを読み飛ばしたい時

    for row in reader:
        v = row[0]
        cover = int(row[1])
        back = int(row[4])

        full = []
        full.append("https://kotenseki.nijl.ac.jp/biblio/200003803/canvas/"+str(cover))
        
        body = []
        for i in list(range(cover+1, back)):
            c = "https://kotenseki.nijl.ac.jp/biblio/200003803/canvas/"+str(i)
            body.append(c)
            full.append(c)

        full.append(
            "https://kotenseki.nijl.ac.jp/biblio/200003803/canvas/"+str(back))

        st.append({
            "@id": "https://kotenseki.nijl.ac.jp/biblio/200003803/range/r"+v+".json",
            "@type": "sc:Range",
            "label": "第"+v+"冊",
            "canvases": full
        })
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
        st.append({
            "@id": "https://kotenseki.nijl.ac.jp/biblio/200003803/range/r"+v+"_body.json",
            "@type": "sc:Range",
            "label": "本文",
            "within": "https://kotenseki.nijl.ac.jp/biblio/200003803/range/r"+v+".json",
            "canvases": body
        })
        st.append({
            "@id": "https://kotenseki.nijl.ac.jp/biblio/200003803/range/r"+v+"_backcover.json",
            "@type": "sc:Range",
            "label": "裏表紙",
            "within": "https://kotenseki.nijl.ac.jp/biblio/200003803/range/r"+v+".json",
            "canvases": [
                "https://kotenseki.nijl.ac.jp/biblio/200003803/canvas/"+str(back)
            ]
        })


fw = open("data/range.json", 'w')
json.dump(st, fw, ensure_ascii=False, indent=4,
          sort_keys=True, separators=(',', ': '))
