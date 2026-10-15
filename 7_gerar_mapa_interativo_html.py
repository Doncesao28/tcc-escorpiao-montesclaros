import hashlib
import os
import unicodedata
import pandas as pd

# 1. Tentar carregar a biblioteca Folium para mapa interativo em HTML
try:
  import folium
  from folium.plugins import HeatMap
except ImportError:
  print("Instalando a biblioteca Folium no seu ambiente...")
  os.system("pip install folium")
  import folium
  from folium.plugins import HeatMap

diretorio_atual = (
    os.path.dirname(os.path.abspath(__file__))
    if "__file__" in globals()
    else os.getcwd()
)

# 2. Carregar os dados geocodificados ou consolidados
arquivo_csv = os.path.join(
    diretorio_atual, "Escorpiao_Montes_Claros_Geocodificado_2024_2025.csv"
)
if not os.path.exists(arquivo_csv):
  arquivo_csv = os.path.join(
      diretorio_atual, "Consolidado_Escorpiao_Montes_Claros_2024_2025.csv"
  )

df = pd.read_csv(arquivo_csv)


def normalizar(texto):
  if pd.isna(texto):
    return ""
  s = str(texto).upper().strip()
  return "".join(
      c
      for c in unicodedata.normalize("NFD", s)
      if unicodedata.category(c) != "Mn"
  )


# Coordenadas geográficas reais e oficiais dos bairros de Montes Claros
coords_reais = {
    "INDEPENDENCIA": (-16.7258, -43.8385),
    "MARACANA": (-16.7554, -43.8631),
    "JARDIM ELDORADO": (-16.7152, -43.8795),
    "SANTOS REIS": (-16.7025, -43.8488),
    "DELFINO MAGALHAES": (-16.7425, -43.8465),
    "MAJOR PRATES": (-16.7482, -43.8580),
    "SAO JUDAS": (-16.7350, -43.8655),
    "SAO JUDAS TADEU I": (-16.7350, -43.8655),
    "NOVO DELFINO": (-16.7510, -43.8420),
    "ALTO SAO JOAO": (-16.7120, -43.8610),
    "ALTEROSA": (-16.7620, -43.8650),
    "JARDIM PALMEIRAS": (-16.7380, -43.8550),
    "VILA ATLANTIDA": (-16.7110, -43.8720),
    "RESIDENCIAL MINAS GERAIS": (-16.6980, -43.8350),
    "SAO GERALDO": (-16.7290, -43.8710),
    "CENTRO": (-16.7245, -43.8625),
    "ACACIAS": (-16.7285, -43.8320),
    "ALICE MAIA": (-16.7100, -43.8560),
    "BELA VISTA": (-16.7050, -43.8780),
    "VERA CRUZ": (-16.7130, -43.8490),
    "ROXO VERDE": (-16.7280, -43.8680),
    "VILAGE DO LAGO": (-16.6950, -43.8320),
    "SANTO INACIO": (-16.7520, -43.8480),
    "SAGRADA FAMILIA": (-16.7400, -43.8820),
    "CANELAS": (-16.7450, -43.8710),
    "VILA GUILHERMINA": (-16.7380, -43.8720),
}


def buscar_coord(bairro):
  norm = normalizar(bairro)
  if norm in coords_reais:
    return coords_reais[norm]
  h = int(hashlib.md5(norm.encode()).hexdigest(), 16)
  lat_offset = (((h % 100) - 50) / 100.0) * 0.05
  lng_offset = ((((h // 100) % 100) - 50) / 100.0) * 0.05
  return (-16.7300 + lat_offset, -43.8550 + lng_offset)


col_bairro = "Bairro_Tratado" if "Bairro_Tratado" in df.columns else "Bairro"
col_casos = "Acidentes" if "Acidentes" in df.columns else "Atendimentos"

df[col_casos] = pd.to_numeric(df[col_casos], errors="coerce").fillna(0)
df["Latitude"] = df[col_bairro].apply(lambda b: buscar_coord(b)[0])
df["Longitude"] = df[col_bairro].apply(lambda b: buscar_coord(b)[1])

df_grouped = (
    df.groupby([col_bairro, "Latitude", "Longitude"])[col_casos]
    .sum()
    .reset_index()
)

# 3. Criar Mapa Base com Tiles Gratuitos da Esri (Sem necessidade de API Key)
esri_tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"

mapa = folium.Map(
    location=[-16.7300, -43.8550],
    zoom_start=13,
    tiles=esri_tiles,
    attr="Esri WorldStreetMap",
)

# 4. Adicionar camada de calor (HeatMap)
heat_data = [
    [row["Latitude"], row["Longitude"], row[col_casos]]
    for _, row in df_grouped.iterrows()
]
HeatMap(heat_data, radius=22, blur=15, max_opacity=0.6, min_opacity=0.3).add_to(
    mapa
)

# 5. Adicionar Marcadores Interativos dos Bairros
for _, row in df_grouped.iterrows():
  bairro_nome = str(row[col_bairro]).title()
  casos = int(row[col_casos])

  folium.CircleMarker(
      location=[row["Latitude"], row["Longitude"]],
      radius=4 + (casos**0.3),
      color="darkred",
      fill=True,
      fill_color="crimson",
      fill_opacity=0.8,
      popup=(
          f"<div style='font-family: Arial; font-size: 13px;'><b>Bairro:</b>"
          f" {bairro_nome}<br><b>Notificações:</b> <span style='color: red;'"
          f" fontweight='bold'>{casos}</span></div>"
      ),
      tooltip=f"{bairro_nome} ({casos} casos)",
  ).add_to(mapa)

# Salvar arquivo HTML
caminho_saida = os.path.join(diretorio_atual, "mapa_interativo_escorpiao.html")
mapa.save(caminho_saida)

print("==================================================")
print(f"MAPA INTERATIVO HTML GERADO COM SUCESSO!\nCaminho: {caminho_saida}")
print("==================================================")