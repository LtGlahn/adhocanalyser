import pandas as pd
import geopandas as gpd 
from shapely import wkt

# import STARTHER
import nvdbapiv3
import overlapp
import nvdbgeotricks



if __name__ == '__main__': 

    
    filter1 = {'vegsystemreferanse' : 'Rv41 S12D1', 'fylke' : 38 }
    bkmodul  = nvdbgeotricks.nvdbsok2GDF( nvdbapiv3.nvdbFagdata( 889, filter=filter1 ))
    bktømmer = nvdbgeotricks.nvdbsok2GDF( nvdbapiv3.nvdbFagdata( 900, filter=filter1 ))
    rekkverk = nvdbgeotricks.nvdbsok2GDF( nvdbapiv3.nvdbFagdata( 5, filter=filter1   ))

    # inner_joined1 = overlapp.finnoverlapp( bktømmer, bkmodul, klippgeometri=True, klippvegsystemreferanse=True )
    # inner_joined2 = overlapp.finnoverlapp( bkmodul, rekkverk, klippgeometri=True, klippvegsystemreferanse=True )
    
    left_joined1 = overlapp.finnoverlapp( bktømmer, bkmodul, klippgeometri=True, klippvegsystemreferanse=True, join='left', debug=True  )
    left_joined2 = overlapp.finnoverlapp( bkmodul, rekkverk, klippgeometri=True, klippvegsystemreferanse=True, join='left', debug=True )
    


    left_joined1.to_file( 'testleftjoin.gpkg', layer='eksempel1', driver='GPKG' )
    left_joined2.to_file( 'testleftjoin.gpkg', layer='eksempel2', driver='GPKG' )
    # aa = overlapp.antioverlapp( [(0.3, 0.4), (0, 0.1), (0.25, 0.45)], [(0.31, 0.33), (0.31, 0.32), (0.32, 0.34), (0.4, 1) ] )
    # bb = overlapp.antioverlapp( [(0, 1)], [(0.31, 0.33), (0.4, 1) ] )

