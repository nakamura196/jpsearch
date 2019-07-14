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

# collection = "imakagami"

# collection = "okagami"

# collection = "mizukagami"

collection = "azumakagami"

# ----

url = "https://nakamura196.github.io/jpsearch/data/"+collection+"/manifest.json"
print(url)

# ----

request = urllib.request.Request(url)
response = urllib.request.urlopen(request)

response_body = response.read().decode("utf-8")
data = json.loads(response_body)

# ----

prefix = ".//{http://www.tei-c.org/ns/1.0}"

tmp_path = "data/"+collection+"/template.xml"

# ----

# ローカルJSONファイルの読み込み
with open('data/'+collection+'/data.json', 'r') as f:
    json_data = json.load(f)

wareki_map = {}

date_map = {}
for obj in json_data:
    date = obj["http://purl.org/dc/terms/date"][0]["@value"]
    date_map[date] = []
    for id in obj["http://purl.org/dc/terms/identifier"]:
        date_map[date].append(id["@value"])

    wareki_map[date] = obj["http://purl.org/dc/terms/description"][0]["@value"]

# ----

tree = ET.parse(tmp_path)
ET.register_namespace('', "http://www.tei-c.org/ns/1.0")
ET.register_namespace('xml', "http://www.w3.org/XML/1998/namespace")
root = tree.getroot()

root.find(prefix + "title").text = data["label"]

surfaceGrp = root.find(prefix + "surfaceGrp")
surfaceGrp.set("facs", url)

para = root.find(prefix + "body").find(prefix + "p")

files = glob.glob("../../docs/data/"+collection+"/tei/*.xml")

zone_map = {}
line_map= {}

for file in sorted(files):
    tree2 = ET.parse(file)
    root2 = tree2.getroot()

    surfaces = root2.findall(prefix+"surface")
    for surface in surfaces:
        canvasID = surface.find(prefix+"graphic").get("n")
        zones = surface.findall(prefix+"zone")
        for zone in zones:
            zone_id = zone.get("{http://www.w3.org/XML/1998/namespace}id")
            zone_map[zone_id] = canvasID

    divs = root2.find(prefix+"body").findall(prefix + "div")

    for div in divs:
        zone_id = div.get("facs")
        if zone_id == None:
            print("No facs")
            continue
        zone_id = zone_id.replace("#", "")
        lines = div.findall(prefix+"line")

        for line in lines:
            line_id = line.get("{http://www.w3.org/XML/1998/namespace}id")
            line_map[line_id] = zone_map[zone_id]

count = 0


st = []
all = []
'''
st.append({
    "@id": "https://kotenseki.nijl.ac.jp/biblio/200005040/range/r_date.json",
    "@type": "sc:Range",
    "label": "年月日別",
    # "canvases": all
})
'''

count = 1
for date in sorted(date_map):

    print(date)

    if date == "":
        continue

    line_ids = date_map[date]
    canvases = []
    for line_id in sorted(line_ids):
        if line_id not in line_map:
            # print("not in map\t"+line_id)
            count += 1
            continue
        canvasID = line_map[line_id]
        # print(date+"\t"+canvasID)
        if canvasID not in canvases:
            canvases.append(canvasID)
            
        if canvasID not in all:
            all.append(canvasID)

    st.append({
        "@id": "https://kotenseki.nijl.ac.jp/biblio/200005040/range/r_date_"+str(count)+".json",
        "@type": "sc:Range",
        "label": wareki_map[date]+" ("+date+")",
        # "within": "https://kotenseki.nijl.ac.jp/biblio/200005040/range/r_date.json",
        "canvases": canvases
    })

    count += 1

# all.sort()

data["structures"] = st

fw = open('../../docs/data/'+collection+'/manifest_d.json', 'w')
json.dump(data, fw, ensure_ascii=False, indent=4,
          sort_keys=True, separators=(',', ': '))



print(count)



# tree.write("../../docs/data/"+collection+"/tei.xml", encoding="utf-8")
