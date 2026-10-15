import folium
from folium.plugins import HeatMap
import pandas as pd

# 1. Carregar os dados geocodificados
input_csv = "Escorpiao_Montes_Claros_Geocodificado_2024_2025.csv"
df = pd.read_csv(input_csv)

# Filtrar apenas bairros com coordenadas válidas
df_valid = df.dropna(subset=["Latitude", "Longitude"])

# Agrupar por bairro e somar o total de acidentes
df_grouped = (
    df_valid.groupby(["Bairro_Tratado", "Latitude", "Longitude"])["Acidentes"]
    .sum()
    .reset_index()
)

# 2. Centrar o mapa na cidade de Montes Claros - MG
center_lat = -16.7282
center_lng = -43.8578

# Utilizar o servidor Esri WorldStreetMap (Livre, sem chave e sem marca de água)
mapa = folium.Map(
    location=[center_lat, center_lng],
    zoom_start=13,
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    attr="Esri, USGS, NOAA",
)

# 3. Gerar a camada de Mapa de Calor (Heatmap)
heat_data = [
    [row["Latitude"], row["Longitude"], row["Acidentes"]]
    for _, row in df_grouped.iterrows()
]
HeatMap(
    heat_data,
    radius=22,
    blur=15,
    max_zoom=1,
    gradient={0.2: "blue", 0.4: "lime", 0.6: "yellow", 1: "red"},
).add_to(mapa)

# 4. Adicionar marcadores interativos nos bairros
for _, row in df_grouped.iterrows():
  folium.CircleMarker(
      location=[row["Latitude"], row["Longitude"]],
      radius=5,
      popup=(
          f"<b>Bairro:</b> {row['Bairro_Tratado']}<br><b>Acidentes:</b>"
          f" {int(row['Acidentes'])}"
      ),
      color="#2b5c8f",
      fill=True,
      fill_color="#3186cc",
      fill_opacity=0.7,
  ).add_to(mapa)

# 5. Salvar num ficheiro HTML limpo
output_html = "Mapa_Escorpiao_Montes_Claros_Perfeito.html"
mapa.save(output_html)

print("==================================================")
print(f"MAPA PERFEITO GERADO SEM MARCA DE ÁGUA: {output_html}")
print("==================================================")