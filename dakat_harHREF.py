"""
Sjekker alle objekttyper og tar vare på utvalgte geometriegenskaper (her: Kun høydereferanse)
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
        geomTyper = [ x for x in objDakat['egenskapstyper'] if 'eometri' in x['navn']]
        mal['Antall geometrier'] = len( geomTyper )
        for geom in geomTyper: 
            record = deepcopy(mal )
            record['egenskapsId'] = geom['id']
            record['navn'] = geom['navn']
            record['viktighet'] = geom['viktighet']
            valgfrie = ['høydereferanse', 'høydereferanse_tall' ]
            for valg in valgfrie: 
                if valg in geom: 
                    record[valg] = geom[valg]

            data.append( record )

mydf = pd.DataFrame( data )
mydf.to_csv( 'dakat_geomvarianter.csv', index=False, sep=';')