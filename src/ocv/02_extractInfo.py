#coding:utf-8
import cv2
import requests
import shutil
import json
import urllib.request
import csv
import requests
from bs4 import BeautifulSoup

def download_img(url, file_name):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(file_name, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

rows = []
row = ["URL", "IMG"]
rows.append(row)

with open('01_list.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)  # ヘッダーを読み飛ばしたい時

    for row in reader:
        url = row[1]
        print(url)
        row = [url]

        if "/syouzou/" in url:
            r = requests.get(url)
            r.encoding = r.apparent_encoding
            soup = BeautifulSoup(r.text, 'lxml')  # 要素を抽出

            tbodys = soup.find_all("tbody")

            for tbody in tbodys:
                tr = tbody.find_all("tr")[2]
                img_url = tr.find_all("td")[0].find("img").get("src")

                img_url = url.split("/html/")[0] + "/img/" + img_url.split("/img/")[1]
                row.append(img_url)
    
    rows.append(row)

with open('02_images.csv', 'w') as f:
    writer = csv.writer(f, lineterminator='\n')  # 改行コード（\n）を指定しておく
    writer.writerows(rows)  # 2次元配列も書き込める
