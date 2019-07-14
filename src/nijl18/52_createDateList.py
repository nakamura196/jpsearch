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

collection = "azumakagami"
rows = []
with open('data/'+collection+'/01_list_d.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)  # ヘッダーを読み飛ばしたい時

    for row in reader:
        uri = row[0]
        text = row[1]
        v = int(row[2])
        p = int(row[3])
        l = int(row[4])
        c = row[5]
        y = row[6]
        md = row[7]

        y = y.split("（")[0]+md
        print(y)
        row = [y]
        rows.append(row)

with open('data/'+collection+'/date.csv', 'w') as f:
    writer = csv.writer(f, lineterminator='\n')  # 改行コード（\n）を指定しておく
    writer.writerows(rows)  # 2次元配列も書き込める
