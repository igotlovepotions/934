import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("IEEE37_BusXY.csv")

plt.figure(figsize=(10, 8))
plt.scatter(df['X'], df['Y'], c='red', s=50)
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.title('IEEE 37 Bus Network')
plt.grid(True)
plt.show()
