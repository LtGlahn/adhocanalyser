""" 
Datadump av vegnett og fagdata - ALLE fagdata - langs Ev134 
"""
from requests.exceptions import ChunkedEncodingError
import requests 
import STARTHER
import nvdbapiv3 
import pandas as pd 


def slettCol( mydf ): 
    """
    Fjerner overflødige kolonner fra dataframe 
    """

    slettCol = ['geometri', 'href', 'typeVeg_sosi', 'kontraktsområder', 'vegsystemreferanse', 'gate', 
                'relasjoner', 'målemetode']
    
    for SLETT in slettCol: 
        if SLETT in mydf.columns: 
            mydf.drop( columns=SLETT, inplace=True )

    return mydf 

if __name__ == '__main__': 


    # mittFilter = {'vegsystemreferanse' : 'EV134 S8D1 m0-1182'} # Liten testsample
    mittFilter = {'vegsystemreferanse' : 'EV134'}

    filnavn = 'Ev134dump/ev134dump_'

    # Laster ned vegnett 
    vegDf = pd.DataFrame( nvdbapiv3.nvdbVegnett(filter=mittFilter ).to_records())
    vegDf = slettCol( vegDf )
    vegDf.to_excel( filnavn + 'vegnett.xlsx', index=False )

    # Liste over vegobjekt vi ignorerer 
    ignorerListe = [
        343,  # Stedsnavn - totalt uinteressant for budsjettformål 
        562,  # Testobjekttype Ikke indeksert og dessuten totalt uinteressant 
        573,  # Svingerestriksjon totalt uinteressant for budsjettformål (og dessuten snål datahåndtering)
        793,  # NVDB dokumentasjon - Ikke indeksert og dessuten total uinteressant 
        871, # Historisk_Bruksklasse Skjermet og dessuten uinteressant 
        886, # Omkjøringsrute - Burde gått greit, men gir feilmelding fra LES pga datavolum (digert enkeltobjekt). Dog uinterssant
        890, # Bruksklasse, modulvogntog, uoffisiell - Skjermet 
        892,  # Bruksklasse, 12/65 mobilkran m.m., uoffisiell - Skjermet 
        894, # Bruksklasse, 12/100-vegnett, uoffisiell - Skjermet 
        895,  # VegROS Skjermet 
        901,  # Bruksklasse, tømmertransport, uoffisiell - Skjermet 
        903,  # Bruksklasse, spesialtransport, uoffisiell - Skjermet
        905,  # Bruksklasse, normaltransport, uoffisiell - Skjermet 
        50001  # NetNode Ikke indeksert - Irrelevant 
    ]


    dakat = requests.get( 'https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekttyper.json' ).json()

    # dakat = dakat[0:7] # Liten testsample
    for objType in dakat:
        if objType['id'] not in ignorerListe:
            myDf = pd.DataFrame( nvdbapiv3.nvdbFagdata( objType['id'], filter=mittFilter).to_records() )
            myDf = slettCol( myDf )
            if len( myDf ) > 0: 
                myDf.to_excel( f"{filnavn}_objType_{objType['id']:0>4}.xlsx", index=False )
                print( f"Objekttype {objType['id'] } {objType['navn']}: Hentet {len(myDf['nvdbId'].unique())} objekter fordelt over {len( myDf)} rader")
            else: 
                print( f"Objekttype {objType['id'] } {objType['navn']} - INGEN DATA returnert for filter {mittFilter}")

        else:
            print(  f"Ignorerer objekttype {objType['id']}" )
