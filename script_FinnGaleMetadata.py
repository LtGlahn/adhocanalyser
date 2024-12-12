"""
Skal finne ugyldige metadata for både 2D og 3D geometrier

Fra jira-sak NVDB-14179

Objekter med XYZ-geometri skal ha 5 parameter (datafangstmetode, nøyaktighet, synbarhet, datafangstmetode høyde og nøyaktighet høyde).

Objekter med bare XY-geometri skal ha 3 parametere (datafangstmetode, nøyaktighet og synbarhet)

Dersom dette ikke er infridd skal endringssettet avvises med beskjed om hvilken parameter som mangler verdi.

Dersom Objekt uten Z-verdi har verdi for høydekvalitet skal endringssettet avvises med beskjed om at høyde ikke kan ha kvalitet når det mangler høyde.

"""

from shapely import from_wkt
import json
import requests 
from datetime import datetime, timedelta
from copy import deepcopy 
import pandas as pd 

import STARTHER
import nvdbapiv3 
import skrivnvdb

def sjekkGeometriMetadata( egenskap:dict ): 
    """
    Selve valideringsfunksjonen. Returnerer True dersom ugyldig
    """
    datafangstmetoder = ['dig','fot','gen','lan','pla','sat','byg','ukj']
    syntbarhet = [ 0, 1, 2, 3]

    try:             
    
        if egenskap['kvalitet']['datafangstmetode'] not in datafangstmetoder: 
            return True 
        
        if egenskap['kvalitet']['nøyaktighet'] < 0: 
            return True 

        if egenskap['kvalitet']['synbarhet'] not in syntbarhet: 
            return True 

        # Objekter med XYZ-geometri skal også ha datafangstmetode høyde og nøyaktighet høyde.
        geometri = from_wkt( egenskap['verdi'] )
        if geometri.has_z: 

            if egenskap['kvalitet']['datafangstmetodeHøyde'] not in datafangstmetoder: 
                return True 
            
            if egenskap['kvalitet']['nøyaktighetHøyde'] <= 0: 
                return True 

    except KeyError: 
        return True 

    # Returnerer kun False dersom ingen av sjekkene over feiler             
    return False 




def finnUgyldigeMetadata( mittObj:dict ):
    """
    Analyserer et objekt og sjekker for gyldige metadata 

    Returnerer True dersom objektet ikke har korrekte metadata, eller False om alt er OK

    Eks på godkjent geometriegenskap
        "kvalitet": {
                "målemetode": 96,
                "datafangstmetode": "sat",
                "nøyaktighet": 2,
                "synbarhet": 0,
                "målemetodeHøyde": 96,
                "datafangstmetodeHøyde": "sat",
                "nøyaktighetHøyde": 3,
                "maksimaltAvvik": -1
            },
    """

    objektetFeiler = False 
    for egenskap in mittObj['egenskaper']: 
        if egenskap['egenskapstype'] ==  "Geometri": 

            TF = sjekkGeometriMetadata( egenskap )
            if TF == True: 
                objektetFeiler = True 
                # Tar vare på kopi til analyseformål 
                geomkopi = deepcopy( egenskap )
                geomkopi['nvdbId'] = mittObj['id']
                geomkopi['objektType'] = mittObj['metadata']['type']['id']
                myWkt = from_wkt( geomkopi['verdi'])
                geomkopi['3d'] = myWkt.has_z

                kvalitet = geomkopi.pop( 'kvalitet', None )
                if kvalitet: 
                    geomkopi.update( kvalitet )
                galeGeom.append( geomkopi)

    return objektetFeiler

galeGeom = []
alleGaleObj = []

if __name__ == '__main__': 

    t0 = datetime.now()
    for objType in [5, 14, 7, 199, 95, 96]:

        # print( f"Analyserer objekttype {objType}")

        data = []

        # forb = nvdbapiv3.apiforbindelse()
        # forb.login( miljo='testskriv')

        sok = nvdbapiv3.nvdbFagdata( objType, filter={'inkluder' : 'metadata,egenskaper'} ) 
        # sok.miljo('test')
        # assert 'test' in sok.apiurl, f"Klarte ikke velge miljø TESTPROD???"

        countsok = 0 
        countKorrigert = 0
        for etObj in sok: 
            countsok += 1 
            FEILER = finnUgyldigeMetadata( etObj  )
            if FEILER: 
                alleGaleObj.append( etObj )
                countKorrigert += 1 

            # if countsok % 10000 == 0: 
            #     print( f"\tSøk {countsok} av {sok.antall} for objekttype {objType}")

            # if countKorrigert >= 1000: 
            #     break 
   
        print( f"Objekttype {objType}: Fant {countKorrigert} etter å ha sjekket {countsok} objekt. Feilrate: {round( 100 * countKorrigert / countsok )} %")
    
    print( f"Tidsbruk totalt: {datetime.now()-t0}")

    mydf = pd.DataFrame( galeGeom)