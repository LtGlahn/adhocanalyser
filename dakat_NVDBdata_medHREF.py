"""
Sjekker alle objekttyper og tar vare på utvalgte geometriegenskaper (her: Kun høydereferanse)
"""
import requests
import pandas as pd
from copy import deepcopy 

import STARTHER
import nvdbapiv3 

headers = { "X-Client" : "nvdbapi.py fra Nvdb gjengen, vegdirektoratet",
 "X-Kontaktperson" : "jan.kristian.jensen@vegvesen.no" }

dakat = requests.get( 'https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekttyper').json()
data = []
for obj in dakat: 

    if obj['id'] < 20000 and obj['id'] != 793: 
    # if obj['id'] == 855: 

        print( f"{obj['id']} {obj['navn']}")

        mal = { 'objtype' : obj['id'] , 'Navn' : obj['navn']}   
        objDakat = requests.get( 'https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekttyper/' + str( obj['id']), headers=headers ).json()
        geomTyper = [ x for x in objDakat['egenskapstyper'] if 'eometri' in x['navn']]
        mal['Antall geometrier'] = len( geomTyper )
        for geom in geomTyper: 
            record = deepcopy(mal )
            record['ETnavn'] = geom['navn']
            record['ETviktighet'] = geom['viktighet']
            # valgfrie = ['høydereferanse', 'høydereferanse_tall' ]
            if 'høydereferanse_tall' in geom and geom['høydereferanse_tall'] > 0: 
                record['DAKAT høydereferanse_tall'] = geom['høydereferanse_tall']

                sok = nvdbapiv3.nvdbFagdata( obj['id'] )
                for vegobjekt in sok: 
                    geometrier = [ x for x in vegobjekt['egenskaper'] if x['id'] == geom['id']]
                    if len( geometrier ) > 0: 
                        nyRec = deepcopy( record )
                        nyRec['vegobjektId'] = vegobjekt['id']
                        kandidater = [ x for x in geometrier[0].keys() if 'øyderef' in x]
                        for kan in kandidater: 
                            nyRec['vegobjekt_' + str(kan)] = geometrier[0][kan]

                        data.append( nyRec )

mydf = pd.DataFrame( data )


# resultat = mydf.groupby( ['objtype', 'Navn', 'Antall geometrier', 'ETnavn', 'ETviktighet', 'DAKAT høydereferanse_tall', 'vegobjekt_høydereferanse'], dropna=False).agg( { 'vegobjektId' : 'count' } ).reset_index()
# resultat.to_excel( 'nvdbobjMedHREF.xlsx', index=False )
