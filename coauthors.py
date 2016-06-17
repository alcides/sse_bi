import sys
import pandas as pd
#import matplotlib.pyplot as plt

from nltk.corpus import stopwords

GRAPH = True

by_year = False
filter_since = None
if len(sys.argv) >= 2:
    if sys.argv[1] == 'year':
        by_year = True
    if sys.argv[1] == 'since':
        filter_since = int(sys.argv[2])

df = pd.read_csv("data/pubs_sse.csv", sep=",", header=0)

approved = map(lambda x: x.strip(), open('data/sse_members.txt').readlines())

stop = map(unicode, stopwords.words('english'))
graph = {}
graph_y = {}
people = []

pairs = {}
indiv_pubs = {}

for i in df.index:
    pub = df.ix[i][0]
    author = df.ix[i][10]
    year = df.ix[i][7]
    
    if author not in approved:
        print "rejected", author
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
        
def histogram(lst):
    cnt = {}
    for i in lst:
        if i not in cnt:
            cnt[i] = 1
        else:
            cnt[i] += 1
    return cnt

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
        
vertex = {}
        
if GRAPH:
    
    def make_name(n):
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
    
    for pair in sorted(pairs.keys()):
        if pair[0] not in vertex:
            vertex[pair[0]] = t.add_vertex()
            name_prop[vertex[pair[0]]] = make_name(pair[0])
            pub_prop[vertex[pair[0]]] = indiv_pubs[pair[0]] * 4
        if pair[1] not in vertex:
            vertex[pair[1]] = t.add_vertex()
            name_prop[vertex[pair[1]]] = make_name(pair[1])
            pub_prop[vertex[pair[1]]] = indiv_pubs[pair[1]] * 4
        
        v1 = vertex[pair[0]]
        v2 = vertex[pair[1]]
        
        e = t.add_edge(v1, v2)
        pp_prop[e] = pairs[pair] * 4
    
    gt.graph_draw(t,
              vertex_font_size=16,
              vertex_anchor=0,
              output_size=[8192,4024],
              edge_pen_width= pp_prop,
              vertex_size = pub_prop,
              vertex_text = name_prop,
              output='graph.png')
              
    state = gt.minimize_blockmodel_dl(t)
    k = dr.sfdp_layout(state)
    gt.graph_draw(state, pos=k, output="cluster.pdf")