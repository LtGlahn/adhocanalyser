"""
Dataprepp for fattigmanns nettverksanalyse 

Leser CSV-fil med start- og målpunkt og forberder 
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString

if __name__ == '__main__':

    store2store = pd.read_csv( 'store_store_combinations.csv' )
    store2store['geometry'] = store2store.apply( lambda row : LineString( [ [ row['startlon'], row['startlat'] ] , [ row['endlon'], row['endlat'] ] ] )  , axis=1 )
    store2store = gpd.GeoDataFrame( store2store, geometry='geometry', crs=4326 )
    store2store = store2store.to_crs( 25833 )
    store2store['Avstand luftlinje'] = store2store['geometry'].apply( lambda x : x.length )
    store2store.to_file( 'luftlinje.gpkg', layer='store2store', driver='GPKG' )

    store2covenant = pd.read_csv( 'store_covenant_combinations.csv' )
    store2covenant['geometry'] = store2covenant.apply( lambda row : LineString( [ [ row['startlon'], row['startlat'] ] , [ row['endlon'], row['endlat'] ] ] )  , axis=1 )
    store2covenant = gpd.GeoDataFrame( store2covenant, geometry='geometry', crs=4326 )
    store2covenant = store2covenant.to_crs( 25833 )
    store2covenant['Avstand luftlinje'] = store2covenant['geometry'].apply( lambda x : x.length )
    store2covenant.to_file( 'luftlinje.gpkg', layer='store2covenant', driver='GPKG' )
