import json
from SPARQLWrapper import SPARQLWrapper
import csv
import urllib.request
import urllib

rows = []

page = 0

flg = True

row = ["URI", "LABEL", "V", "P", "L", "C"]
rows.append(row)

d = 1000
# d = 20

arr = []

max = 0

while(flg):

        print(page)

        url = "https://jpsearch.go.jp/api/item/search/nij18-default?from=" + \
            str(page * d)+"&size="+str(d) + \
            "&keyword=増鏡"
        '''
        url = "https://jpsearch.go.jp/api/item/search/jps-cross?f-db=nij18&from=" + \
            str(page * d)#+"&size="+str(d)
        url = "https://jpsearch.go.jp/api/item/search-so/nij18-default?csid=nij18-default&from=" + \
            str(page * d)+"&size="+str(d)+"&keyword=増鏡"
        '''
        print(url)
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)

        response_body = response.read().decode("utf-8")
        data = json.loads(response_body)

        max = data["hit"]

        list_s = data["list"]
        print(len(list_s))

        for obj in list_s:
                id = obj["id"]

                if obj not in arr:
                        arr.append(obj)
                else:
                        # print(obj)
                        # flg = False
                        # break
                        continue

                collection = obj["nij18-NihuRoot"]["nihuDC"]["FesData"]["Subject-s"][0]
                relation = obj["nij18-NihuRoot"]["nihuDC"]["FesData"]["Relation-s"]
                label = obj["nij18-NihuRoot"]["nihuDC"]["FesData"]["Title-s"][0].replace(
                    "］", "]").split("]")
                if len(label) > 1:
                        label = label[1]
                else:
                        label = label[0]
                # print(relation)
                v = relation[0].replace("］", "]").split("]")[1]
                p = relation[1].replace("］", "]").split("]")[1]
                l = relation[2].replace("］", "]").split("]")[1]

                row = [id, label, v, p, l, collection]
                # print(row)
                rows.append(row)

                if len(rows) - 1 == max:
                        flg = False
                        break

        print(len(rows) - 1)
        print(max)
        page += 1

with open('data/01_list.csv', 'w') as f:
    writer = csv.writer(f, lineterminator='\n')  # 改行コード（\n）を指定しておく
    writer.writerows(rows)  # 2次元配列も書き込める
