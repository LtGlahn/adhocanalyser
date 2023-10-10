"""
Finner avvik mellom bruksklassene for normal- og tømmetransport. 

Egenskapene "Bruksklasse" og "Bruksklasse, vinter" skal jo være identiske for disse to 
objekttypene, men vi har en del datafeil 

Objekttype ID: 
901 = Bruksklasse tømmertransport, uoffisiell 
905 = Bruksklasse normaltransport, uoffisiell 
"""
from datetime import datetime

import pandas as pd
import geopandas as gpd 
from shapely import wkt 


import STARTHER
import nvdbapiv3 
import overlapp
import nvdbgeotricks


if __name__ == '__main__': 

    pd.options.display.float_format = '{:.2f}'.format

    bk901 = nvdbapiv3.nvdbFagdata(901 )
    bk905 = nvdbapiv3.nvdbFagdata(905 )

    forb = nvdbapiv3.apiforbindelse()
    forb.login( miljo='prodles')
    bk901.forbindelse = forb
    bk905.forbindelse = forb


    # Testdatasett med et par av de feila vi fant på https://www.vegvesen.no/jira/browse/NVDB-12683
    mittFilter = { 'vegsystemreferanse' : '3035 KV10210,3805 KV43348,5025 KV6060,3420 KV2240,3448 KV3378', 'tidspunkt' : '2023-06-03'}
    # bk901.filter( mittFilter )
    # bk905.filter( mittFilter )

    t0 = datetime.now()
    df901 = pd.DataFrame( bk901.to_records())
    df905 = pd.DataFrame( bk905.to_records())
    t1 = datetime.now()
    print( f"Datanedlasting tidsbruk: {t1-t0}")
    df901['geometry'] = df901['geometri'].apply( wkt.loads )
    df905['geometry'] = df905['geometri'].apply( wkt.loads )
    df901 = gpd.GeoDataFrame( df901, geometry='geometry', crs=5973 )
    df905 = gpd.GeoDataFrame( df905, geometry='geometry', crs=5973 )

    if not 'Bruksklasse vinter' in df905.columns:
        df905['Bruksklasse vinter'] = ''

    if not 'Bruksklasse vinter' in df901.columns:
        df901['Bruksklasse vinter'] = ''

    t2 = datetime.now()
    bkOverlapp = overlapp.finnoverlapp( df905, df901)
    print( f"Overlapp tidsbruk: {datetime.now()-t2}")
    bkOverlapp.fillna( '', inplace=True )

    avvik = bkOverlapp[ (bkOverlapp['Bruksklasse']          != bkOverlapp['t901_Bruksklasse']) | 
                        (bkOverlapp['Bruksklasse vinter']   != bkOverlapp['t901_Bruksklasse vinter']) ]

    # Filtrerer ut fra regneark med gyldige og ugyldige kombinasjoner 
    # (en tidligere versjon av 'kombinasjonerBKnormal_tommer.xlsx' som Tone har kommentert på)
    gyldigRegneark = pd.read_excel( '/mnt/c/Users/jajens/OneDrive - Statens vegvesen/arbeidsfiler/NVDBkombinasjonerBKnormal_tommer.xlsx')
    gyldigRegneark.fillna( '', inplace=True )
    gyldig_col = ['Bruksklasse', 't901_Bruksklasse', 'Bruksklasse vinter', 't901_Bruksklasse vinter' ]
    gyldig = gyldigRegneark[ gyldigRegneark['kommentarer'] == 'Gyldig']
    
    for junk, row in gyldig.iterrows(): 
        tmp = avvik[ ((avvik['Bruksklasse'] == row['Bruksklasse'] ) & 
                      (avvik['Bruksklasse vinter'] == row['Bruksklasse vinter'] ) &  
                      (avvik['t901_Bruksklasse'] == row['t901_Bruksklasse'] ) &  
                      (avvik['t901_Bruksklasse vinter'] == row['t901_Bruksklasse vinter'] ) ) ]
        
        if len( tmp ) > 0:
            print( f"Dropper {len(tmp)} objekt med gldig BK kombinasjon: {row['Bruksklasse']} - {row['t901_Bruksklasse']}  - BK vinter: {row['Bruksklasse vinter']} {row['t901_Bruksklasse vinter']} ")

            avvik = avvik[ ~((avvik['Bruksklasse'] == row['Bruksklasse'] ) & 
                      (avvik['Bruksklasse vinter'] == row['Bruksklasse vinter'] ) &  
                      (avvik['t901_Bruksklasse'] == row['t901_Bruksklasse'] ) &  
                      (avvik['t901_Bruksklasse vinter'] == row['t901_Bruksklasse vinter'] ) ) ]

    avvik = avvik.copy()

    # Finner alle mulige datakombinasjoner: 
    kombo = avvik.groupby( ['Bruksklasse', 't901_Bruksklasse', 
                    'Bruksklasse vinter', 't901_Bruksklasse vinter']).agg( {'t901_nvdbId' : 'nunique', 
                                                                            'segmentlengde' : 'sum' } ).reset_index()
    kombo.sort_values( by='segmentlengde', ascending=False, inplace=True )

    kombo = pd.merge( kombo, gyldigRegneark[ gyldig_col + ['kommentarer']], on=gyldig_col, how='left')
    nvdbgeotricks.skrivexcel( 'kombinasjonerBKnormal_tommer.xlsx', kombo )

    avvik = pd.merge( avvik, gyldigRegneark[ gyldig_col + ['kommentarer']], on=gyldig_col, how='left')

    col = [ 'kommune', 'fylke', 'vref', 'vegkategori', 'fase', 'vegnummer', 'Bruksklasse', 't901_Bruksklasse', 
            'Bruksklasse vinter', 't901_Bruksklasse vinter', 't901_Utgår_Maks totalvekt', 'Maks vogntoglengde', 't901_Maks vogntoglengde', 
            't901_Tillatt for modulvogntog 1 og 2 med sporingskrav', 'Strekningsbeskrivelse', 't901_Strekningsbeskrivelse', 'kommentarer',
            'typeVeg', 
            'veglenkeType', 'segmentlengde', 'adskilte_lop', 'trafikantgruppe', 'nvdbId', 'versjon', 't901_nvdbId', 't901_versjon', 
            'veglenkesekvensid', 'startposisjon', 'sluttposisjon', 'geometry' ]

    avvik.sort_values( by=['fase', 'vegkategori', 'fylke', 'Bruksklasse', 'vref' ], inplace=True )

    nvdbgeotricks.skrivexcel( 'helenorge_avvikBKnormal_VS_BKtommer.xlsx', avvik[col] )
    avvik[col].to_file( 'helenorge_avvikBKnormal_VS_BKtommer.gpkg', layer='avvikBKnormal_tommer', driver='GPKG'  )
