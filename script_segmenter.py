""" 
Segmenter hele nettverket til NVDB for Trondheim kommune med fartgsgrense 
"""

import pandas as pd
import geopandas as gpd 
from shapely import wkt

import STARTHER
import nvdbapiv3
import segmentering

if __name__ == '__main__': 

    mittfilter = { 'kommune'  : 5001, 'veglenketype': 'hoved,konnektering'  } # Trondheim kommune 
    sok = nvdbapiv3.nvdbVegnett( filter=mittfilter  ) # ALLLE veglenker innafor Trondheim kommune - også de uten trafikantgruppe 
    mydf = pd.DataFrame( sok.to_records())

    # Konverterer fra dataframe => Geodataframe  
    mydf['geometry']  = mydf['geometri'].apply( wkt.loads )
    heleNettverk = gpd.GeoDataFrame( mydf, geometry='geometry', crs=5973 )


    # Laster ned fartsgrense 
    mydf = pd.DataFrame( nvdbapiv3.nvdbFagdata(105, filter={'kommune' : 5001}).to_records() )
    fart = gpd.GeoDataFrame( mydf, geometry=mydf['geometri'].apply(wkt.loads ))

    # Må dele opp, segmenteringsrutinen forutsetter gyldig metrering 
    bilveg = heleNettverk[ heleNettverk['trafikantgruppe'] == 'K' ]
    fotveg = heleNettverk[ heleNettverk['trafikantgruppe'] != 'K' ]

    medFartsgrense = segmentering.segmenter( bilveg, fart)

    # Slår sammen segmentert fartsgrense med "fotveg" - datasettet 
    heleNettverket_medFart = pd.concat( [ medFartsgrense, fotveg ], ignore_index=True )

    # Lagrer resultatet 
    # heleNettverk.to_file( 'trondheimNettverk.gpkg', layer='alleLenker', driver='GPKG')   # QGIS friendly
    heleNettverket_medFart.to_file( 'segmentert.gdb', layer='allelenker_medfart', driver='OpenFileGDB', TARGET_ARCGIS_VERSION='ARCGIS_PRO_3_2_OR_LATER')   # Esri friendly 
