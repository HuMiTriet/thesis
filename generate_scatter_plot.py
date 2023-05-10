import json
import os
import matplotlib.pyplot as plt

# x: list[float] = [
#     0.01,
#     0.01,
#     0.01,
#     0.01,
#     0.02,
#     0.02,
#     0.02,
#     0.02,
#     0.03,
#     0.03,
#     0.03,
#     0.03,
#     0.04,
#     0.04,
#     0.04,
#     0.04,
#     0.05,
#     0.05,
#     0.05,
#     0.05,
#     0.06,
#     0.06,
#     0.06,
#     0.06,
#     0.07,
#     0.07,
#     0.07,
#     0.07,
#     0.08,
#     0.08,
#     0.08,
#     0.08,
#     0.09,
#     0.09,
#     0.09,
#     0.09,
#     0.1,
#     0.1,
#     0.1,
#     0.1,
# ]

x: list[float] = [
    0.01,
    0.02,
    0.03,
    0.04,
    0.05,
    0.06,
    0.07,
    0.08,
    0.09,
    0.1,
]

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

plt.xlabel("delay in seconds")
plt.ylabel("latency time (in seconds)")
plt.title("token ring with delay")

plt.show()
