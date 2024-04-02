"""
Sammenligner lengde for stedfesting langs vegnett med egengeometri linje 
"""

import pandas as pd
import geopandas as gpd
from shapely import wkt 

import STARTHER
import nvdbapiv3 
import nvdbgeotricks

def vegsegment2lengde( segmenter ):
    lengde = 0
    for seg in segmenter:
        lengde += seg['lengde']
    return lengde

if __name__ == '__main__': 
    mittfilter = { 'egenskap' : '(4714!=null)', 'kontraktsomrade' :  '3401 Nordre Hedmarken 2022-2028' }
    sok = nvdbapiv3.nvdbFagdata( 5, filter=mittfilter)
    data = pd.DataFrame( sok.to_records( vegsegmenter=False, geometri=True ))

    data['stedfestinglengde'] = data['vegsegmenter'].apply( vegsegment2lengde )
    data['geometry'] = data['geometri'].apply( wkt.loads )
    data['geometrilengde'] = data['geometry'].apply( lambda x : x.length )

    data['vegkart'] = data['nvdbId'].apply( lambda x : 'https://vegkart.atlas.vegvesen.no/#valgt:' + str( x ) + ':5' )
    col = [ 'objekttype', 'nvdbId', 'versjon', 'startdato',
            'Rekkverkstype', 'Etableringsår',
            'Bruksområde', 'Høyde, dimensjonerende',
            'Plassering på bru', 'relasjoner', 'vegsystemreferanser',
            'stedfesting_detaljer',
            'Tilleggsinformasjon', 'Produktnavn/typegodkjenning',
            'Prosjektreferanse', 'strekningslengde',
            'Lengde', 'stedfestinglengde', 'geometrilengde',  'vegkart' ]
    
    nvdbgeotricks.skrivexcel( 'rekkverkslengde.xlsx', data[col] )
    myGdf = gpd.GeoDataFrame( data, geometry='geometry', crs=5973 )
    myGdf[col+['geometry']].to_file( 'rekkverkslengde.gpkg')

    