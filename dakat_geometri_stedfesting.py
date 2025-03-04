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

    if obj['id'] < 20000 and obj['id'] != 793 and obj['id'] != 608: 
    # if obj['id'] == 855: 

        print( f"{obj['id']} {obj['navn']}", flush=True)


        objDakat = requests.get( 'https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekttyper/' + str( obj['id']), headers=headers ).json()
        mal = { 'objtype' : obj['id'] , 'Navn' : obj['navn'], 'stedfesting' : objDakat['stedfesting']['navn'] }   
        geomTyper = [ x for x in objDakat['egenskapstyper'] if 'eometri' in x['navn']]
        mal['Antall geometrier'] = len( geomTyper )
        for geom in geomTyper: 
            record = deepcopy(mal )
            record['ETid'] = geom['id']
            record['ETnavn'] = geom['navn']
            record['egenskapstype'] = geom['egenskapstype']
            record['ETviktighet'] = geom['viktighet']
            record['innenfor_mor'] = geom['innenfor_mor']
            record['geometritype'] = geom['geometritype']

            # valgfrie = ['høydereferanse', 'høydereferanse_tall' ]
            if 'høydereferanse_tall' in geom and geom['høydereferanse_tall'] > 0: 
                record['DAKAT høydereferanse_tall'] = geom['høydereferanse_tall']

            data.append( record )

mydf = pd.DataFrame( data )


# resultat = mydf.groupby( ['objtype', 'Navn', 'Antall geometrier', 'ETnavn', 'ETviktighet', 'DAKAT høydereferanse_tall', 'vegobjekt_høydereferanse'], dropna=False).agg( { 'vegobjektId' : 'count' } ).reset_index()
# resultat.to_excel( 'nvdbobjMedHREF.xlsx', index=False )
