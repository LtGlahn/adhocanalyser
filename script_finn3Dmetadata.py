"""
Fjerner metadata relatert til høyde for 2D geometrier. 
"""

from shapely import from_wkt
import json
import requests 
from datetime import datetime, timedelta
from copy import deepcopy 

import STARTHER
import nvdbapiv3 
import skrivnvdb



def finn3Dmetadata( mygeom:dict ): 
    """
    Leser geometriegenskapen og ser om vi har ugyldige metadata for 2D geometri

    Returnerer False eller True

    Returnerer ny geometriegenskap som skal sendes til SKRIV hvis vi bør rette datafeil
    """
    
    lagNyGeometri = False 
    geometri = from_wkt( mygeom['verdi'] )
    if not geometri.has_z: # Ser KUN på 3D geometrier  
        return False  

    if 'høydereferanse' in mygeom and mygeom['høydereferanse'] in [0, 1, 99, 9999]: 
        lagNyGeometri = True  
    # if 'kvalitet'  in mygeom: 
    #     if 'målemetodeHøyde' in mygeom['kvalitet'] and mygeom['kvalitet']['målemetodeHøyde'] != -1: 
    #         STATISTIKK['målemetodeHøyde'] +=1 
    #         STAT_maalH.add( mygeom['kvalitet']['målemetodeHøyde'] )
    #         lagNyGeometri = True 
        # if 'nøyaktighetHøyde' in mygeom['kvalitet'] and mygeom['kvalitet']['nøyaktighetHøyde'] != -1: 
        #     STATISTIKK['nøyaktighetHøyde'] += 1
        #     STAT_noyH.add( mygeom['kvalitet']['nøyaktighetHøyde'] )
        #     lagNyGeometri = True 

    return lagNyGeometri


def analyserObjekt( nvdbObj:dict ): 
    """
    Returnerer TRUE eller FALSE hvis vi er happy med metadata geometri  
    """

    korrigerEgenskaper = [ ]
    gyldig3D = False  
    for egenskap in nvdbObj['egenskaper']: 
        if egenskap['egenskapstype'] ==  "Geometri": 
            gyldig3D = finn3Dmetadata( egenskap )
            
    return gyldig3D 


if __name__ == '__main__': 

    t0 = datetime.now()
    for objType in [5, 14, 7, 199, 96]:

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
            kopi = deepcopy( etObj )
            gyldig3D = analyserObjekt( etObj  )
            if gyldig3D == True: 
                data.append( kopi )
                countKorrigert += 1 

            if countKorrigert >= 4: 
                break 
   
        with open( '3dgeomMetadata_' + str( objType) + '.json', 'w') as f: 
            json.dump( data, f, indent=4, ensure_ascii=False )

        print( f"Objekttype {objType}: Fant {len( data)} etter å ha sjekket {countsok} objekt")
