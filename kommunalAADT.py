"""
Setter sammen siste gyldige data, dvs kombinerer dagens data 
med det som ble satt historisk 3.12.2021 (med "År, gjelder for" < 2020 )
"""


import pandas as pd
import geopandas as gpd
from shapely import wkt 

import STARTHER
import nvdbapiv3
import nvdbgeotricks 



def nyVegreferanse( row, vrefcol='vegsystemreferanse', hentAlle=False ): 
    """
    Henter ny vegsystemreferanse hvis den mangler 
    """

    if len( row[vrefcol] ) > 3 and not hentAlle: 
        return row[vrefcol] 
    else: 
        start = f"{row['startposisjon']:.8f}@{row['veglenkesekvensid']}"
        slutt = f"{row['sluttposisjon']:.8f}@{row['veglenkesekvensid']}"
        rute = nvdbapiv3.hentrute( start, slutt )
        if len( rute ) == 1: 
            return row['vref']
        else: 
            xx = [ x['vref'] for x in rute if 'vref' in x]
            print( f"Fant {len(rute)} vegsegmenter på søk etter vegreferanse: {','.join(xx)} " )
            yy = nvdbgeotricks.joinvegsystemreferanser( xx )
            return ','.join( yy )
            
    return ''

if __name__ == '__main__': 

    sok = nvdbapiv3.nvdbFagdata( 540)
    sok.filter( { 'vegsystemreferanse' : 'Kv,Pv,Rv', 'tidspunkt' : '2021-12-02'})
    gamleAadt = pd.DataFrame( sok.to_records())
    gamleAadt['geometry'] = gamleAadt['geometri'].apply( wkt.loads )
    gamleAadt = gpd.GeoDataFrame( gamleAadt, geometry='geometry', crs=5973 ) 

    # Filtrerer vekk 2020 og 2021-tall fra de gamle dataene 
    gamleAadt = gamleAadt[ gamleAadt['År, gjelder for'] < 2020 ]
    gamleAadt.reset_index( inplace=True )
    gamleAadt['_tmpIndex'] = gamleAadt.index
    gamleAadt['geometrilengde'] = gamleAadt['geometry'].length

    gamleAadt.drop( columns='relasjoner', inplace=True )

    nyttSok = nvdbapiv3.nvdbFagdata(540)
    nyttSok.filter( {'vegsystemreferanse' : 'Kv,Pv,Sv'})
    nyeAADT = pd.DataFrame( nyttSok.to_records())
    nyeAADT['geometry'] = nyeAADT['geometri'].apply( wkt.loads )
    nyeAADT.drop( columns='relasjoner', inplace=True )
    nyeAADT = gpd.GeoDataFrame( nyeAADT, geometry='geometry', crs=5973 )


    # Lager en join
    joined = nvdbgeotricks.finnoverlapp( nyeAADT, gamleAadt, klippgeometri=True, prefixB='gml_' )
    joined['ny_geometrilengde'] = joined['geometry'].length
    joined['andel'] = joined['ny_geometrilengde'] / joined['gml_geometrilengde']

    # Reparererer vegreferanser
    joined['nye_vref'] = joined.apply( nyVegreferanse, axis=1 )