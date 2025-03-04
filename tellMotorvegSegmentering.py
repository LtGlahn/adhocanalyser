"""
Teller lengde på motorveg og motortrafikkveg - og "vanlig veg"

Bruker KOSTRA regler og segmentering av vegnett + vegobjekt 595 Motorveg
"""
import pandas as pd
import geopandas as gpd
from shapely import wkt 

import STARTHER
import nvdbapiv3 
import nvdbgeotricks 
import segmentering

if __name__ == '__main__': 

    vegnettfilter = { 'trafikantgruppe' : 'K', 
                     'vegsystemreferanse' : 'Ev,Rv,Fv,Kv', 
                     'adskiltelop' : 'med,nei',
                     'veglenketype' : 'hoved',
                     'sideanlegg' : False }
    
    vegdf = pd.DataFrame( nvdbapiv3.nvdbVegnett( filter=vegnettfilter ).to_records())
    veg = gpd.GeoDataFrame( vegdf, geometry=vegdf['geometri'].apply( wkt.loads), crs=5973  )

    # Trenger kun et subsett av kolonnene
    # 'href', 'veglenkesekvensid', 'startposisjon', 'sluttposisjon',
    #    'kortform', 'veglenkenummer', 'segmentnummer', 'startnode', 'sluttnode',
    #    'referanse', 'type', 'detaljnivå', 'typeVeg', 'typeVeg_sosi',
    #    'målemetode', 'feltoversikt', 'geometri', 'lengde', 'fylke', 'kommune',
    #    'vegsystemreferanse', 'gate', 'startdato', 'medium', 'vref',
    #    'vegkategori', 'fase', 'nummer', 'strekning', 'delstrekning',
    #    'fra_meter', 'til_meter', 'trafikantgruppe', 'adskilte_lop', 'måledato',
    #    'ankerpunktmeter', 'kryssdel', 'geometry'

    col = ['veglenkesekvensid', 'startposisjon', 'sluttposisjon',
       'kortform', 
         'detaljnivå', 'typeVeg', 
        'feltoversikt', 'lengde', 'fylke', 'kommune',
       'medium', 'vref',
       'vegkategori', 'trafikantgruppe', 'adskilte_lop', 'geometry' ]