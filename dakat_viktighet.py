"""
Sjekker alle objekttyper og tar vare på utvalgte geometriegenskaper (her: Kun høydereferanse)
"""
import requests
import pandas as pd
from copy import deepcopy 
from time import sleep

import STARTHER
import nvdbapiv3 

dakat = requests.get( 'https://nvdbapiles.atlas.vegvesen.no/vegobjekttyper').json()
# dakat = requests.get( 'https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekttyper').json()
data = []
for obj in dakat: 

    if obj['id'] < 20000 and obj['id'] != 793: 
    # if obj['id'] == 855: 

        print( f"{obj['id']} {obj['navn']}")

        mal = { 'objtype' : obj['id'] , 'Navn' : obj['navn']}   
        try: 
            objDakat = requests.get( 'https://nvdbapiles.atlas.vegvesen.no/vegobjekttyper/' + str( obj['id'])).json()
            # objDakat = requests.get( 'https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekttyper/' + str( obj['id'])).json()
        except JSONDecodeError: 
            print( "nettverket tryna, prøver på ny")
            sleep( 3 )
            objDakat = requests.get( 'https://nvdbapiles.atlas.vegvesen.no/vegobjekttyper/' + str( obj['id'])).json()
            # objDakat = requests.get( 'https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekttyper/' + str( obj['id'])).json()


        for egenskap in objDakat['egenskapstyper']: 
        
            if egenskap['viktighet'] not in mal.keys():
                mal[ egenskap['viktighet'] ] = 1
            else:
                mal[ egenskap['viktighet'] ] += 1


        data.append( mal )
mydf = pd.DataFrame( data )

