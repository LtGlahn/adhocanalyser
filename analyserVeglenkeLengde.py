"""
Analyserer en veglenkesekvekvens for å sjekke dataintegritet lengde vegnett == geometrisk lengde
"""
import pandas as pd
import geopandas as gpd
from shapely import wkt
from tqdm import tqdm

import STARTHER
import nvdbapiv3 
import nvdbgeotricks 

def sok2veglengdeAnalyse( sokeobjekt ): 
    """
    Itererer over søkeobjekt nvdbapiv3.nvbdVegnett(), regner ut forhold mellom låst lengde / geometrisk lengde og returnerer GDF
    """

    segmenter = []
    veglenkesekvens = {}

    count = 0
    for vl in sokeobjekt:
        if count == 0: 
            print( f"Henter {sokeobjekt.antall} vegsegmenter")
        count += 1

        if count == 1000 or count == 5000 or count % 10000 == 0: 
            print( 'vegsegment', count, 'av', sokeobjekt.antall)

        vl['geometrilengde'] = vl['geometri']['lengde'] 
        vl = nvdbapiv3.flatutvegnettsegment( vl )
        vl['geometry'] = wkt.loads( vl['geometri'] )
        vl['geometrilengde2D'] = vl['geometry'].length 
        vl['lengdeavvik_m'] = vl['geometrilengde'] - vl['lengde']
        vl['lengdeavvik_prosent'] =  100* vl['lengdeavvik_m'] / vl['geometrilengde'] 

        # Henter veglenkesekvens for å sjekke låst lengde
        vid = vl['veglenkesekvensid']
        if not vid in veglenkesekvens: 
            r = sokeobjekt.forbindelse.les( '/vegnett/veglenkesekvenser/' + str(vid) )
            if r.ok: 
                temp = r.json()
            else:
                print( f"Fikk ikke hentet veglenkesekvens {vid} : HTTP {r.status_code} {r.text}")
                temp = { 'låst_lengde' : None, 'lengdeTotal' : None }

            veglenkesekvens[vid] = { 
                    'låst_lengde' : temp['låst_lengde'], 
                    'lengdeTotal' : temp['lengde']  }


        vl['låst_lengde'] = veglenkesekvens[vid]['låst_lengde']
        vl.pop( 'href', None )
        metadata = vl.pop( 'metadata', {})
        junk = vl.pop( 'typeVeg_sosi', {})
        junk = vl.pop( 'kontraktsområder', {})
        junk = vl.pop( 'riksvegruter', {})
        junk = vl.pop( 'geometri', '' )
        vref = vl.pop( 'vegsystemreferanse', {})
        vref = vl.pop( 'ankerpunktmeter', '')
        vref = vl.pop( 'kryssdel', '')

        vl.update( metadata )
        
        segmenter.append( vl )        

    mydf = pd.DataFrame( segmenter )
    myGdf = gpd.GeoDataFrame( mydf, geometry='geometry', crs=5973)
    return myGdf 


def hentveglenkesekvens( veglenkesekvensId:int, forb=None, segmentert=False  ): 
    """
    Henter ikke-segmenterte veglenker for angitt veglenkesekvens ID og regner ut geometrisk lengde. 

    Returnerer geodataframe

    ARGUMENTS
        veglenkesekvensid: int (heltall), ID til NVDB veglenkesekvens

    KEYWORDS
        forb: None eller en forekomst av nvdbapiv3.  

        segmenentert: False . Sett lik True hvis du ønsker analyse av segmentert vegnett
    """
    if not forb: 
        forb = nvdbapiv3.apiforbindelse()


    if not isinstance( veglenkesekvensId, list): 
        veglenkesekvensId = [ veglenkesekvensId ]

    veglenker = []
    for VID in veglenkesekvensId: 

        if isinstance( VID, str): 
            veglenkesekvensId = int( VID )

        assert isinstance( VID, int), "Feil input datatype, veglenkesekvensId må være heltall"

        r = forb.les(  '/vegnett/veglenkesekvenser/' + str( VID ))
        if not r.ok: 
            print(f"Feil ved henting av veglenkesekvensId {VID}")
            print("      respons fra NVDB api LES: HTTP {r.status_code} \n{r.text}")
        else: 
            
            data = r.json()
            if not segmentert:  
                for vl in data['veglenker']: 
                    vl['geometrilengde'] = vl['geometri']['lengde'] 
                    vl = nvdbapiv3.flatutvegnettsegment( vl )
                    vl['veglenkesekvensid'] = data['veglenkesekvensid']
                    vl['geometry'] = wkt.loads( vl['geometri']  )
                    vl['geometrilengde2D'] = vl['geometry'].length 
                    vl['lengdeavvik_m'] = vl['geometrilengde'] - vl['lengde']
                    vl['lengdeavvik_prosent'] =  100* vl['lengdeavvik_m'] / vl['geometrilengde'] 
                    vl['låst_lengde'] = data['låst_lengde']

                    veglenker.append( vl )

            else: 
                r2 = forb.les( '/vegnett/veglenkesekvenser/segmentert/' + str( VID ))
                data2 = r2.json()
                for vl in data2: 
                    vl['geometrilengde'] = vl['geometri']['lengde'] 
                    vl = nvdbapiv3.flatutvegnettsegment( vl )
                    vl['geometry'] = wkt.loads( vl['geometri']  )
                    vl['geometrilengde2D'] = vl['geometry'].length 
                    vl['lengdeavvik_m'] = vl['geometrilengde'] - vl['lengde']
                    vl['lengdeavvik_prosent'] =  100* vl['lengdeavvik_m'] / vl['geometrilengde'] 
                    vl['låst_lengde'] = data['låst_lengde']
                    vl.pop( 'href', None )
                    vl.pop( 'geometri', None )
                    vl.pop( 'kontraktsområder', None )
                    vl.pop( 'riksvegruter', None )

                    metadata = vl.pop( 'metadata', {})
                    vl.update( metadata )
                    
                    veglenker.append( vl )



    myGdf = gpd.GeoDataFrame( veglenker, geometry='geometry', crs=5973 )
    return myGdf 




if __name__ == '__main__': 
    # junk = hentveglenkesekvens( '0000')
    myGdf = hentveglenkesekvens( 121461 )
    myGdf2 = hentveglenkesekvens( 121461, segmentert=True )

