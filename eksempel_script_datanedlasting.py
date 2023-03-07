import pandas as pd
import geopandas as gpd 
from shapely import wkt

import STARTHER
import nvdbapiv3
import nvdbgeotricks

if __name__ == '__main__': 

    mittfilter = { 'kommune'  : 5001, 'vegsystemreferanse' : 'Ev,Rv,Fv,Kv' } # Trondheim kommune 
    sok = nvdbapiv3.nvdbFagdata( 899, filter=mittfilter  ) # Bruksklasse modulvogntog 
    mydf = pd.DataFrame( sok.to_records())

    # Konverterer fra dataframe => Geodataframe  
    mydf['geometry']  = mydf['geometri'].apply( wkt.loads )
    myGdf = gpd.GeoDataFrame( mydf, geometry='geometry', crs=5973 )

    # Lagrer resultatet 
    myGdf.to_file( 'demo_bruksklassenedlasting.gpkg', layer='889 bruksklasse modulvogntog', driver='GPKG')
    nvdbgeotricks.skrivexcel( 'demo_bruksklassenedlasting.xlsx', mydf  )
