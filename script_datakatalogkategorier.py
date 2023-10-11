import json 
import requests
import pandas as pd 
import STARTHER
import nvdbapiv3 
import nvdbgeotricks


if __name__ == '__main__': 
    forb = nvdbapiv3.apiforbindelse()
    forb.velgmiljo( 'prodles')
    kategorier = forb.les( '/vegobjekttyper/kategorier' ).json()

    myList = []
    for enKat in kategorier: 
        kat = forb.les( '/vegobjekttyper', params={'inkluder' : 'alle', 'kategori' : enKat['id']} ).json()
        print( f"{enKat['navn']}")
        for objType in kat: 
            myDict = { 'Kategori id'                 : enKat['id'],
                      'Kategori navn'                : enKat['navn'],
                       'VegobjektType'               : objType['id'],
                        'Vegobjekt Navn'             : objType['navn'],
                         'kategori sorteringsnummer' : enKat['sorteringsnummer']
                        #  'kategori startdato'        : enKat['startdato'],
                        #  'kategori beskrivelse'      : enKat['beskrivelse']
                           }
            if 'startdato' in enKat: 
                myDict['kategori startdato'] = enKat['startdato']
            if 'beskrivelse' in enKat: 
                myDict['kategori beskrivelse'] = enKat['beskrivelse']

            myList.append( myDict)


    mydf = pd.DataFrame( myList )
    nvdbgeotricks.skrivexcel( 'NVDBkategorier.xlsx', mydf )
    # https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekttyper/kategorier
    # https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekttyper?inkluder=relasjonstyper&kategori=222