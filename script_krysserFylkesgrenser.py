"""
Løper gjennom alle objekt og finner dem som krysser fylkesgrensa
"""
import pandas as pd
import geopandas as gpd
from shapely import wkt

import STARTHER
import nvdbapiv3 
import nvdbgeotricks

if __name__ == '__main__': 

    objektTyper = [ 904 ]
    resultat = { }
    gpkgfil = 'analyseKrysserfylkesgrensa.gpkg'
    forb = nvdbapiv3.apiforbindelse()
    forb.velgmiljo( 'stm-utvles')

    for objType in objektTyper: 
        data = []

        sok = nvdbapiv3.nvdbFagdata( objType )
        sok.forbindelse = forb
        count = 0 
        for obj in sok: 
            if len(  obj['lokasjon']['fylker'] ) > 1: 
                data.extend( nvdbapiv3.nvdbfagdata2records( obj )  )
            count += 1 
            if count % 10000 == 0: 
                print( f"Hentet objekt {count} av {sok.antall}  ( {round( 100* count / sok.antall ) }% )")


        if len( data ) > 0: 
            data = pd.DataFrame( data )
            data = gpd.GeoDataFrame( data, geometry=data['geometri'].apply( wkt.loads ), crs=5973 )
            data.drop( columns='geometri', inplace=True )
            resultat[objType] = data 
            data.to_file( gpkgfil, layer='krysserFylkesgrense_' + str( objType), driver='GPKG' )

        else: 
            print( f"Ingen objekter av typen {objType} krysser fylkesgrensene i miljø {forb.apiurl} ")

