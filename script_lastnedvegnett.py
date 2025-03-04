import pandas as pd
import geopandas as gpd 
from shapely import wkt

import STARTHER
import nvdbapiv3
import nvdbgeotricks

if __name__ == '__main__': 

    mittfilter = { 'kommune'  : 5001  } # Trondheim kommune 
    sok = nvdbapiv3.nvdbVegnett( filter=mittfilter  ) # ALLLE veglenker innafor Trondheim kommune - også de uten trafikantgruppe 
    mydf = pd.DataFrame( sok.to_records())

    # Konverterer fra dataframe => Geodataframe  
    mydf['geometry']  = mydf['geometri'].apply( wkt.loads )
    myGdf = gpd.GeoDataFrame( mydf, geometry='geometry', crs=5973 )

    # Lagrer resultatet 
    # myGdf.to_file( 'trondheimNettverk.gpkg', layer='alleLenker', driver='GPKG')   # QGIS friendly
    myGdf.to_file( 'trondheimNettverk.gdb', layer='alleLenker', driver='FileGDB')   # Esri friendly 

