"""
Itererer over alle objekter i NVDB og leter etter dem som mangler stedfesting 
"""
from datetime import datetime 

import pandas as pd
import geopandas as gpd 
from shapely import wkt

import STARTHER 
import nvdbapiv3 

if __name__ == '__main__': 


    langsG = None
    tverrG = None 
    forsterket = None

    objektTypeR = [99, 519, 836 ]
    for objektType in objektTypeR: 
        t0 = datetime.now( )

        sok = nvdbapiv3.nvdbFagdata( objektType )

        data = []
        count = 0
        for etObj in sok:
            count += 1
            feltsted = set()
            for stedf in etObj['lokasjon']['stedfestinger']: 
                if 'kjørefelt' in stedf and isinstance( stedf['kjørefelt'], list) and len( stedf['kjørefelt']) > 0: 
                    feltsted.update( stedf['kjørefelt'] ) 
            if len( feltsted ) > 0:
                feltsted = ','.join( list( feltsted ))
                etObj['egenskaper'].append( { 'id' : -1, 'navn' : 'felt', 'egenskapstype' : 'Tekst', 'datatype' : 'Tekst', 'verdi' : feltsted }  )

                data.append( etObj )

        if len( data ) > 0: 
            mydf = pd.DataFrame( nvdbapiv3.nvdbfagdata2records( data) )
            mydf['geometry'] = mydf['geometri'].apply( wkt.loads )
            myGdf = gpd.GeoDataFrame( mydf, geometry='geometry', crs=5973 )

            if objektType == 99: 
                myGdf.to_file( 'vegoppmerking_feltstedfesting.gpkg', layer='vegoppmerking 99 langsg med felt', driver='GPKG' )
                langsG = myGdf.copy()

            elif objektType == 519: 
                myGdf.to_file( 'vegoppmerking_feltstedfesting.gpkg', layer='vegoppmerking 519 tverrg med felt', driver='GPKG' )
                tverrG = myGdf.copy()

            elif objektType == 836: 
                myGdf.to_file( 'vegoppmerking_feltstedfesting.gpkg', layer='vegoppmerking 836 forsterket med felt', driver='GPKG' )
                forsterket = myGdf.copy()

            else: 
                print( f"Vet ikke hvor jeg skal lagre objekttype {objektType}")

        else: 
            print( "Ingen objekter tilfredsstiller kriteriene")
        print( f"Sjekket {count} objekter, {len(data)} tilfredsstiller kriteriene")

        print( f"Tidsbruk objekttype {objektType} {datetime.now()-t0}")

