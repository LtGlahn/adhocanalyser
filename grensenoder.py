from csv import excel
import requests 

import pandas as pd
import geopandas as gpd

import STARTHER
import nvdbgeotricks 

if __name__ == '__main__': 

    shpfil = '/mnt/c/data/kartverket/Basisdata_0000_Norge_25833_KonnekteringspunkterNorgeSverige_Shape/KP_Norge_Sverige_2021_33.shp'
    grense = gpd.read_file( shpfil )
    grense = grense[ grense['OBJEKTTYP'] == 'Väg' ]

    nyedata = []
    for junk, eigrense in grense.iterrows(): 

        url = 'https://nvdbapiles-v3.atlas.vegvesen.no/posisjon'
        r = requests.get( url, params={ 'ost' : eigrense['geometry'].x, 'nord' : eigrense['geometry'].y } )
        if r.ok: 
            data = r.json()[0]
            vlenk = data.pop( 'veglenkesekvens', None )
            vref = data.pop( 'vegsystemreferanse', None )
            geom = data.pop( 'geometri', None )
            data['Vegreferanse'] = vref['kortform']
            data['Vegkategori'] = vref['vegsystem']['vegkategori']
            data['Vegnummer'] = vref['vegsystem']['nummer']
            data['stedfesting'] = vlenk['kortform']
            data['geometry'] = eigrense['geometry']
            data['vegnettsgeometri'] = geom['wkt']

            data['Vegkart lenke'] = f"https://vegkart.atlas.vegvesen.no/#kartlag:geodata/@{round( eigrense['geometry'].x )},{ eigrense['geometry'].y },15"

            nyedata.append( data )

        else: 
            print( f"Fant ikke veg for posisjon {eigrense['geometry'].wkt} ")
            print( r.status_code, r.text )

    mineNyeData = pd.DataFrame( nyedata )
    mineNyeData.rename( columns={'avstand' : 'Avstand til nærmeste norske veg'},  inplace=True )
    mineNyeData = gpd.GeoDataFrame( mineNyeData, geometry='geometry', crs=25833 )
    mineNyeData.to_file( 'grenseveger_sverige.gpkg', layer='grenseveger', driver='GPKG')
    
    excelcol = [ 'Vegreferanse', 'Vegkategori', 'Vegnummer',  'Avstand til nærmeste norske veg', 'Vegkart lenke'  ]


    nvdbgeotricks.skrivexcel( 'Grenseveger sverige.xlsx', mineNyeData[excelcol] )