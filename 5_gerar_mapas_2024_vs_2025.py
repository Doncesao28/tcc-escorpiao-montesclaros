import contextily as cx
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 1. Carregar os dados geocodificados
input_csv = "Escorpiao_Montes_Claros_Geocodificado_2024_2025.csv"
df = pd.read_csv(input_csv)
df_valid = df.dropna(subset=["Latitude", "Longitude"])

# Agrupar por ano e bairro
df_2024 = (
    df_valid[df_valid["Ano"] == 2024]
    .groupby(["Bairro_Tratado", "Latitude", "Longitude"])["Acidentes"]
    .sum()
    .reset_index()
)
df_2025 = (
    df_valid[df_valid["Ano"] == 2025]
    .groupby(["Bairro_Tratado", "Latitude", "Longitude"])["Acidentes"]
    .sum()
    .reset_index()
)

# Configurar figura com 2 mapas lado a lado
fig, axes = plt.subplots(1, 2, figsize=(18, 10), sharex=True, sharey=True)

# Posições de deslocamento (offsets) direcionadas para cada bairro não encavalar
offsets = {
    "INDEPENDÊNCIA": (0.012, -0.008),  # Aponta para o canto inferior direito
    "MARACANÃ": (-0.018, -0.012),  # Aponta para o canto inferior esquerdo
    "JARDIM ELDORADO": (-0.022, 0.010),  # Aponta para o canto superior esquerdo
    "SANTOS REIS": (0.008, 0.015),  # Aponta para cima
    "DELFINO MAGALHÃES": (0.018, 0.005),  # Aponta para a direita
    "MAJOR PRATES": (-0.020, 0.002),  # Aponta para a esquerda
    "SÃO JUDAS TADEU I": (-0.015, -0.005),
}


def plot_mapa_perfeito(df_ano, ax, ano):
  # 1. Camada de Calor (KDEPlot)
  sns.kdeplot(
      data=df_ano,
      x="Longitude",
      y="Latitude",
      weights="Acidentes",
      cmap="Reds",
      fill=True,
      thresh=0.06,
      alpha=0.55,
      levels=15,
      ax=ax,
  )

  # 2. Pontos Proporcionais
  scatter = ax.scatter(
      df_ano["Longitude"],
      df_ano["Latitude"],
      s=df_ano["Acidentes"] * 4.5,
      c=df_ano["Acidentes"],
      cmap="Reds",
      alpha=0.85,
      edgecolors="darkred",
      linewidth=0.8,
      zorder=3,
  )

  # 3. Adicionar o Mapa Base da Esri (limpo)
  try:
    cx.add_basemap(
        ax,
        crs="EPSG:4326",
        source=cx.providers.Esri.WorldStreetMap,
        alpha=0.75,
        attribution="",
    )
  except Exception:
    pass

  # 4. Rótulos apontando para os Bairros do Top 5 com Setas
  top5 = df_ano.sort_values(by="Acidentes", ascending=False).head(5)
  for _, r in top5.iterrows():
    b_nome = r["Bairro_Tratado"]
    dx, dy = offsets.get(b_nome, (0.010, 0.008))

    ax.annotate(
        f"{b_nome}\n({int(r['Acidentes'])} casos)",
        xy=(r["Longitude"], r["Latitude"]),
        xytext=(r["Longitude"] + dx, r["Latitude"] + dy),
        fontsize=8.5,
        fontweight="bold",
        color="black",
        ha="center",
        va="center",
        bbox=dict(
            boxstyle="round,pad=0.3",
            fc="white",
            ec="darkred",
            lw=0.8,
            alpha=0.9,
        ),
        arrowprops=dict(
            arrowstyle="->",
            connectionstyle="arc3,rad=0",
            color="darkred",
            lw=0.9,
        ),
        zorder=5,
    )

  # 5. Título e Ajustes dos Eixos
  total = int(df_ano["Acidentes"].sum())
  ax.set_title(
      f"Ano de {ano} — Total: {total:,} Casos".replace(",", "."),
      fontsize=13,
      fontweight="bold",
      pad=12,
  )
  ax.set_xlabel("Longitude", fontsize=10, fontweight="bold")
  ax.set_ylabel("Latitude", fontsize=10, fontweight="bold")
  ax.grid(True, linestyle=":", alpha=0.4)

  # 6. Caixa de Legenda Resumo formatada com \n (Sem tags HTML de <br>)
  txt_legenda = f"Top 5 Bairros ({ano}):\n"
  for i, (_, r) in enumerate(top5.iterrows(), 1):
    txt_legenda += f"{i}. {r['Bairro_Tratado']}: {int(r['Acidentes'])} casos\n"

  # Caixa no canto inferior esquerdo
  ax.text(
      0.02,
      0.02,
      txt_legenda.strip(),
      transform=ax.transAxes,
      fontsize=8.5,
      verticalalignment="bottom",
      bbox=dict(
          boxstyle="round,pad=0.5",
          facecolor="white",
          edgecolor="darkred",
          alpha=0.92,
          linewidth=1,
      ),
      zorder=6,
  )

  return scatter


# Gerar os dois anos
scatter1 = plot_mapa_perfeito(df_2024, axes[0], "2024")
scatter2 = plot_mapa_perfeito(df_2025, axes[1], "2025")

# Barra de Cores Lateral
cbar = fig.colorbar(scatter2, ax=axes.ravel().tolist(), shrink=0.75, pad=0.02)
cbar.set_label("N° de Acidentes por Bairro", fontsize=11, fontweight="bold")

# Título Geral do Gráfico
plt.suptitle(
    "Mapeamento Espacial das Picadas de Escorpião em Montes Claros - MG (2024 vs"
    " 2025)",
    fontsize=15,
    fontweight="bold",
    y=0.98,
)

# Salvar com Alta Qualidade
output_png = "Comparativo_Escorpiao_Montes_Claros_Perfeito.png"
plt.savefig(output_png, dpi=300, bbox_inches="tight")
plt.close()

print("==================================================")
print(f"IMAGEM PERFEITA GERADA COM SUCESSO: {output_png}")
print("==================================================")