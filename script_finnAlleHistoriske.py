"""
Finner alle historiske vegobjekter på angitt veglenkesekvens og dato 

Kan lett modifiseres til andre søkefiltre
"""
import json
import requests
from requests.auth import HTTPBasicAuth
import getpass 

import pandas as pd
import geopandas as gpd 
from shapely import wkt


import STARTHER
import nvdbapiv3 
import nvdbgeotricks 
import bomst2datafangst

# 89559367           EV6 S157D1 m9116-9180              877063
# 114685970          EV6 S157D1 m9344-9442              877064
# 114686002          EV6 S157D1 m13569-13637         878672
# 89559139             EV6 S158D1 m3756-3841              878747
# 89559134             EV6 S158D1 m4013-4079              878748
# 89559119             EV6 S158D1 m4579-4676              878750
# 89559070             EV6 S158D1 m6909-6977              878760



if __name__ == '__main__': 
    vlenk = [ 877063, 877064, 878672, 878747, 878748, 878750, 878760 ]
    vlenkfilter = ','.join( [ '0-1@'+str(x) for x in vlenk ]  )
    tidspunkt = '2021-06-14'

    dakaturl = 'https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekttyper.json'
    dakat = requests.get( dakaturl ).json()

    forbudsliste = [521, 524, 525, 525, 526, 562, 644, 645, 793, 871, 532, 539,
                    890, 891, 892, 893, 894, 895, 900, 901, 902, 903, 904, 905, 
                    810, 821, 912, 605, 616, 646, 580, 643,
                     105, 915, 916, 917, 918, 919, 920, 50001, 50002 ]

    alledata = []
    data = []
    objTyper = []
    mittfilter= { 'tidspunkt' : tidspunkt, 'veglenkesekvens' : vlenkfilter  }
    for objType in dakat: 
        if objType['id'] not in forbudsliste: 
            temp =  nvdbapiv3.nvdbFagdata( objType['id'], filter=mittfilter ).to_records( geometri=True, vegsegmenter=False )
            if len( temp ) > 0: 
                alledata.extend( temp )
                data.append( pd.DataFrame( temp ))
                objTyper.append(  str(objType['id']) + ' ' + objType['navn']  )
                print( f"Fant {len(temp)} forekomster av objekttype {objType['id']}  {objType['navn']}")

        else: 
            print( f"\t\tHopper over {objType['id']} {objType['navn']}")


    navneliste = [ nvdbapiv3.esriSikkerTekst( x) for x in objTyper ]
    # nvdbgeotricks.skrivexcel( 'historiskeTrafikklommeData.xlsx', data, sheet_nameListe=navneliste, slettgeometri=False )

    minGeojson = {'type': 'FeatureCollection',
                    'features': [] }
    for objType in data: 
        objType['geometry'] = objType['geometri'].apply( wkt.loads )
        myGdf = gpd.GeoDataFrame( objType, geometry='geometry', crs=5973 )
        myGdf = myGdf.to_crs( 4326 )
        temp = bomst2datafangst.gdf2geojson( myGdf )
        minGeojson['features'].extend( temp['features'] )


    # Sender til datafangst 
    kontrakt = 'bbc66a6e-73cd-411b-a15e-584c3155c9d0'
    # dfApi = 'https://datafangst.test.vegvesen.no/api/v1/contract/'
    dfApi = 'https://datafangst.vegvesen.no/api/v1/contract/'
    url = dfApi + kontrakt +  '/featurecollection'
    username = 'jajens'

    headers = headers = { 'Content-Type' : 'application/geo+json', 'Accept' : 'application/json' }
    pw = getpass.getpass( username+"'s PROD Password: ")
