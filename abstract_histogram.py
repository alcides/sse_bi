import pandas as pd
#import matplotlib.pyplot as plt

from nltk.corpus import stopwords


df = pd.read_csv("data/pubs_sse.csv", sep=",", header=0)

stop = map(unicode, stopwords.words('english'))
other_stop = ['de', 'also', 'one', 'two', 'even', 'e', 'may']

read = []
key_dict = {}

def add_key(k):
    if str(k) in map(str,stop) or k in other_stop:
        return
    if k not in key_dict:
        key_dict[k] = 1
    else:
        key_dict[k] += 1

for i in df.index:
    pub = df.ix[i][0]
    if pub in read:
        continue
    read.append(pub)
    
    keys = df.ix[i][5]
    if type(keys) != float:
        parts = keys.split(";")
        if len(parts) == 1:
            parts = keys.split(",")
        for k_ in parts:
            k = k_.strip().lower()
            if not k:
                continue
            add_key(k)
            
    keys = df.ix[i][3]
    if type(keys) != float:
        parts = keys.split(" ")
        for k_ in parts:
            k = k_.strip().lower()
            if not k:
                continue
            add_key(k)

            
data = []
for k in key_dict:
    if key_dict[k] > 50:
        data.append((key_dict[k], k))

data.sort()
data.reverse()

for oc, k in data:
    print "%s;%d" % (k, oc)