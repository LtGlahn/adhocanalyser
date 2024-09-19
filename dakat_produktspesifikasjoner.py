"""
Sjekker alle objekttyper og returnerer 200 + lenke for de objekttypene som har produktspesifikasjon
"""
import requests
import pandas as pd
from copy import deepcopy 

dakat = requests.get( 'https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekttyper').json()
alleEgenskaper = []
for obj in dakat: 

    # if obj['id'] < 20000 and obj['id'] != 793: 
    mal = { 'objtype' : obj['id'] } # , 'Navn' : obj['navn']}   
    url = 'https://www.vegvesen.no/nvdb/datakatalog/eksport/produktspesifikasjon/' + str( obj['id'] ) + '.pdf'
    r = requests.get( url )
    mal['httpStatus'] = r.status_code
    if r.ok: 
        mal['fungerendeLenke'] = url
    alleEgenskaper.append( mal )

prodspek = pd.DataFrame( alleEgenskaper )
prodspek.to_csv( 'harProduktspesifikasjon.csv', index=False)