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

# ----

prefix = ".//{http://www.tei-c.org/ns/1.0}"
xml = ".//{http://www.w3.org/XML/1998/namespace}"

tmp_path = "data/template_n.xml"

# ----

for v, data_v in sorted(texts.items()):

    if v > 54:
        continue

    url = "https://nakamura196.github.io/jpsearch/data/genji/manifest/" + \
        str(v).zfill(2)+".json"

    print(url)

    # ----

    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)

    response_body = response.read().decode("utf-8")
    data = json.loads(response_body)

    canvas_map = {}
    canvases = data["sequences"][0]["canvases"]
    for canvas in canvases:
        canvas_map[canvas["@id"]] = {
            "image": canvas["images"][0]["resource"]["@id"],
            "width": int(canvas["width"]),
            "height": int(canvas["height"])
        }

    tree = ET.parse(tmp_path)
    ET.register_namespace('', "http://www.tei-c.org/ns/1.0")
    root = tree.getroot()

    root.find(prefix + "title").text = data["label"]

    surfaceGrp = root.find(prefix + "surfaceGrp")
    surfaceGrp.set("facs", url)

    # para = root.find(prefix + "body").find(prefix + "p")

    div = None

    surface = None

    pmax = max(data_v)+1
    pmin = min(data_v)
    for i in range(pmin, pmax):

        p = i

        lb = ET.Element(
            "{http://www.tei-c.org/ns/1.0}lb")
        # para.append(lb)

        div = ET.Element(
            "{http://www.tei-c.org/ns/1.0}div")
        # para.append(div)

        cid = int(p/2) + 1

        canvas_id = canvases[cid]["@id"]

        canvas = canvas_map[canvas_id]
        image = canvas["image"]

        zone_id = "zone_"+str(v).zfill(4)+"_"+str(p).zfill(4)

        if p == 1 or p % 2 == 0:

            surface = ET.Element(
                "{http://www.tei-c.org/ns/1.0}surface")
            surfaceGrp.append(surface)

            graphic = ET.Element(
                "{http://www.tei-c.org/ns/1.0}graphic")
            surface.append(graphic)
            graphic.set("url", canvas_map[canvas_id]["image"])
            graphic.set("n", canvas_id)

            pb = ET.Element(
                "{http://www.tei-c.org/ns/1.0}pb")
            pb.set("n", str(p))
            div.append(pb)
        
        if p in data_v:
            data_p = data_v[p]

            zone = ET.Element(
                "{http://www.tei-c.org/ns/1.0}zone")
            surface.append(zone)
            zone.set("xml:id", zone_id)
            w = canvas["width"]
            h = canvas["height"]
            if p % 2 == 0:
                # if p == 1 or p % 2 == 0:
                zone.set("lrx", str(w))
                zone.set("lry", str(h))
                zone.set("ulx", str(int(w/2)))
                zone.set("uly", "0")
            else:
                zone.set("lrx", str(int(w/2)))
                zone.set("lry", str(h))
                zone.set("ulx", "0")
                zone.set("uly", "0")

            # pb.set("facs", "#"+zone_id)
            # div.set("facs", "#"+zone_id)

            for l, data_l in sorted(data_p.items()):
                lb = ET.Element(
                    "{http://www.tei-c.org/ns/1.0}lb")
                # para.append(lb)
                zone.append(lb)

                line = ET.Element(
                    "{http://www.tei-c.org/ns/1.0}line")
                line.set("xml:id", l.split("/")[-1])
                line.text = data_l
                # para.append(line)
                zone.append(line)

    tree.write("../../docs/data/genji/tei_n/"+str(v).zfill(2)+".xml", encoding="utf-8")
