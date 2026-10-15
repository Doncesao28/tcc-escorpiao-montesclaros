import contextily as cx
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 1. Carregar os dados geocodificados
input_csv = "Escorpiao_Montes_Claros_Geocodificado_2024_2025.csv"
df = pd.read_csv(input_csv)

# Filtrar apenas registros válidos com coordenadas
df_valid = df.dropna(subset=["Latitude", "Longitude"])

# Agrupar por bairro
df_grouped = (
    df_valid.groupby(["Bairro_Tratado", "Latitude", "Longitude"])["Acidentes"]
    .sum()
    .reset_index()
)

# 2. Configurar a figura
fig, ax = plt.subplots(figsize=(11, 9))

# 3. Gerar a camada de Densidade / Calor (KDEplot)
sns.kdeplot(
    data=df_grouped,
    x="Longitude",
    y="Latitude",
    weights="Acidentes",
    cmap="Reds",
    fill=True,
    thresh=0.08,
    alpha=0.65,
    levels=15,
    ax=ax,
)

# 4. Adicionar os pontos dos bairros
scatter = ax.scatter(
    df_grouped["Longitude"],
    df_grouped["Latitude"],
    s=df_grouped["Acidentes"] * 3.5,  # Tamanho da bolha
    c=df_grouped["Acidentes"],  # Cor proporcional
    cmap="Reds",
    alpha=0.85,
    edgecolors="darkred",
    linewidth=0.8,
)

# Barra de cores lateral
cbar = plt.colorbar(scatter, ax=ax, shrink=0.75)
cbar.set_label("Soma de N° Acidentes", fontsize=11, fontweight="bold")

# 5. Adicionar o mapa base da Esri (Sem marca d'água "API KEY REQUIRED")
try:
  cx.add_basemap(
      ax,
      crs="EPSG:4326",
      source=cx.providers.Esri.WorldStreetMap,
      alpha=0.85,
  )
except Exception as e:
  print(f"Aviso mapa base: {e}")

# 6. Adicionar apenas o Top 5 Bairros com posições deslocadas para não encavalar o texto
top_bairros = df_grouped.sort_values(by="Acidentes", ascending=False).head(6)

# Deslocamentos manuais leves para afastar os textos uns dos outros
offsets = {
    "INDEPENDÊNCIA": (0.003, 0.002),
    "MARACANÃ": (-0.005, -0.003),
    "JARDIM ELDORADO": (-0.006, 0.002),
    "SANTOS REIS": (0.004, 0.003),
    "DELFINO MAGALHÃES": (0.004, -0.003),
    "MAJOR PRATES": (-0.006, -0.004),
}

for _, row in top_bairros.iterrows():
  b_nome = row["Bairro_Tratado"]
  dx, dy = offsets.get(b_nome, (0.002, 0.002))

  ax.annotate(
      f"{b_nome} ({int(row['Acidentes'])})",
      xy=(row["Longitude"], row["Latitude"]),
      xytext=(row["Longitude"] + dx, row["Latitude"] + dy),
      fontsize=8.5,
      fontweight="bold",
      color="black",
      bbox=dict(
          boxstyle="round,pad=0.2", fc="white", ec="darkred", lw=0.8, alpha=0.85
      ),
      arrowprops=dict(
          arrowstyle="->", connectionstyle="arc3,rad=0", color="darkred", lw=0.7
      ),
  )

# Título e eixos
plt.title(
    "Mapeamento de Picadas de Escorpião em Montes Claros - MG (2024–2025)",
    fontsize=12,
    fontweight="bold",
    pad=15,
)
plt.xlabel("Longitude", fontsize=10)
plt.ylabel("Latitude", fontsize=10)
plt.grid(True, linestyle="--", alpha=0.3)

# 7. Salvar imagem PNG em alta resolução
output_png = "Mapa_Calor_Escorpiao_Montes_Claros_Limpo.png"
plt.savefig(output_png, dpi=300, bbox_inches="tight")
plt.close()

print("==================================================")
print(f"IMAGEM PNG GERADA: {output_png}")
print("==================================================")