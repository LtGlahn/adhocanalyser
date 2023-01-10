"""
Svarer på spørsmålet: _Hvor kan vi kjøre 24m langt modulvogntog (såkalt tømmer-modulvogntog), men ikke vanlig (25.25m) modulvogntog?

Dette finner vi ved å finne overlapp og differanser mellom objekttypene _889 Bruksklasse, modulvogntog_ og _900 Bruksklasse, tømmertransport_ 
der egenskapsverdiene på _BK tømmer_ tillater modulvogntog. 
(Mer presist egenskapene _Tillatt for modulvogntog type 1 og 2 med sporingskrav == Ja_ og _Maks tillatt vogntoglengde == 24m_)

"""

from datetime import datetime 
from shapely import wkt 
import pandas as pd
import geopandas as gpd

import STARTHER
import nvdbapiv3
import nvdbgeotricks


if __name__ == '__main__': 
    t0 = datetime.now()
    mittfilter = { 'vegsystemreferanse' : 'Ev,Rv,Fv,Kv' }

    sok = nvdbapiv3.nvdbFagdata(900)
    sok.filter( mittfilter ) 
    bk = pd.DataFrame( sok.to_records() )
    bk = bk[ bk['veglenkeType'] == 'HOVED' ]
    bk = bk[ bk['trafikantgruppe'] == 'K' ].copy()
    # bk = bk[ bk['adskilte_lop'] != 'Mot' ].copy()
    bk['lengde (km)'] = bk['segmentlengde'] / 1000

    # tillattTommer = bk.groupby( ['vegkategori', 
    #         'Tillatt for modulvogntog 1 og 2 med sporingskrav', 'Bruksklasse', 
    #         'Maks vogntoglengde', 'Maks totalvekt']).agg( {'lengde (km)' : 'sum' } ).reset_index()

    bk['geometry'] = bk['geometri'].apply( wkt.loads ) 
    bk = gpd.GeoDataFrame( bk, geometry='geometry', crs=5973) 

    sok = nvdbapiv3.nvdbFagdata( 889)
    sok.filter( mittfilter ) 
    bkmodul = pd.DataFrame( sok.to_records() )
    bkmodul = bkmodul[ bkmodul['veglenkeType'] == 'HOVED' ]
    bkmodul = bkmodul[ bkmodul['trafikantgruppe'] == 'K' ]
    # bkmodul = bkmodul[ bkmodul['adskilte_lop'] != 'Mot' ].copy()
    # bkmodul['lengde (km)'] = bkmodul['segmentlengde'] / 1000
    bkmodul['Gjelder ikke linksemitrailer'].fillna( '', inplace=True )    
    bkmodul['geometry'] = bkmodul['geometri'].apply( wkt.loads ) 
    bkmodul = gpd.GeoDataFrame( bkmodul, geometry='geometry', crs=5973) 

    # modulvogntoglengde = bkmodul.groupby( ['vegkategori', 
    #         'Gjelder ikke linksemitrailer']).agg( { 'lengde (km)' : 'sum' } ).reset_index()


    bk['minindex'] = bk.index

    t1 = datetime.now()
    print( f"Nedlastingstid {t1-t0} ")
    joined =     nvdbgeotricks.finnoverlapp( bk, bkmodul, prefixB='bk889_', klippgeometri=False, klippvegsystemreferanse=False   )
    joined_cut = nvdbgeotricks.finnoverlapp( bk, bkmodul, prefixB='bk889_', klippgeometri=True,  klippvegsystemreferanse=True   )
    t2 = datetime.now()
    print( f"Tidsbruk finnoverlapp X 2: {t2-t1} ")

    bk_ikkemodulvogntog = bk[  ~bk['minindex'].isin( joined['minindex'] ) ]
    
    # nvdbgeotricks.skrivexcel( 'modulvogntogOskar.xlsx', [ veglengde, modulvogntoglengde, tillattTommer], 
    #                     sheet_nameListe=['Lengde vegnett', 'BK modulvogntog', 'BK tømmertransport']) 


    # Gode navn på lag: 
    # 
    

    # gpkgfil = 'moduleksperiment.gpkg'
    # bk_ikkemodulvogntog.to_file(    gpkgfil, layer='Ikke 25.25m modulvogntog', driver='GPKG') 
    # joined.to_file(                 gpkgfil, layer='Både 24 og 25.25m modulvogntog - Ukorrigert', driver='GPKG') 
    # joined_cut.to_file(             gpkgfil, layer='Både 24 og 25.25m modulvogntog - korrigert', driver='GPKG') 


    # nvdbgeotricks.skrivexcel( 'Modulvogntog ikke 25.25m.xlsx', bk_ikkemodulvogntog )
