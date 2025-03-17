"""
Laster ned elektrisk anlegg for 30-103 Østfold Sør 2022-2028 på Fv130 og følger barne-relasjonene 
derfra og ned. Debugger Jostein H sin sak 
"""
import pandas as pd 
import geopandas as gpd 
from shapely import wkt

import STARTHER
import nvdbapiv3 

def plukkUtAssosiasjon( input:dict )-> dict:
    """
    Returnerer dictionary med ID for assosiasjon og alle NVDB ID som inngår i assosiasjonen
    """

    temp = set()
    for rel in input['innhold']: 
        temp.add( rel['verdi'])

    return { f"ASS {input['id']}" : temp }

def plukkUtAssosiasjoner( input:list ) -> dict: 
    """
    Plukker ut alle assosiasjoner fra listen med egenskaper
    """
    ass =  [ x for x in input if 'Assosiert' in x['navn']  ]
    nyAss = {}
    for x in ass: 
        nyAss.update( plukkUtAssosiasjon( x ))

    return nyAss

def behandleObjekt( obj:dict ): 
    etobj = { 'nvdbId' : obj['id'], 
                 'objektType' : f"{obj['metadata']['type']['id']} {obj['metadata']['type']['navn']}",
                 'geometry' : wkt.loads( obj['geometri']['wkt']) }
    assosiasjoner = plukkUtAssosiasjoner(obj['egenskaper'])
    barneRelasjoner = {}
    # etobj.update( assosiasjoner )

    if 'relasjoner' in obj and 'barn' in obj['relasjoner']: 
        for barn in obj['relasjoner']['barn']: 
            barneRelasjoner[f"barn {barn['listeid']}"] = set( barn['vegobjekter'])

    # Sjekker at "barn"-relasjoner og "Assosierte" egenskaper stemmer overens 
    ass = [ x for x in list( etobj.keys() ) if 'ASS' in x ]
    QA = ''
    for assKey in ass: 
        (junk, relId) = assKey.split()
        barnKey = f"barn {relId}"
        if barnKey in barneRelasjoner: 
            diff1 = etobj[assKey]  - etobj[barnKey]
            diff2 = etobj[barnKey] - etobj[assKey]
                        
            if len( diff1 ) > 0: 
                QA += f" | Assosierte objekt som mangler i barn-relasjon {relId}: {'.'.join( [ str(x) for x in diff1 ] )}"

            if len( diff2 ) > 0: 
                QA += f" | For MANGE barn i barn-relasjon {relId}: {'.'.join( [ str(x) for x in diff2 ] )}"

        else: 
            print( f"MANGLER RELASJON {relId} i objekt {etobj['nvdbId']} relasjon.barn element '{barnKey}'")

    if QA == '': 
        etobj['QA relasjoner'] = 'objektets assosiasjon-egenskaper stemmer med angitte barnerelasjoner'

    # Sjekker at objektet ikke er lukket
    if 'sluttdato' in obj['metadata']:
        etobj['SLUTTDATO'] = obj['metadata']['sluttdato']
        etob['QA relasjoner'] += f"| Objektet er LUKKET"

    # Legger på vegsystemreferanse
    etobj['vref'] = ','.join(  [ x['kortform'] for x in obj['lokasjon']['vegsystemreferanser'] ] )
    
    # Legger på kontraktsområder
    etobj['kontraktsomrader'] = [x['navn'] for x in obj['lokasjon']['kontraktsområder'] ]

    return etobj 

def rekursivt_sjekkFamilie( nvdbId:int, staMMor=None, slektstre=None  )->dict: 
    """
    Sjekker rekursivt alle barn og barnebarn og kvalitetsikrer alle relasjonene 
    """
    returdata = []
    

    obj = nvdbapiv3.finnid( nvdbId, kunfagdata=True )

    if staMMor is None: 
        staMMor = {}
        staMMor['stammorId'] = nvdbId
        staMMor['Stammor Type'] = f"{obj['metadata']['type']['id']} {obj['metadata']['type']['navn']}"

    if isinstance( slektstre, str):
        slektstre += f" -> {obj['metadata']['type']['id']}:{nvdbId}"

    else: 
        slektstre = f"{obj['metadata']['type']['id']}:{nvdbId}"

    # Sjekker dette objektets relasjoner og legger på informasjon om overliggende hierarki
    objRetur = behandleObjekt( obj ) 
    objRetur.update( staMMor )
    objRetur['slektstre'] = slektstre 
    returdata.append( objRetur )



    # Jobber oss rekursivt gjennom alle relasjoner 
    assosiasjoner = plukkUtAssosiasjoner(obj['egenskaper'])
    for assType in assosiasjoner.keys(): 
        for eiDatter in assosiasjoner[assType]: 
            returdata.extend( rekursivt_sjekkFamilie( eiDatter, staMMor=staMMor, slektstre=slektstre ))

    return returdata 
if __name__ == '__main__': 
    mittfilter = {'kontraktsomrade' : '30-103 Østfold Sør 2022-2028', 'vegsystemreferanse' : 'Fv130' }
    sok = nvdbapiv3.nvdbFagdata( 461, filter=mittfilter )

    data = []
    rekursivedata = []
    for obj in sok:

        data.append( behandleObjekt( obj ) )
        rekursivedata.extend( rekursivt_sjekkFamilie( obj['id'] ))


    mydf = pd.DataFrame( rekursivedata )
    mydf.to_excel( 'relasjonseksempelQA.xlsx', index=False )