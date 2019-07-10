from pprint import pprint
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import urllib.request
from bs4 import BeautifulSoup
import sys
import os
import csv
import json
from time import sleep
import urllib.parse
import argparse


def exec(uri, key):

    path = "manifests/"+uri.split("/")[-1]+".json"

    if os.path.exists(path):
        return

    flg = True
    page = 0

    manifests = []

    while flg:

        options = webdriver.ChromeOptions()

        options.add_argument('--headless')

        driver = webdriver.Chrome(
            "/usr/local/bin/chromedriver", options=options)

        # PhantomJSをSelenium経由で利用します.
        # driver = webdriver.PhantomJS()

        print(page * 20)

        url = "https://kotenseki.nijl.ac.jp/app/l/#%2Fsl%2Fde%2F%7B%22details%22:%5B%7B%22no%22:1,%22type%22:%22text%22,%22item%22:%7B%22index%22:%221%22,%22name%22:%22%E6%9B%B8%E5%90%8D%22,%22field%22:%22%5C%22s.hshomeih%5C%22,%20%5C%22s.hshomeiy%5C%22,%20%5C%22t.kshomei.s.kshomeih%5C%22,%20%5C%22t.kshomei.s.kshomeiy%5C%22,%20%5C%22s.tshomeih%5C%22,%20%5C%22s.tshomeiy%5C%22,%20%5C%22t.isho.s.ishomeih%5C%22,%20%5C%22t.isho.s.ishomeiy%5C%22,%20%5C%22en.s.hshomeih%5C%22,%20%5C%22en.s.hshomeiy%5C%22,%20%5C%22en.s.tshomeih%5C%22,%20%5C%22en.s.tshomeiy%5C%22,%20%5C%22syomeiMC%5C%22%22,%22comField%22:%22%5C%22s.hshomeih.keyword%5C%22,%20%5C%22s.hshomeiy.keyword%5C%22,%20%5C%22t.kshomei.s.kshomeih.keyword%5C%22,%20%5C%22t.kshomei.s.kshomeiy.keyword%5C%22,%20%5C%22s.tshomeih.keyword%5C%22,%20%5C%22s.tshomeiy.keyword%5C%22,%20%5C%22t.isho.s.ishomeih.keyword%5C%22,%20%5C%22t.isho.s.ishomeiy.keyword%5C%22%22,%22hlField%22:%22%5C%22s.tshomeih%5C%22,%20%5C%22s.tshomeiy%5C%22%22,%22$$hashKey%22:%22object:189%22%7D,%22value%22:%22" + \
            key+"%22,%22method%22:%7B%22index%22:%221%22,%22name%22:%22%E5%AE%8C%E5%85%A8%E4%B8%80%E8%87%B4%22,%22method%22:%22multi_match%22,%22key%22:%22complete%22,%22wildcardfo%22:%22%7C%22,%22wildcardba%22:%22%7C%22,%22$$hashKey%22:%22object:209%22%7D%7D,%7B%22type%22:%22radio%22,%22name%22:%22pubflg%22,%22value%22:%221%22%7D%5D,%22sortField%22:%22s.wid%22,%22sortOrder%22:%22acs%22,%22sz%22:20,%22fr%22:" + \
                str(page*20)+",%22time%22:%2220190710143401%22,%22romajiCheck%22:%22%22%7D"

        # PhantomJSで該当ページを取得＆レンダリングします
        driver.get(url)

        # ちょっと待つ
        # （ページのJS実行に時間が必要あれば）
        time.sleep(5)  # 5s

        # レンダリング結果をPhantomJSから取得します.
        html = driver.page_source

        # 画像のURLを取得する（JSでレンダリングしたところ）.
        bs = BeautifulSoup(html, "html.parser")
        aas = bs.find_all("a")

        if len(aas) > 0:

            count = 0

            for aa in aas:
                link = aa.get("href")
                if link != None and link.find("/viewer") != -1:
                    id = link.split("/")[2]
                    iri = "https://kotenseki.nijl.ac.jp/biblio/"+id+"/manifest"
                    print(iri)
                    if iri not in manifests:
                        manifests.append(iri)

                    count += 1

            if count == 0:
                flg = False

        else:
            flg = False

        # 終了
        driver.quit()

        page += 1

    collection = {
        "@context": "http://iiif.io/api/presentation/2/context.json",
        "@id": uri,
        "@type": "sc:Collection",
        "label": key,
        "manifests": []
    }

    for i in range(len(manifests)):
        iri = manifests[i]
        manifest = {
            "@context": "http://iiif.io/api/presentation/2/context.json",
            "@id": iri,
            "@type": "sc:Manifest",
            "label": "["+str(i+1)+"]"
        }
        collection["manifests"].append(manifest)

    fw = open(path, 'w')
    json.dump(collection, fw, ensure_ascii=False, indent=4,
              sort_keys=True, separators=(',', ': '))


with open('01_list.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)  # ヘッダーを読み飛ばしたい時

    for row in reader:
        uri = row[0]
        key = row[3]

        exec(uri, key)
