#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pandas as pd
#import matplotlib.pyplot as plt

from nltk.corpus import stopwords
from nltk.stem.snowball import EnglishStemmer
stemmer = EnglishStemmer()

clas = map( lambda x: (x, stemmer.stem(x)), map(lambda x: type(x) == str and x.lower().strip().decode('utf-8') or u"", open("data/acm_categories.txt", 'r').readlines()))

GRAPH = True
keywords = False
by_year = False
filter_since = None
if len(sys.argv) >= 2:
    if sys.argv[1] == 'year':
        by_year = True
    if sys.argv[1] == 'since':
        filter_since = int(sys.argv[2])
    if sys.argv[3] == 'keywords':
        keywords = True


df = pd.read_csv("data/pubs_sse.csv", sep=",", header=0)

approved = map(lambda x: x.strip(), open('data/sse_members.txt').readlines())

stop = map(unicode, stopwords.words('english'))
graph = {}
graph_y = {}
people = []

pairs = {}
indiv_pubs = {}

pubkeys = {}

for i in df.index:
    pub = df.ix[i][0]
    author = df.ix[i][10]
    year = df.ix[i][7]
    
    if author not in approved:
        #print "rejected", author
        continue
    
    if filter_since and int(year) < filter_since:
        continue
    
    if author not in indiv_pubs:
        indiv_pubs[author] = 1
    else:
        indiv_pubs[author] += 1
    
    if author not in people:
        people.append(author)
    if pub not in graph:
        graph[pub] = [author]
    else:
        graph[pub].append(author)
    graph_y[pub] = year
    
    ks = []
    abstract = df.ix[i][3]
    keys = df.ix[i][5]
    keys = type(keys) == str and keys.decode('utf-8').lower() or ""
    abstract = type(abstract) == str and abstract.decode('utf-8').lower() or ""    
    
    for cl, cl_s in clas:
        if cl in keys:
            ks.append(cl)
            continue
        if cl in abstract:
            ks.append(cl)
            continue
        if cl_s in stemmer.stem(abstract):
            ks.append(cl)
    pubkeys[pub] = ks
        
def histogram(lst):
    cnt = {}
    for i in lst:
        if i not in cnt:
            cnt[i] = 1
        else:
            cnt[i] += 1
    return cnt
    
    
def merge(b, o):    
    if not o:
        return b
    else:
        for k in o:
            if k not in b:
                b[k] = o[k]
            else:
                b[k] += o[k]
        return b

coauthor_keys = {}
for author in people:
    coauthors = []
    for pub in graph:
        if author in graph[pub]:
            for coauthor in graph[pub]:
                if coauthor != author:
                    if coauthor < author:
                        k = by_year and (coauthor, author, graph_y[pub]) or (coauthor, author)
                    else:
                        k = by_year and (author, coauthor, graph_y[pub]) or (coauthor, author)
                    if k not in pairs:
                        pairs[k] = 1
                    else:
                        pairs[k] += 1
                    coauthors.append(coauthor)
                    
                    dic = {}
                    for v in pubkeys[pub]:
                        dic[v] = 1
                    coauthor_keys[k] = merge(dic, k in coauthor_keys and coauthor_keys[k] or {})
    key_dict = histogram(coauthors)
            
    data = []
    for k in key_dict:
        data.append((key_dict[k], k))

    data.sort()
    data.reverse()


for pair in sorted(pairs.keys()):
    if by_year:
        print pair[0] + ";" + pair[1] + ";" + str(pair[2]) + ";"+ str(pairs[pair])
        print pair[1] + ";" + pair[0] + ";" + str(pair[2]) + ";"+ str(pairs[pair])
    else:
        print pair[0] + ";" + pair[1] + ";" + str(pairs[pair])
        print pair[1] + ";" + pair[0] + ";" + str(pairs[pair])
        
if keywords:
    for pair in sorted(coauthor_keys):
        if coauthor_keys[pair]:
            ls = sorted([ (coauthor_keys[pair][k], k) for k in coauthor_keys[pair]])[::-1]
            strr = ", ".join([ str(a[1]) + " " + str(a[0]) for a in ls ])
            print pair[0], ",", pair[1], ",", strr
        
vertex = {}
        
if GRAPH:
    
    def make_name(n):
        if "Gabriel Silva" in n:
            return u"João Gabriel"
        parts = n.split(" ")
        if len(parts) < 2:
            return n
        else:
            return "%s %s" % ( parts[0], parts[-1] )
    
    import graph_tool.all as gt
    import graph_tool.draw as dr
    import math
    
    t = gt.Graph(directed=False)
    pp_prop = t.new_edge_property("int")
    t.edge_properties["pair_pub"] = pp_prop
    
    name_prop = t.new_vertex_property('string')
    t.vertex_properties['name'] = name_prop
    
    pub_prop = t.new_vertex_property('int')
    t.vertex_properties['pubs'] = pub_prop
    
    pub_prop_font = t.new_vertex_property('int')
    t.vertex_properties['pub_prop_font'] = pub_prop_font
    
    
    pairdone = []
    for opair in sorted(pairs.keys()):
        pair = tuple(sorted(opair))
        if pair in pairdone:
            continue
        pairdone.append(pair)
        
                
        if pair[0] not in vertex:
            vertex[pair[0]] = t.add_vertex()
            name_prop[vertex[pair[0]]] = make_name(pair[0])
            pub_prop[vertex[pair[0]]] = indiv_pubs[pair[0]] * 4
            pub_prop_font[vertex[pair[0]]] = min(18, indiv_pubs[pair[0]] / 4)
        if pair[1] not in vertex:
            vertex[pair[1]] = t.add_vertex()
            name_prop[vertex[pair[1]]] = make_name(pair[1])
            pub_prop[vertex[pair[1]]] = indiv_pubs[pair[1]] * 4
            pub_prop_font[vertex[pair[1]]] = min(18, indiv_pubs[pair[1]] / 4)
        
        v1 = vertex[pair[0]]
        v2 = vertex[pair[1]]
        
        e = t.add_edge(v1, v2)
        pp_prop[e] = pairs[opair]
    
    gt.graph_draw(t,
              vertex_font_size=15, #pub_prop_font,
              vertex_anchor=0,
              output_size=[8192,4024],
              edge_pen_width= pp_prop,
              vertex_size = 150, #pub_prop,
              vertex_text = name_prop,
              output='graph.png')
              