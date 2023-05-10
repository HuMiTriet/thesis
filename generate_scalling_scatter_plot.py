import json
import os
import matplotlib.pyplot as plt

x: list[float] = [
    4,
    4,
    4,
    4,
    5,
    5,
    5,
    5,
    6,
    6,
    6,
    6,
    7,
    7,
    7,
    7,
    8,
    8,
    8,
    8,
    9,
    9,
    9,
    9,
    10,
    10,
    10,
    10,
    11,
    11,
    11,
    11,
    12,
    12,
    12,
    12,
    13,
    13,
    13,
    13,
]

# x: list[float] = [
#     4,
#     5,
#     6,
#     7,
#     8,
#     9,
#     10,
#     11,
#     12,
#     13,
# ]

y: list[float] = []

plt.style.use("seaborn")

plt.tight_layout()

with open(os.path.join("result.json"), "r", encoding="utf-8") as file:
    y = json.loads(file.read())

plt.scatter(
    x,
    y,
    edgecolors="black",
)

plt.xlabel("number of nodes")
plt.ylabel("latency time (in seconds)")
plt.title("Ricart Agrawala with increasing number of client")

plt.show()
