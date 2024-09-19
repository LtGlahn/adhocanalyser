"""
Finner tunnelløp ut fra vegnett og matcher med NVDB tunnelløp. 
"""
#%% 
from copy import deepcopy 

import pandas as pd 
import geopandas as gpd
from shapely import from_wkt

import STARTHER
import nvdbapiv3 


if __name__ == '__main__': 

    mittfilter= { 'vegsystemreferanse' : 'Ev,Rv', 'kommune' : 5001 }
    myDf = pd.DataFrame( nvdbapiv3.nvdbVegnett( filter=mittfilter ).to_records())


#%% asdf

    myGdf = gpd.GeoDataFrame( myDf, geometry=myDf['geometri'].apply( from_wkt ), crs=5973)
    tunnel = myGdf[ myGdf['medium'] == 'U']
    utafor = myGdf[ myGdf['medium'] != 'U']


# %%
