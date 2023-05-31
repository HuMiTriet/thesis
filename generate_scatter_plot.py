import json
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from numpy import size
import numpy as np

ALGORITHM_NAME = "ricart_agrawala"

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


# x: list[float] = [
#     0.01,
#     0.02,
#     0.03,
#     0.04,
#     0.05,
#     0.06,
#     0.07,
#     0.08,
#     0.09,
#     0.1,
#     0.11,
#     0.12,
#     0.13,
#     0.14,
#     0.15,
#     0.16,
#     0.17,
#     0.18,
#     0.19,
#     0.2,
# ]


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
# x = x * TIME


plt.style.use("seaborn")

plt.tight_layout()

with open(
    os.path.join(f"{ALGORITHM_NAME}_median.json"),
    "r",
    encoding="utf-8"
    # os.path.join(f"{ALGORITHM_NAME}.json"), "r", encoding="utf-8",
) as file:
    data = json.loads(file.read())

x = [float(point["delay_time"]) for point in data]
y = [float(point["latency"]) for point in data]
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
plt.title(f"{ALGORITHM_NAME} algorithm with delay (run {TIME} times)")

m, b = np.polyfit(x, y, 1)

plt.plot(
    x,
    m * np.array(x) + b,
    color="red",
    linewidth=2,
    label=f"{ALGORITHM_NAME} slope = {m} and bias is {b}",
)

# with open(
#     os.path.join("ricart_agrawala_median.json"), "r", encoding="utf-8"
# ) as file:
#     y_ricart = json.loads(file.read())

# plt.scatter(x, y_ricart, edgecolors="black", c="black")

# m_2, b_2 = np.polyfit(x, y_ricart, 1)

# plt.plot(
#     x,
#     m_2 * np.array(x) + b_2,
#     color="green",
#     linewidth=2,
#     label=f"ricart slope = {m_2} and bias is {b_2}",
# )

# with open(os.path.join("maekawa_median.json"), "r", encoding="utf-8") as file:
#     y_maekawa = json.loads(file.read())

# plt.scatter(x, y_maekawa, edgecolors="black", c="yellow")

# m_3, b_3 = np.polyfit(x, y_maekawa, 1)

# plt.plot(
#     x,
#     m_3 * np.array(x) + b_3,
#     color="blue",
#     linewidth=2,
#     label=f"maekawa slope = {m_3} and bias is {b_3}",
# )

plt.legend(loc="lower right")
plt.show()
