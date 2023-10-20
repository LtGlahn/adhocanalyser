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


if __name__ == '__main__': 
    t0 = datetime.now()

    # Henter vegnett 
    vegnett = pd.DataFrame( nvdbapiv3.nvdbVegnett( filter={'fylke' : 3, 'veglenketype' : 
                                                            'hoved,konnektering',
                                                            'trafikantgruppe' : 'K'}).to_records() )
    


    fartsgrense = pd.DataFrame( nvdbapiv3.nvdbFagdata(105, filter={'fylke' : 3}).to_records())
    trafikkmengde = pd.DataFrame( nvdbapiv3.nvdbFagdata(540, filter={'fylke' : 3}).to_records())


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

    filnavn =  'oslo_segmentertveg_' + str( datetime.now() )[0:10] + '.gpkg'


    segmentert.to_file( filnavn )

    # vil du heller ha Esri fil-geodatabase? (.GDB, også kalt FGDB)
    # filnavn =  'oslo_segmentertveg_' + str( datetime.now() )[0:10] + '.gdb'
    # segmentert.to_file( filnavn,  driver= 'OpenFileGDB' )
    # 
    # Eventuelt gi ditt eget navn på vegnettet
    # segmentert.to_file( filnavn, layer='vegnett', driver= 'OpenFileGDB' )

##############################################################
###
### Resultat fra kjøring på Jans PC 
###
# In [28]: %run script_segmenteringseksempel_Oslo.py
# Eksport av 97643 vegsegmenter kommer til å ta tid...
# Vegsegment 1000 av 97643
# Vegsegment 5000 av 97643
# Vegsegment 10000 av 97643
# Vegsegment 20000 av 97643
# Vegsegment 30000 av 97643
# Vegsegment 40000 av 97643
# Vegsegment 50000 av 97643
# Vegsegment 60000 av 97643
# Vegsegment 70000 av 97643
# Vegsegment 80000 av 97643
# Vegsegment 90000 av 97643
# Eksport av 44529 objekter kommer til å ta tid...
# Objekt 1000 av 44530
# Objekt 5000 av 44530
# Objekt 10000 av 44530
# Objekt 20000 av 44530
# Objekt 30000 av 44530
# Objekt 40000 av 44530
# Manglende geometri-element for 1 vegobjekter fra dette søket
# nvdbFagdata: Søkeobjekt for vegobjekter fra NVDB api V3
# ObjektType: 105 Fartsgrense
# Filtere
# {
#     "fylke": 3
# }
# Parametre som styrer responsen:
# {
#     "inkluder": [
#         "alle"
#     ]
# }
# Statistikk fra NVDB api V3
# {
#     "antall": 44529,
#     "lengde": 3786696.135
# }
# Pagineringsinfo: Antall objekt i databuffer= 0
# {
#     "antall": 1000,
#     "hvilken": 1,
#     "antallObjektReturnert": 44530,
#     "meredata": false,
#     "initielt": false,
#     "dummy": false
# }
# fra miljø https://nvdbapiles-v3.atlas.vegvesen.no/
# Objekt 1000 av 7180
# Objekt 5000 av 7180
# Tidsbruk datanedlasting: 0:01:25.670870
# Segmentering av 97643 datarader med veg og 2 typer fagdata med ialt 61202 datarader
# Segmentering: Behandler vegsegment 1 av 97643 ( 0% ) tidsbruk 0:00:00
# Segmentering: Behandler vegsegment 10 av 97643 ( 0% ) tidsbruk 0:00:00
# Segmentering: Behandler vegsegment 100 av 97643 ( 0% ) tidsbruk 0:00:01
# Segmentering: Behandler vegsegment 500 av 97643 ( 1% ) tidsbruk 0:00:07
# Segmentering: Behandler vegsegment 1000 av 97643 ( 1% ) Estimert ferdig om: 0:23:11 

# Degenert tilfelle (f.eks stedfesting MOT?) veglenkesekvens=603948 kommune=301
#         Vegnett=(0.472888,0.56167774), fagdata=(0.54244942, 0.56167774) 
#         kv11635 s1d1 m787-815 
#         POINT (265316.278 6648583.083) - POINT (265404.801 6648809.232)

# Segmentering: Behandler vegsegment 10000 av 97643 ( 10% ) Estimert ferdig om: 0:21:03 
# Segmentering: Behandler vegsegment 20000 av 97643 ( 20% ) Estimert ferdig om: 0:18:31 
# Segmentering: Behandler vegsegment 30000 av 97643 ( 31% ) Estimert ferdig om: 0:16:06 
# Segmentering: Behandler vegsegment 40000 av 97643 ( 41% ) Estimert ferdig om: 0:13:25 
# Segmentering: Behandler vegsegment 50000 av 97643 ( 51% ) Estimert ferdig om: 0:10:59 
# Segmentering: Behandler vegsegment 60000 av 97643 ( 61% ) Estimert ferdig om: 0:08:40 
# Segmentering: Behandler vegsegment 70000 av 97643 ( 72% ) Estimert ferdig om: 0:06:19 
# Segmentering: Behandler vegsegment 80000 av 97643 ( 82% ) Estimert ferdig om: 0:04:01 
# Segmentering: Behandler vegsegment 90000 av 97643 ( 92% ) Estimert ferdig om: 0:01:44 
# Segmentering ferdig, tidsbruk: 0:22:10
# Tidsbruk segmentering: 0:22:11.486519