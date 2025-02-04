"""
Sjekker hvilke objekttyper som har en lengde- eller arealegenskap som påvirkes av klipping
"""
import requests
import pandas as pd
from copy import deepcopy 

dakat = requests.get( 'https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekttyper').json()
data = []
for obj in dakat: 

    if obj['id'] < 20000 and obj['id'] != 793: 

        print( f"{obj['id']} {obj['navn']}")

        mal = { 'objtype' : obj['id'] , 'Navn' : obj['navn']}   
        objDakat = requests.get( 'https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekttyper/' + str( obj['id'])).json()
        # geomTyper = [ x for x in objDakat['egenskapstyper'] if 'eometri' in x['navn']]
        # lengdeEgenskaper = [ x for x in objDakat['egenskapstyper'] if 'lengde' in x['navn'].lower()]
        # arealEgenskaper  = [ x for x in objDakat['egenskapstyper'] if 'areal' in x['navn'].lower()]
        # mal['Antall geometrier'] = len( geomTyper )
        for egenskap in objDakat['egenskapstyper']: 

            record = deepcopy(mal )
            record['egenskapsId']   = egenskap['id']
            record['navn']          = egenskap['navn']
            record['viktighet']     = egenskap['viktighet']

            data.append( record )

mydf = pd.DataFrame( data )
mydf.to_csv( 'dakat_alleEgenskaper.csv', index=False, sep=';')