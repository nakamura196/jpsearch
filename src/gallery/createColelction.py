import glob
import json
import os
import urllib.request
import urllib.request
from bs4 import BeautifulSoup
import base64

url = "https://jpsearch.go.jp/curation?from=0"

odir = "/Users/nakamura/git/jpsearch/docs/data/gallery"
prefix = "https://nakamura196.github.io/jpsearch/data/gallery"

# odir = "/Users/nakamura/git/dataset_tmp/docs/data/gallery"
# prefix = "https://nakamura196.github.io/dataset_tmp/data/gallery"

html = urllib.request.urlopen(url)

# htmlをBeautifulSoupで扱う
soup = BeautifulSoup(html, "html.parser")

rawJ = soup.find_all('script')
J = str(rawJ[0])
J1 = J.split('\"')
J2 = J1[1]

d = base64.b64decode(J2)
d = json.loads(d)

collections_json = {
    "@context": "http://iiif.io/api/presentation/2/context.json",
    "@id": "https://nakamura196.github.io/jpsearch/data/gallery/collections.json",
    "@type": "sc:Collection",
    "label": "Gallery demo",
    "viewingHint": "top",
    "members": []
}

members = collections_json["members"]

list = d["children"][0]["result"]["list"]
for curation in list:
    id = curation["id"]
    print(id)

    url2 = "https://jpsearch.go.jp/curation/"+id

    html2 = urllib.request.urlopen(url2)

    # htmlをBeautifulSoupで扱う
    soup2 = BeautifulSoup(html2, "html.parser")

    rawJ = soup2.find_all('script')
    J = str(rawJ[0])
    J1 = J.split('\"')
    J2 = J1[1]

    d = base64.b64decode(J2)
    d = json.loads(d)

    # print(d)

    collection_uri = prefix+"/"+id+".json"

    collection = {
        "@context": "http://iiif.io/api/presentation/2/context.json",
        "@type": "sc:Collection",
        "vhint": "use-thumb",
        "@id": collection_uri,
        "label": d["title"]["ja"],
        "manifests": []
    }

    manifests = collection["manifests"]

    if "parts" in d["children"][0]["curation"]:
        parts = d["children"][0]["curation"]["parts"]
        # print(len(parts))

        for part in parts:
            # print(part)
            if "children" in part:
                if "items" in part["children"][0]:
                    items = part["children"][0]["items"]
                    for item in items:
                        if "image" in item:
                            if "infoJsonUrl" in item["image"]:

                                manifest_uri = item["image"]["url"]
                                image_uri = item["image"]["infoJsonUrl"].replace(
                                    "/info.json", "")

                                manifest = {
                                    "@type": "sc:Manifest",
                                    "@id": manifest_uri,
                                    "label": item["description"]["ja"],
                                    "thumbnail": {
                                        "@id": image_uri+"/full/200,200/0/default.jpg",
                                        "@type": "dctypes:Image",
                                        "service": {
                                            "@context": "http://iiif.io/api/image/2/context.json",
                                            "@id": image_uri,
                                            "profile": "http://iiif.io/api/image/2/level1.json"
                                        }
                                    }
                                }

                                manifests.append(manifest)

    if len(manifests) > 0:

        with open(odir+"/"+id+".json", 'w') as outfile:
            json.dump(collection, outfile, ensure_ascii=False,
                      sort_keys=True, separators=(',', ': '), indent=2)

        members.append({
            "@id": collection["@id"],
            "@type": "sc:Collection",
            "label": collection["label"]
        })



with open(odir+"/collections.json", 'w') as outfile:
    json.dump(collections_json, outfile, ensure_ascii=False,
              sort_keys=True, separators=(',', ': '), indent=2)
