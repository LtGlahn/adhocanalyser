"""

Vi henter objekter med en spøring med paginering. Det går fint. Så henter vi 
lenkene de er stedfestet til en etter en, og det går ikke fint med historisk=true. 
For ex 
https://nvdbapiles-v3.atlas.vegvesen.no/vegnett/veglenkesekvenser/segmentert/121764?historisk=true 
som tydligvis altig går feil for en av objektene på vegen
Spefikt finner vi ikke 0.63878974@121764 for i går, men finner den for i dag 
når vi ikke søker historisk
Nyeste versjon av den lenkesekvensen er fra 23 januar, så vi vet at den burde komme med.
"""

from datetime import datetime 
import pandas as pd


import STARTHER
import nvdbapiv3 

if __name__ == '__main__': 

    resultater = [ ]

    vlenkid = str( 121764 )
    forb = nvdbapiv3.apiforbindelse()


    count = 0 
    while count < 1000: 
        count += 1 
        # Henter ikke-segmentert veglenkesekvens https://nvdbapiles-v3.atlas.vegvesen.no/vegnett/veglenkesekvenser/121764
        vlid = forb.les( '/vegnett/veglenkesekvenser/' + vlenkid ).json()
        veglenker = pd.DataFrame( vlid['veglenker'])
        fasit_veglenkenummer = set( veglenker['veglenkenummer'])
        
        # Henter segmentert vegnett   https://nvdbapiles-v3.atlas.vegvesen.no/vegnett/veglenkesekvenser/segmentert/121764?historisk=true
        tidspunkt = datetime.now()
        segmentert = pd.DataFrame( forb.les( '/vegnett/veglenkesekvenser/segmentert/' + vlenkid, params={'historisk' : 'true' }  ).json()  )

        segmentert_veglenkenummer = set( segmentert['veglenkenummer'])

        resultater.append( {
                    'tidspunkt'                    : str( tidspunkt),
                    'veglenkesekvensid'            : vlenkid, 
                    'Antall veglenker'             : len( veglenker ), 
                    'Antall SEGMENTERTE veglenker' : len( segmentert['veglenkenummer'].unique() ), 
                    'Antall vegsegmenter'          : len( segmentert ),
                    'Veglenkenummer som mangler'   : ','.join( [ str( x ) for x in list( fasit_veglenkenummer - segmentert_veglenkenummer )] )
                } )
        
    data = pd.DataFrame( resultater )
    minimum = data['Antall SEGMENTERTE veglenker'].min()
    maximum = data['Antall SEGMENTERTE veglenker'].max()
    print( f"{len(data)} forsøk, fasit={len(veglenker)} veglenker i ikke-segmentert vegnett, får mellom {minimum} og {maximum} veglenker i segmentert vegnett")