import re
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

DSS = "ieee37.dss"
CSV = "IEEE37_BusXY.csv"
SAIDA = "ieee37_topologia"

# Barras com PV (so a localizacao esta definida)
pv_barras = {
    "728": "PV_1", "733": "PV_2", "737": "PV_3", "740": "PV_4",
    "718": "PV_5", "720": "PV_6", "722": "PV_7", "742": "PV_8",
}

# 1. Coordenadas
df = pd.read_csv(CSV, header=None, names=["Bus", "X", "Y"], skipinitialspace=True)
df["Bus"] = df["Bus"].astype(str).str.strip()
pos = {r.Bus: (r.X, r.Y) for r in df.itertuples()}

# 2. Le linhas e cargas do .dss
fase_nome = {"1.2": "AB", "2.3": "BC", "3.1": "CA"}
linhas, cargas = [], {}

with open(DSS) as f:
    for l in f:
        low = l.strip().lower()
        if low.startswith("new line."):
            b1 = re.search(r"bus1=(\S+)", l, re.I)
            b2 = re.search(r"bus2=(\S+)", l, re.I)
            lc = re.search(r"linecode=(\S+)", l, re.I)
            if b1 and b2 and lc:  # ignora o Jumper
                linhas.append((b1.group(1).split(".")[0],
                               b2.group(1).split(".")[0], lc.group(1)))
        elif low.startswith("new load."):
            bus1 = re.search(r"bus1=(\S+)", l, re.I).group(1)
            kw = float(re.search(r"kw=\s*([\d.]+)", l, re.I).group(1))
            partes = bus1.split(".")
            barra, nos = partes[0], ".".join(partes[1:])
            d = cargas.setdefault(barra, {"kw": 0.0, "fases": []})
            d["kw"] += kw
            d["fases"].append(fase_nome.get(nos, "ABC"))

# Tabela de cargas por barra (com as fases), pra usar no relatorio
tab = pd.DataFrame(
    [{"barra": b, "kw_total": d["kw"], "fases": "+".join(d["fases"])}
     for b, d in cargas.items()]
).sort_values("barra")
tab.to_csv(f"{SAIDA}_cargas.csv", index=False)

# 3. Figura
fig, ax = plt.subplots(figsize=(13, 10))
cores_cabo = {"721": "#333333", "722": "#1f77b4", "723": "#2ca02c", "724": "#ff7f0e"}

for a, b, lc in linhas:
    if a in pos and b in pos:
        ax.plot([pos[a][0], pos[b][0]], [pos[a][1], pos[b][1]],
                color=cores_cabo.get(lc, "gray"), lw=1.8, zorder=1)

# Equipamentos especiais (tracejado)
especiais = [("sourcebus", "799", "Trafo subestacao"),
             ("799", "799r", "Regulador"),
             ("709", "775", "Trafo XFM1")]
for a, b, nome in especiais:
    if a in pos and b in pos:
        ax.plot([pos[a][0], pos[b][0]], [pos[a][1], pos[b][1]],
                color="purple", ls="--", lw=2.2, zorder=1)

# Barras: tamanho proporcional a carga
for r in df.itertuples():
    kw = cargas.get(r.Bus, {}).get("kw", 0)
    cor = "lightcoral" if kw > 0 else "lightsteelblue"
    ax.scatter(r.X, r.Y, s=50 + kw * 0.7, c=cor, edgecolors="k",
               linewidths=0.6, zorder=2)
    ax.annotate(r.Bus, (r.X, r.Y), xytext=(6, 6), textcoords="offset points",
                fontsize=8, zorder=4)

# PVs: estrela dourada por cima
for barra, nome in pv_barras.items():
    if barra in pos:
        x, y = pos[barra]
        ax.scatter(x, y, s=420, marker="*", c="gold", edgecolors="k",
                   linewidths=1, zorder=5)
        ax.annotate(nome, (x, y), xytext=(8, -14), textcoords="offset points",
                    fontsize=8, fontweight="bold", color="darkgoldenrod", zorder=6)

# Fonte
if "799" in pos:
    ax.scatter(*pos["799"], s=200, marker="s", c="black", zorder=5)

# Legenda
leg = [Line2D([0], [0], color=c, lw=2.5, label=f"Linecode {k}") for k, c in cores_cabo.items()]
leg += [
    Line2D([0], [0], color="purple", ls="--", lw=2, label="Trafo / regulador"),
    Line2D([0], [0], marker="*", color="w", markerfacecolor="gold",
           markeredgecolor="k", markersize=16, label="PV (310 kW, 350 kVA)"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="lightcoral",
           markeredgecolor="k", markersize=9, label="Barra com carga (tamanho = kW)"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="lightsteelblue",
           markeredgecolor="k", markersize=9, label="Barra sem carga"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="black",
           markersize=10, label="Barra 799 (subestacao)"),
]
ax.legend(handles=leg, loc="best", fontsize=8, framealpha=0.9)

ax.set_title("IEEE 37 Barras: topologia, cargas e PVs (8 x 310 kW)")
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.grid(True, ls="--", alpha=0.4)
ax.set_aspect("equal", adjustable="datalim")
fig.tight_layout()

# 4. Exporta (antes do show)
fig.savefig(f"{SAIDA}.png", dpi=300, bbox_inches="tight")
fig.savefig(f"{SAIDA}.pdf", bbox_inches="tight")
print("Salvo:", f"{SAIDA}.png", f"{SAIDA}.pdf", f"{SAIDA}_cargas.csv")

plt.show()