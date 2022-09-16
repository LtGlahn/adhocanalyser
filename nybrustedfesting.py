import pandas as pd
import geopandas as gpd
from shapely import wkt 


import STARTHER
import nvdbapiv3
import nvdbgeotricks 


if __name__ == '__main__': 

    brusok = nvdbapiv3.nvdbFagdata( 60 )
    brusok.filter( {'kommune' : 5001 })
    bruGdf = pd.DataFrame( brusok.to_records())
    bruGdf['geometry'] = bruGdf['geometri'].apply( wkt.loads ) 
    bruGdf = gpd.GeoDataFrame( bruGdf, geometry='geometry', crs=5973 )
    bruGdf['row_id'] = bruGdf.index
    brucol = [  'row_id', 'nvdbId', 'versjon', 'Lengde',
                'Brukategori', 'Status',
                'Navn', 'Opprinnelig Brutus F-Nr', 'Brutusnummer',
                'vref',  'veglenkesekvensid',  'startposisjon', 'sluttposisjon', 'segmentlengde', 
                'trafikantgruppe', 'geometri', 'geometry'  ]


    # Gjør livet enkelt - tar kun med dem som har 1 og kun 1 oppføring (ett vegsegment)
    # bruGdf.drop_duplicates( subset='nvdbId', keep=False, inplace=True )

    # Veger
    vegsok = nvdbapiv3.nvdbVegnett()
    vegsok.filter( {'kommune' : 5001 })
    vegdf = pd.DataFrame( vegsok.to_records())
    bruveg = vegdf[ vegdf['medium'] == 'L' ].copy()
    bruveg['geometry'] = bruveg['geometri'].apply( wkt.loads )
    bruveg = gpd.GeoDataFrame( bruveg, geometry='geometry', crs=5973 )
    vegcol =  [ 'veglenkesekvensid', 'startposisjon', 'sluttposisjon', 'type', 'medium', 
                'detaljnivå', 'geometri', 'trafikantgruppe', 'vref', 'geometry' ]

    joined = nvdbgeotricks.finnoverlapp( bruGdf[brucol], bruveg[vegcol], prefixA='bru_', prefixB='veg_')

    