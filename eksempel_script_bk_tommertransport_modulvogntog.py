"""
Laster med 900 bruksklasse modulvogntog med filteret Tillatt for modulvogntog med sporingskrav type 1 og 2 = Ja for et historisk tidspunkt
"""
import pandas as pd
import geopandas as gpd 
from shapely import wkt

import STARTHER
import nvdbapiv3
import nvdbgeotricks

if __name__ == '__main__': 

    mittfilter = { 'vegsystemreferanse' : 'Ev,Rv,Fv,Kv' } # 
    mittfilter['egenskap'] = '12057=20911'
    mittfilter['tidspunkt'] = '2022-12-15' 
    sok = nvdbapiv3.nvdbFagdata( 900, filter=mittfilter  ) # Bruksklasse modulvogntog 
    mydf = pd.DataFrame( sok.to_records())

    # Konverterer fra dataframe => Geodataframe  
    mydf['geometry']  = mydf['geometri'].apply( wkt.loads )
    myGdf = gpd.GeoDataFrame( mydf, geometry='geometry', crs=5973 )

    # Lagrer resultatet 
    myGdf.to_file( 'demo_bruksklassenedlasting.gpkg', layer='900 BK tømmertransport tillat 4 modulvt', driver='GPKG')
    nvdbgeotricks.skrivexcel( 'demo_bruksklassenedlasting.xlsx', mydf  )
