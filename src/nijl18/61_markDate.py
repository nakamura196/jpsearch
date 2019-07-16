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

map = {}

with open('data/'+collection+'/date_edited.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)  # ヘッダーを読み飛ばしたい時

    for row in reader:
        uri = row[0]
        wareki = row[1]
        date = row[2]
        date = date.split(" ")[1] if " " in date else ""
        map[uri] = {
            "wareki": wareki,
            "date": date
        }

# ----

prefix = ".//{http://www.tei-c.org/ns/1.0}"
xml = ".//{http://www.w3.org/XML/1998/namespace}"

tmp_path = "data/"+collection+"/template.xml"

# ----

files = glob.glob("../../docs/data/"+collection+"/tei/*.xml")

for file in sorted(files):
    tree2 = ET.parse(file)
    root2 = tree2.getroot()
    ET.register_namespace('', "http://www.tei-c.org/ns/1.0")
    lines = root2.findall(prefix + "line")

    for line in lines:
        id = line.get("{http://www.w3.org/XML/1998/namespace}id")
        # print(id)
        text = line.text
        # print(text)
        if id in map:
            obj = map[id]
            tmp = obj["wareki"].split("月")
            if len(tmp) > 1:
                day = map[id]["wareki"].split("月")[1]
                if "二十" in day:
                    day = day.replace("二十", "廿")
                # print(day)
                if text.startswith(day+"△"):
                    # print(obj["date"])

                    date = ET.Element(
                        "{http://www.tei-c.org/ns/1.0}date")
                    date.set("when", obj["date"])
                    date.set("when-custom", obj["wareki"])
                    date.text = day

                    line.text = ""
                    line.append(date)
                    line.tail = "△"+text.split(day+"△")[1]

    tree2.write(file.replace("/tei/", "/tei_d/"), encoding="utf-8")

    # break
