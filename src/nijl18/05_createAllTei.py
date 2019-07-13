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
xml = ".//{http://www.w3.org/XML/1998/namespace}"

tmp_path = "data/"+collection+"/template.xml"

# ----

tree = ET.parse(tmp_path)
ET.register_namespace('', "http://www.tei-c.org/ns/1.0")
root = tree.getroot()

root.find(prefix + "title").text = data["label"]

surfaceGrp = root.find(prefix + "surfaceGrp")
surfaceGrp.set("facs", url)

para = root.find(prefix + "body").find(prefix + "p")

files = glob.glob("../../docs/data/"+collection+"/tei/*.xml")

for file in sorted(files):
    tree2 = ET.parse(file)
    root2 = tree2.getroot()
    divs = root2.findall(prefix + "div")

    for div in divs:
        lb = ET.Element(
            "{http://www.tei-c.org/ns/1.0}lb")
        # para.append(lb)
        para.append(lb)

        para.append(div)

    surfaces = root2.findall(prefix+"surface")
    for surface in surfaces:
        root.find(prefix+"surfaceGrp").append(surface)

tree.write("../../docs/data/"+collection+"/tei.xml", encoding="utf-8")
