import io
import os
import contextily as cx
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

diretorio_atual = (
    os.path.dirname(os.path.abspath(__file__))
    if "__file__" in globals()
    else os.getcwd()
)
pasta_saida = os.path.join(diretorio_atual, "Mapas_Gerados")
os.makedirs(pasta_saida, exist_ok=True)

arquivo_csv = os.path.join(
    diretorio_atual, "Escorpiao_Montes_Claros_Geocodificado_2024_2025.csv"
)
df = pd.read_csv(arquivo_csv)
df_valid = df.dropna(subset=["Latitude", "Longitude"])

meses_nome_arquivo = {
    1: "01_Janeiro",
    2: "02_Fevereiro",
    3: "03_Marco",
    4: "04_Abril",
    5: "05_Maio",
    6: "06_Junho",
    7: "07_Julho",
    8: "08_Agosto",
    9: "09_Setembro",
    10: "10_Outubro",
    11: "11_Novembro",
    12: "12_Dezembro",
}

meses_nome_titulo = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}


def gerar_mapa_individual(df_filtrado, titulo, filename):
  if df_filtrado.empty or df_filtrado["Acidentes"].sum() == 0:
    print(f"Sem dados para: {titulo}")
    return

  df_grouped = (
      df_filtrado.groupby(["Bairro_Tratado", "Latitude", "Longitude"])[
          "Acidentes"
      ]
      .sum()
      .reset_index()
  )

  fig, ax = plt.subplots(figsize=(11, 9))

  # 1. Camada de calor (KDE)
  try:
    sns.kdeplot(
        data=df_grouped,
        x="Longitude",
        y="Latitude",
        weights="Acidentes",
        cmap="Reds",
        fill=True,
        thresh=0.08,
        alpha=0.6,
        levels=14,
        ax=ax,
    )
  except Exception:
    pass

  # 2. Pontos dos bairros
  scatter = ax.scatter(
      df_grouped["Longitude"],
      df_grouped["Latitude"],
      s=df_grouped["Acidentes"] * 4.5,
      c=df_grouped["Acidentes"],
      cmap="Reds",
      alpha=0.8,
      edgecolors="black",
      linewidth=0.5,
      zorder=3,
  )

  # 3. Mapa base limpo da Esri WorldStreetMap (Sem API Key necessária)
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

  # 4. Apenas o nome do bairro limpo sobre o ponto
  for _, r in df_grouped.iterrows():
    ax.text(
        r["Longitude"],
        r["Latitude"],
        r["Bairro_Tratado"].title(),
        fontsize=7.5,
        fontweight="bold",
        color="#111111",
        ha="center",
        va="center",
        zorder=5,
        bbox=dict(
            boxstyle="round,pad=0.15",
            facecolor="white",
            edgecolor="none",
            alpha=0.65,
        ),
    )

  # Barra de cores
  cbar = fig.colorbar(scatter, ax=ax, shrink=0.75, pad=0.03)
  cbar.set_label("N° de Acidentes", fontsize=10, fontweight="bold")

  # Título e eixos
  total_casos = int(df_grouped["Acidentes"].sum())
  ax.set_title(
      f"{titulo} — Total: {total_casos:,} Casos".replace(",", "."),
      fontsize=12,
      fontweight="bold",
      pad=12,
  )
  ax.set_xlabel("Longitude", fontsize=9, fontweight="bold")
  ax.set_ylabel("Latitude", fontsize=9, fontweight="bold")
  ax.grid(True, linestyle=":", alpha=0.3)

  # 5. Caixa com Top 5 Bairros com Mais Ocasiões
  top5 = df_grouped.sort_values(by="Acidentes", ascending=False).head(5)
  txt_top5 = "Top 5 Bairros com Mais Ocasiões:\n" + "\n".join([
      f"{i}. {r['Bairro_Tratado'].title()} ({int(r['Acidentes'])} casos)"
      for i, (_, r) in enumerate(top5.iterrows(), 1)
  ])

  ax.text(
      0.02,
      0.02,
      txt_top5.strip(),
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

  # 6. Salvamento via memória RAM (Evita erro 22 do Windows)
  buf = io.BytesIO()
  plt.savefig(buf, format="png", dpi=200, bbox_inches="tight")
  plt.close(fig)
  buf.seek(0)

  caminho_arquivo = os.path.join(pasta_saida, filename)
  with open(caminho_arquivo, "wb") as f:
    f.write(buf.getvalue())
  buf.close()

  print(f"Gerado com sucesso: {filename}")


# --- EXECUÇÃO PRINCIPAL ---
print("\n--- Gerando mapas mensais de 2024 ---")
for mes_num in range(1, 13):
  df_mes = df_valid[(df_valid["Ano"] == 2024) & (df_valid["Mês_Num"] == mes_num)]
  gerar_mapa_individual(
      df_mes,
      f"Montes Claros - {meses_nome_titulo[mes_num]} de 2024",
      f"2024_{meses_nome_arquivo[mes_num]}.png",
  )

print("\n--- Gerando mapa TOTAL CONSOLIDADO DE 2024 ---")
df_2024_total = df_valid[df_valid["Ano"] == 2024]
gerar_mapa_individual(
    df_2024_total,
    "Montes Claros - Total Acumulado em 2024",
    "2024_13_TOTAL_CONSOLIDADO.png",
)

print("\n--- Gerando mapas mensais de 2025 ---")
for mes_num in range(1, 13):
  df_mes = df_valid[(df_valid["Ano"] == 2025) & (df_valid["Mês_Num"] == mes_num)]
  gerar_mapa_individual(
      df_mes,
      f"Montes Claros - {meses_nome_titulo[mes_num]} de 2025",
      f"2025_{meses_nome_arquivo[mes_num]}.png",
  )

print("\n--- Gerando mapa TOTAL CONSOLIDADO DE 2025 ---")
df_2025_total = df_valid[df_valid["Ano"] == 2025]
gerar_mapa_individual(
    df_2025_total,
    "Montes Claros - Total Acumulado em 2025",
    "2025_13_TOTAL_CONSOLIDADO.png",
)

print("\n==================================================")
print(f"PROCESSO CONCLUÍDO! Os 26 mapas foram salvos em: '{pasta_saida}'")
print("==================================================")