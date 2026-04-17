import csv
import matplotlib.pyplot as plt

it = []
mortrun = []
mortfroid = []
mortfeu = []
mortparhunt = []
mortsmart = []
mortnotsmart = []

with open("décès.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        it.append(int(row["it"]))
        mortrun.append(int(row["MortRunner"]))
        mortfroid.append(int(row["MortFroid"]))
        mortfeu.append(int(row["MortFeu"]))
        mortparhunt.append(int(row["MortParHunt"]))
        mortsmart.append(int(row["MortSmart"]))
        mortnotsmart.append(int(row["MortNotSmart"]))

plt.plot(it, mortrun, label="MortRunner")
plt.plot(it, mortfroid, label="MortFroid")
plt.plot(it, mortfeu, label="MortFeu")
plt.plot(it, mortparhunt, label="MortParHunt")
plt.plot(it, mortsmart, label="MortSmart")
plt.plot(it, mortnotsmart, label="MortNotSmart")

plt.xlabel("Itérations")
plt.ylabel("Population")
plt.title("Mort durant la course")
plt.legend()
plt.grid()

plt.show()