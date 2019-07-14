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
from rdflib import URIRef, BNode, Literal, Graph
from rdflib.namespace import RDF, RDFS, FOAF, XSD
from rdflib import Namespace

collection = "azumakagami"

map = {}
date_map = {}

g = Graph()

with open('data/'+collection+'/date_edited.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)  # ヘッダーを読み飛ばしたい時

    for row in reader:
        uri = row[0]
        wareki = row[1]
        date = row[2]
        date = date.split(" ")[1] if " " in date else ""
        map[uri] = date
        if date not in date_map:
            date_map[date] = wareki

rows = []

map2 = {}

with open('data/'+collection+'/01_list_d.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)  # ヘッダーを読み飛ばしたい時
    

    for row in reader:
        uri = row[0]
        text = row[1]
        date = map[uri] if uri in map else ""

        if date not in map2:
            map2[date] = {}

        map2[date][uri] = text

        '''
        
        uri = "https://jpsearch.go.jp/data/"+uri
        subject = URIRef(uri)

        p = URIRef("http://purl.org/dc/terms/title")
        g.add((subject, p, Literal(text)))

        p = URIRef("http://purl.org/dc/terms/date")
        g.add((subject, p, Literal(date)))

        '''

for date in map2:
    text = ""
    text += date_map[date] + "\n"
    flg = True

    subject = "http://datetime.hutime.org/date/"+date
    subject = URIRef(subject)

    for uri in sorted(map2[date]):
        text += map2[date][uri]+"\n"
        if flg:
            p = URIRef("http://purl.org/dc/terms/identifier")
            g.add((subject, p, Literal(uri)))

            # flg = False

    

    p = URIRef("http://purl.org/dc/terms/title")
    g.add((subject, p, Literal(text)))

    p = URIRef("http://purl.org/dc/terms/date")
    g.add((subject, p, Literal(date)))

    p = URIRef("http://purl.org/dc/terms/description")
    g.add((subject, p, Literal(date_map[date])))
                
g.serialize(destination='data/'+collection+'/data.json', format='json-ld')
