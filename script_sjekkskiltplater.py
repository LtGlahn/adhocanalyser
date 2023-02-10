"""
Sjekker hvilke skiltplater som finnes eller savnes i det nye skiltplate-API'et 
"""
import requests
import pandas as pd

import STARTHER
import nvdbgeotricks 
 
if __name__ == '__main__':
    dakat = requests.get( 'https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekttyper/96.json' ).json()
    skiltnummer = [ x for x in dakat['egenskapstyper'] if x['navn'] == 'Skiltnummer'][0]


    url = 'https://trafikkskilt.utv.atlas.vegvesen.no/api/v1/skiltplate'
    data = [ ]
    for skilt in skiltnummer['tillatte_verdier']: 
        retval = { 'nvdbenum' : skilt['id'], 'kortnavn' : skilt['kortnavn'],
                    'Skiltnummer' : skilt['verdi'], 'sorteringsnummer' : skilt['sorteringsnummer']  }

        r = requests.get(url, params={'nvdbenum' : skilt['id']}, headers={'accept' : 'image/svg+xml'} )
        retval['url'] = r.url 
        if r.ok: 
            retval['STATUS'] = 'Finnes i API'
        else: 
            retval['STATUS'] = 'Mangler'
        data.append( retval )

    data = pd.DataFrame( data )