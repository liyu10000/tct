d = {(0, 1200): [0], (1000, 1600): [2], (1400, 2200): [1, 2], (1400, 2600): [1], (2800, 1400): [4]}
print(d)

#dd = sorted(d.items(), key=lambda x: len(x[1]), reverse=True)
dd = {key:value for key, value in d.items()}
print(dd)

to_delete = []
for key2, value2 in dd.items():
    for key, value in d.items():
        if key != key2 and set(value).issubset(set(value2)):
            to_delete.append(key)
            
print(to_delete)

for key in to_delete:
    if key in d:
        d.pop(key)
print(d)