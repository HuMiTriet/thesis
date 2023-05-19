import json
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from numpy import size
import numpy as np

ALGORITHM_NAME = "token_ring"

TIME = 10

colors = [
    "black",
    "red",
    "yellow",
    "green",
    "black",
    "red",
    "yellow",
    "green",
    "black",
    "red",
    "yellow",
    "green",
    "black",
    "red",
    "yellow",
    "green",
    "black",
    "red",
    "yellow",
    "green",
    "black",
    "red",
    "yellow",
    "green",
    "black",
    "red",
    "yellow",
    "green",
    "black",
    "red",
    "yellow",
    "green",
    "black",
    "red",
    "yellow",
    "green",
    "black",
    "red",
    "yellow",
    "green",
    "black",
    "red",
    "yellow",
    "green",
    "black",
    "red",
    "yellow",
    "green",
    "black",
    "red",
    "yellow",
    "green",
    "black",
    "red",
    "yellow",
    "green",
    "black",
    "red",
    "yellow",
    "green",
    "black",
    "red",
    "yellow",
    "green",
    "black",
    "red",
    "yellow",
    "green",
    "black",
    "red",
    "yellow",
    "green",
    "black",
    "red",
    "yellow",
    "green",
    "black",
    "red",
    "yellow",
    "green",
]


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
    0.11,
    0.12,
    0.13,
    0.14,
    0.15,
    0.16,
    0.17,
    0.18,
    0.19,
    0.2,
]


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
#     0.11,
#     0.11,
#     0.11,
#     0.11,
#     0.12,
#     0.12,
#     0.12,
#     0.12,
#     0.13,
#     0.13,
#     0.13,
#     0.13,
#     0.14,
#     0.14,
#     0.14,
#     0.14,
#     0.15,
#     0.15,
#     0.15,
#     0.15,
#     0.16,
#     0.16,
#     0.16,
#     0.16,
#     0.17,
#     0.17,
#     0.17,
#     0.17,
#     0.18,
#     0.18,
#     0.18,
#     0.18,
#     0.19,
#     0.19,
#     0.19,
#     0.19,
#     0.2,
#     0.2,
#     0.2,
#     0.2,
# ]

colors = colors * TIME
x = x * TIME

y: list[float] = []

plt.style.use("seaborn")

plt.tight_layout()

with open(
    os.path.join(f"{ALGORITHM_NAME}_median.json"), "r", encoding="utf-8"
) as file:
    y = json.loads(file.read())

print(f"size of x {size(x)} size of y {size(y)}")

plt.scatter(
    x,
    y,
    edgecolors="black",
    # c=colors,
    # cmap="Greens",
)


plt.xlabel("delay in seconds")
plt.ylabel("median latency time (in seconds)")
plt.title(f"{ALGORITHM_NAME} with delay (run {TIME} times)")

m, b = np.polyfit(x, y, 1)

plt.plot(
    x,
    m * np.array(x) + b,
    color="red",
    linewidth=2,
    label=f"slope = {m} and bias is {b}",
)

plt.legend(loc="lower right")
plt.show()
