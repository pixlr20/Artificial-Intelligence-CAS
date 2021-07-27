import random
d = {random.randint(0,10): random.randint(0,100) for n in range(50)}
print(d)
x = sorted(d, key=lambda x: d[x])
for key in x:
    print(str(key) + " " + str(d[key]))