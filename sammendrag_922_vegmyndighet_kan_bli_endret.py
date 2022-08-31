
import pandas as pd
import geopandas as gpd
from shapely import wkt
from shapely.geometry.point import Point
import xmltodict
from xml.parsers.expat import ExpatError
import json
import requests
import re
import numpy as np
import warnings
warnings.simplefilter('ignore', UserWarning )

import STARTHER
import nvdbapiv3
import nvdbgeotricks

if __name__ == '__main__': 
    sok = nvdbapiv3.nvdbFagdata( 922)
    mydf = pd.DataFrame( sok.to_records( ))
    mydf2 = mydf.copy()

    mydf2['_tmp_vegnr_rot']     = mydf2['vref'].apply( lambda x : x.split()[0] )
    mydf2['_tmp_vegnr_hale']    = mydf2['vref'].apply( lambda x : ' '.join( x.split()[1:] ) )
    mydf2['Vegsystemreferanse'] = mydf2['_tmp_vegnr_rot'] + ' ' + mydf2['trafikantgruppe'] + ' ' + mydf2['_tmp_vegnr_hale']
    mydf2['vegnr'] = mydf2['vref'].apply( lambda x : x.split()[0] )
    mydf2.fillna( '', inplace=True )
    col2 = [ 'Strekning', 'Saksnummer', 'Foreslått endring', 'Dato sendt til høring',
        'Prosjektreferanse', 'Tilleggsinformasjon', 'Dato vedtatt' ]
    sammendrag = mydf2.groupby( ['vegnr', 'kommune', 'trafikantgruppe'] + col2 ).agg( {  'segmentlengde' : 'sum' } ).reset_index()

    temp = nvdbgeotricks.joinvegsystemreferanser( mydf2['Vegsystemreferanse'].to_list() ) 
    mydf3 = pd.DataFrame( temp, columns=['Vegsystemreferanse'] )
    mydf3['trafikantgruppe'] = mydf3['Vegsystemreferanse'].apply( lambda x : x.split()[1] )

    nvdbgeotricks.skrivexcel( 'VegmyndighetKanBliEndret.xlsx', [mydf, sammendrag, mydf3], sheet_nameListe=['Vegmyndighet kan bli endret', 'Sammendrag',  'Forenklede vegsystemreferanser'] )
