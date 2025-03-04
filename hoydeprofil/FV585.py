import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
from copy import deepcopy

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point,LineString
from shapely import wkt, get_coordinates

# Mitt tricks for å føye nvdbapiv3 til søkestien
# https://github.com/ltglahn/nvdbapi-V3/
import STARTHER 
import nvdbapiv3 

# API-forespørsel og databehandling
# url = "https://nvdbapiles-v3.atlas.vegvesen.no/vegnett/veglenkesekvenser/segmentert"
params = {
    "vegsystemreferanse": "Fv585",
    "trafikantgruppe": "K",
    "adskiltelop": "med,nei",
    "veglenketype" : "hoved,konnektering", # Tilsvarer detaljniva="VT,VTKB"
    "kryssystem"   : False,
    "sideanlegg"   : False 
}

# response = requests.get(url, params=params)
# data = response.json()

mydf = pd.DataFrame( nvdbapiv3.nvdbVegnett( filter=params).to_records() ) 
myGdf = gpd.GeoDataFrame( mydf, geometry=mydf['geometri'].apply( wkt.loads ) )

# Ignorerer en del kolonner 
col = ['veglenkesekvensid', 'startposisjon', 'sluttposisjon',
       'kortform',  'geometri', 'detaljnivå', 'typeVeg', 
        'feltoversikt', 'lengde', 'fylke', 'kommune',
       'medium', 'vref', 'måledato',
       'vegkategori', 'trafikantgruppe', 'adskilte_lop', 'geometry' ]

myGdf = myGdf[col] 


# Legger Vegnummer, strekning og delstrekning i egen variabel 
myGdf['delstrekning'] = myGdf['vref'].apply( lambda x : ' '.join( x.split()[:-1] ) )


# Sorterer på vegsystemreferanse 
myGdf['meter'] = myGdf['vref'].apply( lambda x :  x.split('m')[-1].split('-')[0].zfill(5) )
myGdf = myGdf.sort_values( by=['delstrekning', 'meter'] )


## Skal iterere over alle segmentene og lager lengde - høyde profil langsetter vegen
# Tomme datastrukturer 
stigningListe = []
punktverdiListe = []
distanse = 0 
forrigePunkt = None 
nestePunkt = None 

for idx, row in myGdf.iterrows(): 
    coords = get_coordinates( row['geometry'], include_z = True ) 
    # TODO: Sjekk om dette segmentet har snudd metrering. I så fall må vi bytte rekkefølgen på koordinater
    # slik at de kommer i metreringsretning. Bør løses med videreutvikling av nvdbapiv3.nvdbVegnett(), som må 
    # legge på informasjon om meteringsretning 
    for j in range( 0, coords.shape[0]):
        if not forrigePunkt: # Første iterasjon => setter startpunkt 
            forrigePunkt = Point( coords[j,:] ) 
            forrige_Z = coords[j,2]
            punktverdiListe.append( { 'delstrekning' : row['delstrekning'], 
                            'X' : coords[j,0],
                            'Y' : coords[j,1],
                            'Z' : forrige_Z, 
                            'distanse' : 0, 
                            'måledato' : row['måledato'],
                            'geometry' : forrigePunkt } ) 

        else: 
            nestePunkt = Point( coords[j,:] ) 
            # Ignorerer høy punkttetthet og oppnår samtidig dobbeltpunkt der to segmenter møtes
            # (startpunkt på nytt segment = sluttpunkt på forrige segment) 
            # Sikrer også uendelig stigning (dele på lengde = 0) 
            if forrigePunkt.distance( nestePunkt ) > 0.5:
                ny_Z = coords[j,2]
                nyGeom = LineString( [ forrigePunkt, nestePunkt ] ) 
                distanse += nyGeom.length
                punktverdiListe.append( { 'delstrekning' : row['delstrekning'], 
                                'X' : coords[j,0],
                                'Y' : coords[j,1],                
                                'Z' : ny_Z, 'distanse' : distanse, 'geometry' : nestePunkt } )
                stigningListe.append( { 'delstrekning' : row['delstrekning'], 
                                        'stigning' : (ny_Z - forrige_Z) / nyGeom.length,
                                        'stigning_abs' : abs( (ny_Z - forrige_Z) / nyGeom.length), 
                                        'start_Z' : forrige_Z,
                                        'slutt_Z' : ny_Z, 
                                        'distanse' : distanse, 
                                        'lengde' : nyGeom.length, 
                                        'måledato' : row['måledato'], 
                                        'geometry' : nyGeom } )
                                        
                forrigePunkt = deepcopy( nestePunkt ) 
                forrige_Z = ny_Z
                                        
punkt = gpd.GeoDataFrame( punktverdiListe, geometry='geometry', crs=5973 )
punkt.to_file( 'hoydeprofil.gpkg', layer='punkt', driver='GPKG' )
stigning = gpd.GeoDataFrame( stigningListe, geometry='geometry', crs=5973 )
stigning.to_file( 'hoydeprofil.gpkg', layer='stigning', driver='GPKG' )



# all_coords = []
# segment_breaks = [0]
# total_length = 0

# for feature in data['objekter']:
    # geometry = feature['geometri']['wkt']
    # coord_pairs = geometry.split('(')[1].split(')')[0].split(',')
    # coords = [list(map(float, pair.split())) for pair in coord_pairs]
    # all_coords.extend(coords)
    # segment_breaks.append(len(all_coords))
    # total_length += feature['lengde']

# df = pd.DataFrame(all_coords, columns=['Lon', 'Lat', 'Z'])
df = punkt[['X', 'Y', 'Z']]
df.to_csv('veidata.csv', index=False)

# # Beregn global min og max høyde
min_height = df['Z'].min()
max_height = df['Z'].max()

# # Plotting med Matplotlib (statisk 3D-plot)
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# for i in range(len(segment_breaks) - 1):
    # start = segment_breaks[i]
    # end = segment_breaks[i+1]
    # segment = df.iloc[start:end]
    # sc = ax.scatter(segment['Lon'], segment['Z'], segment['Lat'], c=segment['Z'], cmap='viridis', vmin=min_height, vmax=max_height)
    # ax.plot(segment['Lon'], segment['Z'], segment['Lat'], c='blue', alpha=0.5)

sc = ax.scatter( df['X'], df['Y'], df['Z'], c=df['Z'], cmap='viridis', vmin=min_height, vmax=max_height)
ax.plot(df['X'], df['Y'], df['Z'], c='blue', alpha=0.5)
ax.set_xlabel('X (utm 33)')
ax.set_ylabel('Y (utm 33)')
ax.set_zlabel('Høyde (m)')
ax.set_title('3D-plot av veistrekning')
plt.colorbar(sc, label='Høyde (m)')
plt.savefig('veistrekning_3d.png')
plt.close()


# Statiske lengde - høyde plot 
fig2 = plt.figure(figsize=(12, 8))
ax2 = fig2.add_subplot(111 )
sc2 = ax2.scatter( punkt['distanse'], punkt['Z'], c=punkt['Z'], cmap='viridis', vmin=min_height, vmax=max_height)
ax2.plot(punkt['distanse'], punkt['Z'], c='blue', alpha=0.5)
ax2.set_xlabel( 'Distanse langs Fv585 (m)' )
ax2.set_ylabel( 'Høyde (m)' ) 
ax2.set_title('2D-plot høydeprofil langs Fv585')
plt.colorbar(sc2, label='Høyde (m)')
plt.savefig('veistrekning_2D.png')
plt.close()

# Plotter stigning vs lengde i 2D plott 
fig3 = plt.figure(figsize=(12, 8))
ax3 = fig3.add_subplot(111 )
sc3 = ax3.scatter( stigning['distanse'], stigning['stigning'], c=stigning['stigning'], cmap='viridis', vmin=min( stigning['stigning'] ), vmax=max( stigning['stigning']))
ax3.plot(stigning['distanse'], stigning['stigning'], c='blue', alpha=0.5)
ax3.set_xlabel( 'Stigning langs Fv585 (m)' )
ax3.set_ylabel( 'Stigning \fraq{dZ}{dX}' ) 
ax3.set_title('2D-plot av stigning Fv585')
plt.colorbar(sc3, label='Stigning \fraq{dZ}{dX}')
plt.savefig('veistrekning_2Dstigning.png')
plt.close()



# ax.set_xlabel('Lengdegrad')
# ax.set_ylabel('Høyde (m)')
# ax.set_zlabel('Breddegrad')
# ax.set_title('3D-plot av veistrekning')
# plt.colorbar(sc, label='Høyde (m)')
# plt.savefig('veistrekning_3d.png')
# plt.close()

# # Interaktiv plotting med Plotly
# fig = go.Figure()

# for i in range(len(segment_breaks) - 1):
    # start = segment_breaks[i]
    # end = segment_breaks[i+1]
    # segment = df.iloc[start:end]
    
    # fig.add_trace(go.Scatter3d(
        # x=segment['Lon'],
        # y=segment['Z'],
        # z=segment['Lat'],
        # mode='lines+markers',
        # line=dict(color='blue', width=2),
        # marker=dict(
            # size=4,
            # color=segment['Z'],
            # colorscale='Viridis',
            # colorbar=dict(title='Høyde (m)'),
            # cmin=min_height,
            # cmax=max_height
        # ),
        # showlegend=False
    # ))

# fig.update_layout(
    # title='Interaktiv 3D-plot av veistrekning',
    # scene=dict(
        # xaxis_title='Lengdegrad',
        # yaxis_title='Høyde (m)',
        # zaxis_title='Breddegrad'
    # ),
    # coloraxis_colorbar=dict(title='Høyde (m)')
# )

# fig.write_html("interaktiv_veistrekning.html")

# print(f"Script fullført. Total veilengde: {total_length:.2f} meter")
# print(f"Høyderange: {min_height:.2f}m - {max_height:.2f}m")
# print("Sjekk 'veidata.csv', 'veistrekning_3d.png', og 'interaktiv_veistrekning.html' i arbeidsmappen.")