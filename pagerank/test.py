import random

pd = dict()
pd[1] = 0.25
pd[2] = 0.25
pd[11] = 0.5
el_count = 0
two_count = 0
print(type(pd.keys()))
for i in range(1000):
    choice = random.choices(population=pd.keys(), weights=pd.values())[0]
    if choice == 11 :
        el_count = el_count + 1
    elif choice == 2:
        two_count = two_count + 1

print(el_count)
print(two_count)
print(pd.items())