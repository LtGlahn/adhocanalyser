from datetime import datetime

import pandas as pd
import geopandas as gpd
from shapely import wkt 

import STARTHER
import nvdbapiv3 
import nvdbgeotricks 
import spesialrapporter

if __name__ == '__main__': 

    t0 = datetime.now()
    forb = nvdbapiv3.apiforbindelse()
    forb.login( miljo='prodles')

    minGDfliste = []
    filnavn = 'bruksklasse_multippelStedfesting'

    objektTyper = [900, 901, 902, 903, 904, 905 ] 
    for objekttype in objektTyper: 
        print( "Henter objekttype=", objekttype, "Tidsbruk:", datetime.now()-t0)

        sok = nvdbapiv3.nvdbFagdata( objekttype )
        sok.filter( { 'vegsystemreferanse' : 'Pv', 'kommune' : 301 })
        sok.forbindelse = forb 
        data = pd.DataFrame( spesialrapporter.finnnVegnummerForSok( sok ) )
        data['geometry'] = data['geometri'].apply( wkt.loads )
        data.drop( columns='geometri', inplace=True )
        minGDF = gpd.GeoDataFrame( data, geometry='geometry', crs=5973 )
        minGDF.to_file( filnavn+'.gpkg', layer=str(objekttype)+' multippel', driver='GPKG' )
        minGDfliste.append( minGDF )

    print( "Tidsbruk datahenting:", datetime.now()-t0 )

    navneliste = [ str(x)+' Multippel stedfesting' for x in objektTyper ]
    nvdbgeotricks.skrivexcel( filnavn+'.xlsx',  minGDfliste, sheet_nameListe=navneliste )

    tidsbruk_totalt = datetime.now()-t0 
