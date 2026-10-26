import matplotlib.pyplot as plt
import pandas as pd
import re

# 1. Carrega as coordenadas das barras
df_coords = pd.read_csv(
    "IEEE37_BusXY.csv",
    header=None,
    names=["Bus", "X", "Y"],
    skipinitialspace=True,
)
# Remove espaços extras dos nomes das barras para garantir o match
df_coords["Bus"] = df_coords["Bus"].astype(str).str.strip()
pos_dict = {row["Bus"]: (row["X"], row["Y"]) for _, row in df_coords.iterrows()}

# 2. Extrai as conexões das linhas direto do ieee37.dss (ou lista manual)
lines_data = [
    ("701.1.2.3", "702.1.2.3"), ("702.1.2.3", "705.1.2.3"), ("702.1.2.3", "713.1.2.3"),
    ("702.1.2.3", "703.1.2.3"), ("703.1.2.3", "727.1.2.3"), ("703.1.2.3", "730.1.2.3"),
    ("704.1.2.3", "714.1.2.3"), ("704.1.2.3", "720.1.2.3"), ("705.1.2.3", "742.1.2.3"),
    ("705.1.2.3", "712.1.2.3"), ("706.1.2.3", "725.1.2.3"), ("707.1.2.3", "724.1.2.3"),
    ("707.1.2.3", "722.1.2.3"), ("708.1.2.3", "733.1.2.3"), ("708.1.2.3", "732.1.2.3"),
    ("709.1.2.3", "731.1.2.3"), ("709.1.2.3", "708.1.2.3"), ("710.1.2.3", "735.1.2.3"),
    ("710.1.2.3", "736.1.2.3"), ("711.1.2.3", "741.1.2.3"), ("711.1.2.3", "740.1.2.3"),
    ("713.1.2.3", "704.1.2.3"), ("714.1.2.3", "718.1.2.3"), ("720.1.2.3", "707.1.2.3"),
    ("720.1.2.3", "706.1.2.3"), ("727.1.2.3", "744.1.2.3"), ("730.1.2.3", "709.1.2.3"),
    ("733.1.2.3", "734.1.2.3"), ("734.1.2.3", "737.1.2.3"), ("734.1.2.3", "710.1.2.3"),
    ("737.1.2.3", "738.1.2.3"), ("738.1.2.3", "711.1.2.3"), ("744.1.2.3", "728.1.2.3"),
    ("744.1.2.3", "729.1.2.3"), ("799r.1.2.3", "701.1.2.3"), ("799.1.2", "799r.1.2"),
    ("799.3.2", "799r.3.2"), ("799.2", "799r.2")
]

plt.figure(figsize=(12, 10))

# 3. Desenha as linhas (arestas)
for b1, b2 in lines_data:
    # Remove sufixos de fase para buscar a coordenada base se necessário
    clean_b1 = b1.split('.')[0]
    clean_b2 = b2.split('.')[0]
    if clean_b1 in pos_dict and clean_b2 in pos_dict:
        x1, y1 = pos_dict[clean_b1]
        x2, y2 = pos_dict[clean_b2]
        plt.plot([x1, x2], [y1, y2], color='gray', linestyle='-', linewidth=1.2, zorder=1)

# 4. Desenha as barras (nós)
plt.scatter(df_coords["X"], df_coords["Y"], c="red", s=60, zorder=2)

for _, row in df_coords.iterrows():
    plt.text(row["X"], row["Y"], str(row["Bus"]), fontsize=8, ha="left", va="bottom", zorder=3)

plt.xlabel("X Coordinate")
plt.ylabel("Y Coordinate")
plt.title("IEEE 37 Bus Network - Topologia e Coordenadas")
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()