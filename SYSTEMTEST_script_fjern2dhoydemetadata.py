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



def fiks2Dgeometri( mygeom:dict ): 
    """
    Leser geometriegenskapen og ser om vi har ugyldige metadata for 2D geometri

    Returnerer None hvis alt er OK

    Returnerer ny geometriegenskap som skal sendes til SKRIV hvis vi bør rette datafeil
    """
    geometri = from_wkt( mygeom['verdi'] )
    if geometri.has_z: 
        return False 

    lagNyGeometri = False 
    if 'høydereferanse' in mygeom and mygeom['høydereferanse'] != -1: 
        lagNyGeometri = True  
        STATISTIKK['høydereferanse'] += 1 
        STAT_HREF.add( mygeom['høydereferanse'] )
    if 'kvalitet'  in mygeom: 
        if 'målemetodeHøyde' in mygeom['kvalitet'] and mygeom['kvalitet']['målemetodeHøyde'] != -1: 
            STATISTIKK['målemetodeHøyde'] +=1 
            STAT_maalH.add( mygeom['kvalitet']['målemetodeHøyde'] )
            lagNyGeometri = True 
        if 'nøyaktighetHøyde' in mygeom['kvalitet'] and mygeom['kvalitet']['nøyaktighetHøyde'] != -1: 
            STATISTIKK['nøyaktighetHøyde'] += 1
            STAT_noyH.add( mygeom['kvalitet']['nøyaktighetHøyde'] )
            lagNyGeometri = True 

    if lagNyGeometri: 
        alleGaleGeoms.append( deepcopy( mygeom ))
        nyGeom = { 'typeId' : mygeom['id'], 'geometri' : [], 'operasjon': 'oppdater' }
        geomElement = { 'srid' : '5973', 'wkt' : mygeom['verdi'] }
        
        if 'kvalitet' in mygeom: 
            geomElement['kvalitet'] = {}
            for kvalKey in mygeom['kvalitet'].keys(): 
                # Ignorerer "målemetodeHøyde", "datafangstmetodeHøyde", "nøyaktighetHøyde"
                if kvalKey in [ "datafangstmetode", "målemetode",  "toleranse", "nøyaktighet", "synbarhet"]:
                    geomElement['kvalitet'][kvalKey] = mygeom['kvalitet'][kvalKey]

        if 'datafangstdato' in mygeom: 
            geomElement['datafangstdato'] = mygeom['datafangstdato']

        # Ignorerer høydereferanse-tagg 

        nyGeom['geometri'].append( geomElement )
        return nyGeom


def analyserObjekt( nvdbObj:dict ): 
    """
    Returnerer enten gyldig objekt til endringssett DELVIS_KORRIGER eller None 
    """

    korrigerEgenskaper = [ ] 
    for egenskap in nvdbObj['egenskaper']: 
        if egenskap['egenskapstype'] ==  "Geometri": 
            nyGeom = fiks2Dgeometri( egenskap )
            if nyGeom: 
                korrigerEgenskaper.append( nyGeom )

    if len( korrigerEgenskaper ) > 0: 

        nyttObj = { 'typeId' : nvdbObj['metadata']['type']['id'], 'nvdbId' : nvdbObj['id'], 'versjon' : nvdbObj['metadata']['versjon']  }
        datostempel = datetime.fromisoformat( nvdbObj['metadata']['sist_modifisert'])
        datostempel = datostempel + timedelta( 0, 15 ) # Legger på 15 sekund 
        nyttObj['validering'] = { 'lestFraNvdb' : datostempel.isoformat() }
        nyttObj['egenskaper'] = korrigerEgenskaper 

        return nyttObj 

STATISTIKK = { 'høydereferanse' : 0, 'målemetodeHøyde' : 0, 'nøyaktighetHøyde' : 0 }
STAT_HREF = set()
STAT_maalH = set()
STAT_noyH = set()
alleGaleGeoms = []

if __name__ == '__main__': 

    t0 = datetime.now()

    # for objType in [3, 5, 96]:
    for objType in [3]:
        data = []
        korriger_objekter = []
        t1 = datetime.now( )

        sok = nvdbapiv3.nvdbFagdata( objType, filter={'inkluder' : 'metadata,egenskaper'} ) 
        # sok.apiurl = 'nvdbapiles-v3-stm.utv.atlas.vegvesen.no'
        # sok.forbindelse.apiurl = 'https://nvdbapiles-v3-stm.utv.atlas.vegvesen.no'
        sok.forbindelse.apiurl = 'https://nvdbapiles-v3.test.atlas.vegvesen.no'


        countsok = 0 
        countKorrigert = 0
        for etObj in sok: 
            countsok += 1 
            kopi = deepcopy( etObj )
            nyttObj = analyserObjekt( etObj  )
            if nyttObj: 
                korriger_objekter.append( nyttObj )
                data.append( kopi )
                countKorrigert += 1 

            if countKorrigert >= 4: 
                break 
   
        with open( 'galHoydeMetadata_HREF_verdi99_' + str( objType) + '.json', 'w') as f: 
            json.dump( data, f, indent=4, ensure_ascii=False )

        print( f"Objekttype {objType}: Fant {len( korriger_objekter)} etter å ha sjekket {countsok} objekt i miljø {sok.forbindelse.apiurl} \n\ttidsbruk: {datetime.now()-t1}") 
    print( f"\ntidsbruk totalt: {datetime.now()-t0}")
