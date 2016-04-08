import pandas as pd
#import matplotlib.pyplot as plt


df = pd.read_csv("data/pubs_sse.csv", sep=",", header=0)

read = []
key_dict = {}
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
            if k not in key_dict:
                key_dict[k] = 1
            else:
                key_dict[k] += 1
            
            
data = []
for k in key_dict:
    if key_dict[k] > 3:
        data.append((key_dict[k], k))

data.sort()
data.reverse()

for oc, k in data:
    print str(k) + ";" + str(oc)