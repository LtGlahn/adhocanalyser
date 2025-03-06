import pandas as pd
import geopandas as gpd 
from shapely import wkt

import STARTHER
import nvdbapiv3
import nvdbgeotricks

if __name__ == '__main__': 

    mittfilter = { 'kommune'  : 5001,                       # Trondheim kommune
                  'veglenketype' : 'hoved,konnektering'  }  # Kun øverste topologinivå (ignorerer nivåene kjørefelt og kjørebane) 
    sok = nvdbapiv3.nvdbVegnett( filter=mittfilter  ) # ALLLE veglenker innafor Trondheim kommune - også de uten trafikantgruppe 
    mydf = pd.DataFrame( sok.to_records())

    # Konverterer fra dataframe => Geodataframe  
    mydf['geometry']  = mydf['geometri'].apply( wkt.loads )
    myGdf = gpd.GeoDataFrame( mydf, geometry='geometry', crs=5973 )


    # Fjerner overflødige kolonner
    sletteCol = ['versjon', 'Gyldig fra dato', 'segmentlengde', 'segmentretning', 'stedfesting_retning', 'stedfesting_felt',
                'Vedtaksnummer', 'Arkivnummer', 'typeVeg_sosi', 'målemetode', 'geometri', 'lengde', 'vegsystemreferanse', 
                  'startdato', 'fase', 'nummer', 'strekning', 'delstrekning', 'fra_meter', 'til_meter',
                'ankerpunktmeter', 'kryssdel', 'sideanleggsdel' ]
    for SLETT in sletteCol: 
        if SLETT in myGdf.columns: 
            myGdf.drop( columns=SLETT, inplace=True )


    # Lagrer resultatet 
    # myGdf.to_file( 'trondheimNettverk.gpkg', layer='alleLenker', driver='GPKG')   # QGIS friendly
    myGdf.to_file( 'trondheimNettverk.gdb', layer='alleLenker', driver='OpenFileGDB', TARGET_ARCGIS_VERSION='ARCGIS_PRO_3_2_OR_LATER')   # Esri friendly 


