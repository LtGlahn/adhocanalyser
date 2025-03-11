""" 
Finner alle tre- og 4siffrende NVDB objekt ID 
"""
from requests.exceptions import ChunkedEncodingError
import requests 
import STARTHER
import nvdbapiv3 
import pandas as pd 




if __name__ == '__main__': 

    dakat = requests.get( 'https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekttyper.json' ).json()
    data = []
    countTotal = 0
    for objType in dakat:
        if objType['id'] > 792:
            sok = nvdbapiv3.nvdbFagdata( objType['id'])

            tempData = []
            countObjType = 0
            try:
                for etobj in sok:
                    countObjType += 1
                    if etobj['id'] < 10000:
                        data.append( etobj )
                        tempData.append( etobj )
            except (ValueError, ChunkedEncodingError) as e:
                feil = ( f"Feilmelding ved henting av type {objType['id']} {objType['navn']}: {e} ")
                print( feil )
                with open( 'logg.log', 'a') as f:
                    f.write( f"{feil}\n")

            else:
                tekst = f"{len(tempData)} objekter av type {objType['id']} {objType['navn']} med NVDB ID < 10000 av totalt {countObjType}"
                print( tekst )
                with open( 'logg.log', 'a') as f:
                    f.write( f"{tekst}\n")

    tekst = f"Ferdig med alle objekttyper!"
    print( tekst )
    with open( 'logg.log', 'a') as f:
        f.write( tekst )