"""
Sjekker alle objekttyper og derles relasjoner
"""
import requests
import pandas as pd
from copy import deepcopy 
from time import sleep

import STARTHER
import nvdbapiv3 

def stedfestingtype( stdf:dict ) -> str: 
    """
    Analyserer stedfestingdefinisjon fra datakatalogen og returnerer hvilken type det er
    """
    
    if 'stedfesting' in stdf and  'stedfestingstype' in stdf['stedfesting']:
        return stdf['stedfesting']['stedfestingstype']
    elif 'stedfesting' in stdf and 'innhold' in stdf['stedfesting'] and 'stedfestingstype' in stdf['stedfesting']['innhold']: 
         return stdf['stedfesting']['innhold']['stedfestingstype']
    else: 
        print( f"Mangler stedfesting? {stdf['id']} {stdf['navn']}")
         
    return "MANGLER"


dakat = requests.get( 'https://nvdbapiles.atlas.vegvesen.no/vegobjekttyper').json()
# dakat = requests.get( 'https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekttyper').json()
data = []
minDakat = {}
for obj in dakat: 

    if obj['id'] < 20000 and obj['id'] != 793: 

        try: 
            objDakat = requests.get( 'https://nvdbapiles.atlas.vegvesen.no/vegobjekttyper/' + str( obj['id'])).json()
            # objDakat = requests.get( 'https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekttyper/' + str( obj['id'])).json()
        except JSONDecodeError: 
            print( "nettverket tryna, prøver på ny")
            sleep( 3 )
            objDakat = requests.get( 'https://nvdbapiles.atlas.vegvesen.no/vegobjekttyper/' + str( obj['id'])).json()
            # objDakat = requests.get( 'https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekttyper/' + str( obj['id'])).json()

        minDakat[obj['id']] = objDakat 
        print( f"{obj['id']} {obj['navn']}", flush=True)

for obj in minDakat.values(): 

        mal = { 'objtype' : obj['id'] , 'Navn' : obj['navn']}   

        for egenskap in obj['egenskapstyper']:
            if egenskap['egenskapstype'] == 'Assosiasjon': 
                nyMal = deepcopy( mal )
                nyMal.update( egenskap ) 
                nyMal['Mor stedfesting']    = stedfestingtype( obj )
                nyMal['Datter stedfesting'] = stedfestingtype(  minDakat[ nyMal['vegobjekttypeid'] ] )
                data.append( nyMal )

mydf = pd.DataFrame( data )

# mydf.columns = ['objtype', 'Navn', 'id', 'navn', 'kortnavn', 'sorteringsnummer',
#        'obligatorisk_verdi', 'skrivebeskyttet', 'avledet', 'sensitivitet',
#        'gruppesorteringsnummer', 'høydereferanse_tall',
#        'nøyaktighetskrav_grunnriss', 'nøyaktighetskrav_høyde',
#        'referansegeometri_tilstrekkelig', 'viktighet', 'kategori',
#        'tilknytning', 'vegobjekttypeid', 'innenfor_mor', 'assosiasjonskrav',
#        'egenskapstype', 'startdato', 'beskrivelse', 'sluttdato', 'veiledning' , 'Mor stedfesting', 'Datter stedfesting']
cols = ['objtype', 'Navn', 'id', 'navn', 
       'tilknytning', 'vegobjekttypeid', 'innenfor_mor', 'Mor stedfesting', 'Datter stedfesting']
data = mydf[cols ]
