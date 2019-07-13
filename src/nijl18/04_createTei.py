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
col_id = "20008370"
key = "水鏡"
'''

collection = "okagami"
col_id = "200019161"
key = "大鏡"

odir = "../../docs/data/"+collection+"/tei"

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
                "text" : text,
                "uri" : uri
                }
    return result


texts = read_list(key)

# ----

prefix = ".//{http://www.tei-c.org/ns/1.0}"
xml = ".//{http://www.w3.org/XML/1998/namespace}"

tmp_path = "data/"+collection+"/template.xml"

# ----

range_map = {}

with open('data/'+collection+'/range.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)  # ヘッダーを読み飛ばしたい時

    for row in reader:
        v = row[0]
        cover = int(row[1])
        start = int(row[2])
        end = int(row[3])
        back = int(row[4])
        dup = row[5].split("|")

        range_map[int(v)] = {
            "start" : start,
            "dup" : dup
        }

# ----

for v, data_v in sorted(texts.items()):

    url = "https://nakamura196.github.io/jpsearch/data/"+collection+"/manifest/" + \
        str(v).zfill(2)+".json"
    print(url)

    # ----

    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)

    response_body = response.read().decode("utf-8")
    data = json.loads(response_body)

    canvas_map = {}
    canvases = data["sequences"][0]["canvases"]
    canvas_index_map = {}
    for i in range(len(canvases)):
        canvas_index_map[canvases[i]["@id"]] = i

    range_body = []
    structures = data["structures"]
    for st in structures:
        if "本文" in st["label"]:
            for cid in st["canvases"]:
                range_body.append(cid)

    canvases_new = []

    for canvas_id in range_body:
        canvas_index = canvas_index_map[canvas_id]

        if str(range_map[v]["start"] + canvas_index) in range_map[v]["dup"]:
            print(range_map[v]["start"] + canvas_index)
            continue

        canvas = canvases[canvas_index]
        canvas_map[canvas_id] = {
            "image": canvas["images"][0]["resource"]["@id"],
            "width": int(canvas["width"]),
            "height": int(canvas["height"])
        }
        canvases_new.append(canvas)

    canvases = canvases_new

    tree = ET.parse(tmp_path)
    ET.register_namespace('', "http://www.tei-c.org/ns/1.0")
    root = tree.getroot()

    root.find(prefix + "title").text = data["label"]

    surfaceGrp = root.find(prefix + "surfaceGrp")
    surfaceGrp.set("facs", url)

    para = root.find(prefix + "body").find(prefix + "p")

    div = None

    surface = None

    pmax = max(data_v)
    pmin = min(data_v)
    for i in range(pmin, pmax + 1):

        p = i

        lb = ET.Element(
            "{http://www.tei-c.org/ns/1.0}lb")
        para.append(lb)

        div = ET.Element(
            "{http://www.tei-c.org/ns/1.0}div")
        para.append(div)

        cid = int(p/2)
        # print(cid)

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
            div.set("facs", "#"+zone_id)

            for l, obj in sorted(data_p.items()):
                lb = ET.Element(
                    "{http://www.tei-c.org/ns/1.0}lb")
                # para.append(lb)
                div.append(lb)

                line = ET.Element(
                    "{http://www.tei-c.org/ns/1.0}line")
                line.set("xml:id", obj["uri"].split("/")[-1])
                line.text = obj["text"]
                # para.append(line)
                div.append(line)

    tree.write(odir+"/"+str(v).zfill(2)+".xml", encoding="utf-8")
