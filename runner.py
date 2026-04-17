import csv
import matplotlib.pyplot as plt

it = []
runners = []
smart = []
notsmart = []

with open("nbrunner.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        it.append(int(row["it"]))
        runners.append(int(row["NbRunner"]))
        smart.append(int(row["nbSmart"]))
        notsmart.append(int(row["nbNotSmart"]))

plt.plot(it, runners, label="Courreurs")
plt.plot(it, smart, label="NbSmart")
plt.plot(it, notsmart, label="NbNotSmart")

plt.xlabel("Itérations")
plt.ylabel("Population")
plt.title("Évolution des coureurs")
plt.legend()
plt.grid()

plt.show()