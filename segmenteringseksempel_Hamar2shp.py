"""
Eksempel på bruk av segmenteringsrutine: 
    Vegnett + trafikkmengde + fartsgrense for Oslo kommune
"""
from datetime import datetime 
import pandas as pd
import geopandas as gpd 
from shapely import wkt

import STARTHER
import nvdbapiv3 
import segmentering
import nvdbgeotricks


if __name__ == '__main__': 
    t0 = datetime.now()

    # Henter vegnett 
    vegnett = pd.DataFrame( nvdbapiv3.nvdbVegnett( filter={'kommune' : 3403, 'veglenketype' : 
                                                            'hoved,konnektering',
                                                            'trafikantgruppe' : 'K', 
                                                            'vegsystemreferanse' : 'Ev,Rv,Fv'}).to_records() )
    


    fartsgrense = pd.DataFrame( nvdbapiv3.nvdbFagdata(105, filter={'kommune' : 3403, 'vegsystemreferanse' : 'Ev,Rv,Fv'}).to_records())
    trafikkmengde = pd.DataFrame( nvdbapiv3.nvdbFagdata(540, filter={'kommune' : 3403, 'vegsystemreferanse' : 'Ev,Rv,Fv'}).to_records())

    # Lager GeodataFrame     
    vegnett         = gpd.GeoDataFrame( vegnett,       geometry=      vegnett['geometri'].apply( wkt.loads), crs=5973 )
    fartsgrense     = gpd.GeoDataFrame( fartsgrense,   geometry=  fartsgrense['geometri'].apply( wkt.loads), crs=5973 )
    trafikkmengde   = gpd.GeoDataFrame( trafikkmengde, geometry=trafikkmengde['geometri'].apply( wkt.loads), crs=5973 )

    print( f"Tidsbruk datanedlasting: {datetime.now()-t0}")
    # Legger på gatenavn
    vegnett['gatenavn'] = vegnett['gate'].apply( lambda x : x['navn'] if isinstance( x, dict) else '' )

    # Tar kun med disse kolonnene fra vegnettet:
    vegnett_col = ['gatenavn', 'veglenkesekvensid', 'startposisjon', 'sluttposisjon',
        'type', 'detaljnivå', 'typeVeg', 
        'feltoversikt', 'geometri', 'lengde', 'fylke',
       'kommune',  'vref',
       'vegkategori', 'fase', 'nummer',
        'trafikantgruppe', 'adskilte_lop', 'medium', 'geometry' ]
    
    # Og kun disse kolonnene fra fartsgrense:  
    fart_col = ['objekttype', 'Fartsgrense', 'veglenkesekvensid',
       'vref',  'startposisjon', 'sluttposisjon',
       'segmentlengde', 'geometry']
    
    # Og kun disse fra trafikkmengde: 
    traf_col = ['objekttype', 'År, gjelder for',
       'ÅDT, total', 'ÅDT, andel lange kjøretøy', 'Grunnlag for ÅDT',
       'veglenkesekvensid', 'vref', 
       'startposisjon', 'sluttposisjon', 'geometry']
    
    t1 = datetime.now()
    segmentert = segmentering.segmenter( vegnett[vegnett_col], [ fartsgrense[fart_col], trafikkmengde[traf_col] ])
    print( f"Tidsbruk segmentering: {datetime.now()-t1}")

    filnavn =  'hamar_segmentertveg_' + str( datetime.now() )[0:10] + '.gpkg'

    segmentert.to_file( filnavn )

    # vil du heller ha Esri fil-geodatabase? (.GDB, også kalt FGDB)
    # filnavn =  'oslo_segmentertveg_' + str( datetime.now() )[0:10] + '.gdb'
    # segmentert.to_file( filnavn,  driver= 'OpenFileGDB' )

    # Tricks for å døpe om lange kolonnenavn => 10 karrakterer
    col = list( segmentert.columns )
    langenavn = { x : 'nyttNavn'  for x in col if len( x ) > 9 }

    segmentert.reset_index( inplace=True )
    nyeNavn = {'Fartsgrense': 'Fartsgr',
                'segmentlengde': 'lengde',
                'veglenkesekvensid': 'vlenkid',
                'startposisjon': 'startpos',
                'sluttposisjon': 'sluttpos',
                'feltoversikt': 'felt',
                'vegkategori': 'vegkat',
                'År, gjelder for': 'AADT_aar',
                'ÅDT, total': 'AADT',
                'ÅDT, andel lange kjøretøy': 'AADT_lang',
                'Grunnlag for ÅDT': 'AADTgrun', 
                'index' : 'rownumber'}
    
    segmentert.rename( columns=nyeNavn, inplace=True )
    segmentert.to_file(       'hamarsegmentERF/hamarsegment.shp' )
    nvdbgeotricks.skrivexcel( 'hamarsegmentERF/hamarsegment.xlsx', segmentert )


