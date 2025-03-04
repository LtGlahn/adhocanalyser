import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go

# API-forespørsel og databehandling
url = "https://nvdbapiles-v3.atlas.vegvesen.no/vegnett/veglenkesekvenser/segmentert"
params = {
    "vegsystemreferanse": "Fv585",
    "detaljniva": "VTKB,VT",
    "trafikantgruppe": "K",
    "adskiltelop": "MED,NEI",
    "srid": "4326"
}

response = requests.get(url, params=params)
data = response.json()

all_coords = []
segment_breaks = [0]
total_length = 0

for feature in data['objekter']:
    geometry = feature['geometri']['wkt']
    coord_pairs = geometry.split('(')[1].split(')')[0].split(',')
    coords = [list(map(float, pair.split())) for pair in coord_pairs]
    all_coords.extend(coords)
    segment_breaks.append(len(all_coords))
    total_length += feature['lengde']

df = pd.DataFrame(all_coords, columns=['Lon', 'Lat', 'Z'])
df.to_csv('veidata.csv', index=False)

# Beregn global min og max høyde
min_height = df['Z'].min()
max_height = df['Z'].max()

# Plotting med Matplotlib (statisk 3D-plot)
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

for i in range(len(segment_breaks) - 1):
    start = segment_breaks[i]
    end = segment_breaks[i+1]
    segment = df.iloc[start:end]
    sc = ax.scatter(segment['Lon'], segment['Z'], segment['Lat'], c=segment['Z'], cmap='viridis', vmin=min_height, vmax=max_height)
    ax.plot(segment['Lon'], segment['Z'], segment['Lat'], c='blue', alpha=0.5)

ax.set_xlabel('Lengdegrad')
ax.set_ylabel('Høyde (m)')
ax.set_zlabel('Breddegrad')
ax.set_title('3D-plot av veistrekning')
plt.colorbar(sc, label='Høyde (m)')
plt.savefig('veistrekning_3d.png')
plt.close()

# Interaktiv plotting med Plotly
fig = go.Figure()

for i in range(len(segment_breaks) - 1):
    start = segment_breaks[i]
    end = segment_breaks[i+1]
    segment = df.iloc[start:end]
    
    fig.add_trace(go.Scatter3d(
        x=segment['Lon'],
        y=segment['Z'],
        z=segment['Lat'],
        mode='lines+markers',
        line=dict(color='blue', width=2),
        marker=dict(
            size=4,
            color=segment['Z'],
            colorscale='Viridis',
            colorbar=dict(title='Høyde (m)'),
            cmin=min_height,
            cmax=max_height
        ),
        showlegend=False
    ))

fig.update_layout(
    title='Interaktiv 3D-plot av veistrekning',
    scene=dict(
        xaxis_title='Lengdegrad',
        yaxis_title='Høyde (m)',
        zaxis_title='Breddegrad'
    ),
    coloraxis_colorbar=dict(title='Høyde (m)')
)

fig.write_html("interaktiv_veistrekning.html")

print(f"Script fullført. Total veilengde: {total_length:.2f} meter")
print(f"Høyderange: {min_height:.2f}m - {max_height:.2f}m")
print("Sjekk 'veidata.csv', 'veistrekning_3d.png', og 'interaktiv_veistrekning.html' i arbeidsmappen.")