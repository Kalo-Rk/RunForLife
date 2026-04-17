import csv
import matplotlib.pyplot as plt

it = []
hunters = []
runners = []
victoires = []
mortrun = []

with open("evolution.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        it.append(int(row["it"]))
        hunters.append(int(row["NbHunter"]))
        runners.append(int(row["NbRunner"]))
        victoires.append(int(row["NbWin"]))
        mortrun.append(int(row["MortRunner"]))

plt.plot(it, hunters, label="Chasseurs")
plt.plot(it, runners, label="Courreurs")
plt.plot(it, victoires, label="Victoires")
plt.plot(it, mortrun, label="MortRunner")

plt.xlabel("Itérations")
plt.ylabel("Population")
plt.title("Évolution durant course")
plt.legend()
plt.grid()

plt.show()