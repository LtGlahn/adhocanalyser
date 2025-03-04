"""
Iterer over alle bruksklasse-data og finner dem burde vært lukket pga følgeoppdatering

(Dvs stedfestet på historisk vegnett, og mangler derfor data på "vegsegmenter")

"""
import pandas as pd

import STARTHER
import nvdbapiv3


if __name__ == '__main__': 

    objTyper = [900, 901, 902, 903, 904, 905 ]
    mittfilter = { 'kartutsnitt' : '172134.257,6728688.089,173068.899,6729185.507' }
    
    forb = nvdbapiv3.apiforbindelse()
    forb.login( miljo='prodles' )
    data = []
    for objType in objTyper: 
        # sok = nvdbapiv3.nvdbFagdata( objType, filter=mittfilter )
        sok = nvdbapiv3.nvdbFagdata( objType  )
        sok.forbindelse = forb 

        for obj in sok: 
            if not 'vegsegmenter' in obj or len( obj['vegsegmenter']) == 0:
                data.append( obj )

    if len( data ) > 0: 
        mydf = pd.DataFrame( nvdbapiv3.nvdbfagdata2records( data, vegsegmenter=False ))
        mydf['vegkart'] = 'https://vegkart.atlas.vegvesen.no/#valgt:' + \
                            mydf['nvdbId'].astype(str)  + ':' + \
                            mydf['objekttype'].astype(str)

