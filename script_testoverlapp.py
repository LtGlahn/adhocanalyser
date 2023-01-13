import pandas as pd 
import geopandas as gpd 
from shapely import wkt

import nvdbapiv3
import nvdbgeotricks


if __name__ == '__main__':

    mittfilter = { 'vegsystemreferanse' : 'RV41 K S12D1 m0-1327'}
    
    bk = pd.DataFrame( nvdbapiv3.nvdbFagdata( 900, filter=mittfilter ).to_records())
    bk['geometry'] = bk['geometri'].apply( wkt.loads ) 
    bk = gpd.GeoDataFrame( bk, geometry='geometry', crs=5973) 
    bk['orginal_segmentlengde'] = bk['segmentlengde']
 

    bkmodul = pd.DataFrame( nvdbapiv3.nvdbFagdata( 889, filter=mittfilter ).to_records())
    bkmodul['geometry'] = bkmodul['geometri'].apply( wkt.loads ) 
    bkmodul = gpd.GeoDataFrame( bkmodul, geometry='geometry', crs=5973) 
    bkmodul['orginal_segmentlengde'] = bkmodul['segmentlengde']

    joined_cut = nvdbgeotricks.finnoverlapp( bk, bkmodul, prefixB='bk889_', klippgeometri=True,  klippvegsystemreferanse=True   )
