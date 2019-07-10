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
    with open('01_list.csv', 'r') as f:
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


url = "https://nakamura196.github.io/jpsearch/data/genji/manifest.json"

texts = read_list()

# ----

prefix = ".//{http://www.tei-c.org/ns/1.0}"
xml = ".//{http://www.w3.org/XML/1998/namespace}"

tmp_path = "data/template.xml"

# ----

request = urllib.request.Request(url)
response = urllib.request.urlopen(request)

response_body = response.read().decode("utf-8")
data = json.loads(response_body)

canvas_map = {}
canvases = data["sequences"][0]["canvases"]
for canvas in canvases:
    canvas_map[canvas["@id"]] = {
        "image" : canvas["images"][0]["resource"]["@id"],
        "width" : int(canvas["width"]),
        "height" : int(canvas["height"])
    }

structures = data["structures"]

range_map = {}

for structure in structures:
    label = structure["label"]
    if label == "本文":
        v = structure["within"].replace(
            "https://kotenseki.nijl.ac.jp/biblio/200003803/range/r", "").replace(".json", "")
        range_map[int(v)] = structure["canvases"]

# ----

for v, data_v in sorted(texts.items()):

    canvases = range_map[v]

    tree = ET.parse(tmp_path)
    ET.register_namespace('', "http://www.tei-c.org/ns/1.0")
    root = tree.getroot()

    root.find(prefix + "title").text = data["label"]+" 第"+str(v)+"冊"

    surfaceGrp = root.find(prefix + "surfaceGrp")
    surfaceGrp.set("facs", url)

    para = root.find(prefix + "body").find(prefix + "p")

    for p, data_p in sorted(data_v.items()):

        lb = ET.Element(
            "{http://www.tei-c.org/ns/1.0}lb")
        para.append(lb)

        pb = ET.Element(
            "{http://www.tei-c.org/ns/1.0}pb")
        pb.set("n", str(p))
        para.append(pb)

        if p == 1 or p % 2 == 0:

            canvas_id = ""

            if p == 1:
                canvas_id = canvases[0]
                
            else:
                if p % 2 == 0:
                    canvas_id = canvases[int(p/2)]

            canvas = canvas_map[canvas_id]
            image = canvas["image"]

            zone_id = "zone_"+str(p).zfill(4)

            surface = ET.Element(
                "{http://www.tei-c.org/ns/1.0}surface")
            surfaceGrp.append(surface)

            graphic = ET.Element(
                "{http://www.tei-c.org/ns/1.0}graphic")
            surface.append(graphic)
            graphic.set("url", canvas_map[canvas_id]["image"])
            graphic.set("n", canvas_id)

            zone = ET.Element(
                "{http://www.tei-c.org/ns/1.0}zone")
            surface.append(zone)
            zone.set("xml:id", zone_id)
            zone.set("lrx", str(canvas["width"]))
            zone.set("lry", str(canvas["height"]))
            zone.set("ulx", str(0))
            zone.set("uly", str(0))

            pb.set("facs", "#"+zone_id)


        for l, data_l in sorted(data_p.items()):
            lb = ET.Element(
                "{http://www.tei-c.org/ns/1.0}lb")
            para.append(lb)

            line = ET.Element(
                "{http://www.tei-c.org/ns/1.0}line")
            line.set("xml:id", l.split("/")[-1])
            line.text = data_l
            para.append(line)

    tree.write("../../docs/data/genji/genji_"+str(v).zfill(2)+".xml", encoding="utf-8")

    if v >= 3:
        break
