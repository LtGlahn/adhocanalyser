"""
Ser på historisk G/S fra 2014 - dd 
"""

import pandas as pd
import geopandas as gpd
from shapely import wkt 

import STARTHER
import nvdbapiv3
import nvdbgeotricks 


if __name__ == '__main__': 

    # Laster ned historisk vegnett
    v = nvdbapiv3.nvdbVegnett()
    v.filter( {'trafikantgruppe' : 'G', 'historisk' : True })
    vegnett = pd.DataFrame( v.to_records())

    # Laster ned 532 Vegreferanse med vegstatus = G/S
    sok = nvdbapiv3.nvdbFagdata( 532)
    sok.filter( 'alle_versjoner' : True, 'egenskap' = '(4567=12983 OR 4567=12159)')
    vegref = pd.DataFrame( sok.to_records())
    


