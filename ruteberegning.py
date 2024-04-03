import requests 
import pandas as pd
import geopandas as gpd
from shapely.geometry import shape
from shapely import ops 
from datetime import datetime

import STARTHER
import nvdbgeotricks

def ruteplan2feature( ruteplanapi:str,  stops:str  ): 
    """
    Anroper ruteplan-API og returnerer dictionary med geometri, lengde og kjøretid 
    """

    r = requests.get( ruteplanapi, params={'stops' : stops, 'ReturnFields' : 'Geometry' } )
    svar = None 
    if r.ok: 
        rute = r.json()
        if 'routes' in rute and isinstance( rute['routes'], list) and len( rute['routes'] ) >= 1:
            minRute = rute['routes'][0] 
            svar = {}
            if 'statistic' in minRute: 
                # svar['tollSmall']       = float( minRute['statistic'].pop( 'tollSmall', None ) )
                # svar['tollLarge']       = float( minRute['statistic'].pop( 'tollLarge', None ) )
                svar['meterFerry']      = int( minRute['statistic'].pop( 'meterFerry', 0 ) )
                ## Må lage logikk for å takle null-verdi ferryCount : ""
                # svar['ferryCount']      = int( minRute['statistic'].pop( 'ferryCount', 0 ) )
                # svar['tollCount']       = int( minRute['statistic'].pop( 'tollCount', 0 ) )
                svar['totalDriveTime']  = minRute['statistic'].pop( 'totalDriveTime', None )
                svar['totalLength']     = minRute['statistic'].pop( 'totalLength', None )

                # # FerryCount er 2X riktig svar, hack for å fikse det
                # if svar['ferryCount'] >= 2 and svar['ferryCount'] % 2 == 0: 
                #     svar['ferryCount'] = round( svar['ferryCount'] / 2 )

            svar['geometry'] = geojson2linestring( minRute )

    if not svar: 
        svar = r.json()
        print( f"Ruteforslag feiler for stops={stops} HTTP  {r.status_code} {r.text[0:200]}")

    return svar 

def geojson2linestring(  featureCollection:dict   ): 
    """
    Omsetter geometri fra geojson featureCollection til sammenhengende linje

    Vil returnere MultiLineString hvis linjene ikke er sammenhengende. Vil trolig 
    feile hvis geometritypen er noe annet enn LineString

    Returnerer shapely LineString-objekt (hvis alt går greit)
    """

    myGeomList = []
    for feat in featureCollection['features']: 
        # Hopper over 
        if 'maneuverType' in feat['properties'] and feat['properties']['maneuverType'] == 'EsriDmtStop': 
            pass 
        else: 
            myGeomList.append( shape( feat['geometry']  ) )

    geom = ops.linemerge( myGeomList )
    return geom 



# Kjøres INTERNT på vegvesen-nettverket mot vår TESTPRODUKSJON
ruteplanapi = 'https://www.test.vegvesen.no/ws/no/vegvesen/ruteplan/routingservice_v3_0/open/routingService/api/Route/best'

if __name__ == '__main__': 
    print( f"Kjører fattigmanns nettverkanalyse")
    tnull = datetime.now()
    store2covenant  = gpd.read_file( 'luftlinje.gpkg', layer='store2covenant')
    store2store     = gpd.read_file( 'luftlinje.gpkg', layer='store2store')
    # store2covenant['stops'] = store2covenant['geometry'].apply( lambda geom : ';'.join( [ ','.join( [ str( round( x, 2) ) for x in p ] ) for p in geom.coords ] ) )


    rute_store2covenant = []
    rute_store2store = []

    t0 = datetime.now()
    print( f"Tidsbruk innlasting av data: {t0-tnull}")
    print( f"======================\n\nHenter ruteforslag store2covenant\n")

    subsett_startid = ['kiwi::7080001190415', 'coop::2559' ]


    # for ii, row in store2covenant.iterrows(): 
    # for ii, row in store2covenant[0:100].iterrows(): 
    for ii, row in store2covenant[ store2covenant['startunikid'].isin( subsett_startid )].iterrows(): 

        # Konverterer row (pandas series) til vanlig dictionary
        rad = row.to_dict()

        # Konverterer geometriske koordinat til "stops" - tekststreng
        stops = ';'.join( [ ','.join( [ str( round( x, 2) ) for x in p ] ) for p in row['geometry'].coords ] )
        rute = ruteplan2feature( ruteplanapi, stops )
        rad.update( rute )
        rute_store2covenant.append( rad )

        if ii+1 in [1, 5, 10, 20, 50] or ii+1 % 100 == 0: 
            print( f"Hentet ruteforslag {ii+1} av {len(store2covenant)} tidsbruk={datetime.now()-t0} \t\t{round( 100*(ii+1)/len(store2covenant),1)}%")

    print( f"Ferdig med {len(rute_store2covenant)} ruteforslag, tidsbruk {datetime.now()-t0}")

    print( f"======================\n\nHenter ruteforslag store2store\n")
    t1 = datetime.now()
    # for ii, row in store2store.iterrows():
    # for ii, row in store2store[0:100].iterrows():
    for ii, row in store2store[ store2store['startid'].isin( subsett_startid )].iterrows(): 
        
        # Konverterer row (pandas series) til vanlig dictionary
        rad = row.to_dict()

        # Konverterer geometriske koordinat til "stops" - tekststreng
        stops = ';'.join( [ ','.join( [ str( round( x, 2) ) for x in p ] ) for p in row['geometry'].coords ] )
        rute = ruteplan2feature( ruteplanapi, stops )
        rad.update( rute )
        rute_store2store.append( rad )

        if ii+1 in [1, 5, 10, 20, 50] or ii+1 % 100 == 0: 
            print( f"Hentet ruteforslag {ii+1} av {len(store2store)} tidsbruk={datetime.now()-t1} \t\t{round( 100*(ii+1)/len(store2store),1)}%")

    print( f"Ferdig med {len(rute_store2store)} ruteforslag, tidsbruk {datetime.now()-t1}")

    # En spissfindighet med rad.update: 
    # Hvis ruteberegning FEILER så får vi feilmelding kode av typen 
    # {'code': 9201, 'message': 'Slutt posisjonen er for langt unna gyldig vegnett.'} 
    # Geometrien blir da lik den opprinnelige luftlinje-geometrien. Disse må filtreres ut fra analysen
    # Når vi får et gyldig ruteforslag så erstattes linftlinje-geometrien med ruteforslagets geometri, 
    # og samtidig får vi påført egenskaper om lengde, antall bomstasjoner etc.  


    print( f"\nFerdig med alle ruteforslag, tidsbruk: {datetime.now()-t0}")

    rute_store2store = pd.DataFrame( rute_store2store )
    rute_store2store = gpd.GeoDataFrame( rute_store2store, geometry='geometry', crs=25833 )

    rute_store2covenant = pd.DataFrame( rute_store2covenant )
    rute_store2covenant = gpd.GeoDataFrame( rute_store2covenant, geometry='geometry', crs=25833 )


    gpkgfil = 'ruteforslag.gpkg'
    rute_store2covenant.to_file( gpkgfil, layer='rute_store2covenant', driver='GPKG')
    rute_store2store.to_file( gpkgfil, layer='rute_store2store', driver='GPKG')

    cscvump_store2store = rute_store2store.drop( columns='geometry')
    cscvump_store2store.to_csv( 'rute_store2store.csv' )

    cscvump_store2covenant = rute_store2covenant.drop( columns='geometry')
    cscvump_store2covenant.to_csv( 'rute_store2covenant.csv' )
