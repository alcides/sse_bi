import pandas as pd
from nltk.stem.snowball import EnglishStemmer

stemmer = EnglishStemmer()

df = pd.read_csv("data/pubs_sse.csv", sep=",", header=0)

clas = map( lambda x: (x, stemmer.stem(x)), map(lambda x: type(x) == str and x.lower().strip().decode('utf-8') or u"", open("data/acm_categories.txt", 'r').readlines()))

read = []
histogram = {}

def add_key(k):
    if k not in histogram:
        histogram[k] = 1
    else:
        histogram[k] += 1


pubs = []
for i in df.index:
    pub = df.ix[i][0]
    if pub in pubs:
        continue
    pubs.append(pub)
    
    abstract = df.ix[i][3]
    keys = df.ix[i][5]
    year = df.ix[i][7]

    keys = type(keys) == str and keys.decode('utf-8').lower() or ""
    abstract = type(abstract) == str and abstract.decode('utf-8').lower() or ""    
    
    for cl, cl_s in clas:
        if cl in keys:
            add_key((cl, year))
            continue
        if cl in abstract:
            add_key((cl, year))
            continue
        if cl_s in stemmer.stem(abstract):
            add_key((cl, year))
            continue
                
for k in histogram:
    print "%s;%d;%s" % (k[0], k[1], histogram[k])
    