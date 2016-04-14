import sys
import pandas as pd
#import matplotlib.pyplot as plt

from nltk.corpus import stopwords

by_year = False
filter_since = None
if len(sys.argv) >= 2:
    if sys.argv[1] == 'year':
        by_year = True
    if sys.argv[1] == 'since':
        filter_since = int(sys.argv[2])

df = pd.read_csv("data/pubs_sse.csv", sep=",", header=0)

stop = map(unicode, stopwords.words('english'))
graph = {}
graph_y = {}
people = []

pairs = {}

for i in df.index:
    pub = df.ix[i][0]
    author = df.ix[i][10]
    year = df.ix[i][7]
    
    if filter_since and int(year) < filter_since:
        continue
    
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
        print pair[0] + ";" + pair[1] + ";" + str(pair[2]) + ";"+ str(pairs[pair]/2)
        print pair[1] + ";" + pair[0] + ";" + str(pair[2]) + ";"+ str(pairs[pair]/2)
    else:
        print pair[0] + ";" + pair[1] + ";" + str(pairs[pair]/2)
        print pair[1] + ";" + pair[0] + ";" + str(pairs[pair]/2)