"""
Itererer over alle objekter i NVDB og leter etter dem som mangler stedfesting 
"""
from datetime import datetime 

import pandas as pd
import geopandas as gpd 
from shapely import wkt

import STARTHER 
import nvdbapiv3 

if __name__ == '__main__': 

    t0 = datetime.now( )
    objektTypeId = 87 

    sok = nvdbapiv3.nvdbFagdata(87 )

    data = []
    for etObj in sok: 

        if 'lokasjon' in etObj and 'kommuner' in etObj['lokasjon'] and len( etObj['lokasjon']['kommuner']) > 0: 
            pass # Normalsituasjon
        else: 

            flattObjekt = { 'nvdbID'    : etObj['id'], 
                    'objektTypeId'      : etObj['metadata']['type']['id'], 
                    'objektTypeNavn'    : etObj['metadata']['type']['navn'],
                    'versjon'           : etObj['metadata']['versjon'],
                    'startdato'         : etObj['metadata']['startdato']  
                }
            if 'sluttdato' in etObj['metadata']: 
                flattObjekt['sluttdato'] = etObj['metadata']['sluttdato']

            if 'egenskaper' in etObj: 
                flattObjekt.update( nvdbapiv3.egenskaper2records( etObj['egenskaper'], geometri=True, relasjoner=True ) )

            if 'geometri' in etObj: 
                flattObjekt['geometri'] = etObj['geometri']['wkt']
            else: 
                print(f"objektId {etObj['id']} har ikke geometri" )
            
            if 'lokasjon' in etObj and 'geometri' in etObj['lokasjon']: 
                flattObjekt['Geometri stedfesting'] = etObj['lokasjon']['geometri']['wkt']

            if 'relasjoner' in etObj: 
                flattObjekt['relasjoner'] = etObj['relasjoner']

            data.append( flattObjekt )

    mydf = pd.DataFrame( data )
    mydf['geometry'] = mydf['geometri'].apply( wkt.loads )
    myGdf = gpd.GeoDataFrame( mydf, geometry='geometry', crs=5973 )
    myGdf.to_file( 'belysningspunkt_historiskvegnett.gpkg', layer='belPunkt historisk veg', driver='GPKG' )    

    print( f"Tidsbruk: {datetime.now()-t0}")