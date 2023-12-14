"""
Sammenligner bruksklasse tømmertransport på ERF-vegnettet ved to ulike tidspunkt. Bruker segmenteringsrutine

Oppdrag for Stortinget
"""
from datetime import datetime

import pandas as pd
import geopandas as gpd
from shapely import wkt

import STARTHER
import nvdbapiv3
import nvdbgeotricks
import segmentering 


if __name__ == '__main__':
    t0 = datetime.now()

    # Henter vegnett
    # vegnett = pd.DataFrame( nvdbapiv3.nvdbVegnett( filter={'veglenketype' : 
    #                                                         'hoved,konnektering',
    #                                                         'trafikantgruppe' : 'K', 
    #                                                         'vegsystemreferanse' : 'Ev,Rv,Fv'}).to_records() )
    # vegnett = vegnett[ vegnett['adskilte_lop'] != 'Mot']
    # vegnett_col = [ 'veglenkesekvensid', 'startposisjon', 'sluttposisjon',
    #     'type', 'detaljnivå', 'typeVeg', 
    #     'feltoversikt', 'geometri', 'lengde', 'fylke',
    #    'kommune',  'vref',
    #    'vegkategori', 'fase', 'nummer',
    #     'trafikantgruppe', 'adskilte_lop', 'medium', 'geometry' ]
    # Henter (nesten) fersk bruksklasse
    bkNY =  pd.DataFrame(  nvdbapiv3.nvdbFagdata(900, filter={ 'vegsystemreferanse' : 'Ev,Rv,Fv' }).to_records() )

    # Henter eldre bruksklasse
    bkGammal =  pd.DataFrame( nvdbapiv3.nvdbFagdata(900, filter={ 'vegsystemreferanse' : 'Ev,Rv,Fv', 'tidspunkt' : '2022-11-02'  }).to_records())


    # Lager GeodataFrame     
    # vegnett  = gpd.GeoDataFrame( vegnett,  geometry=      vegnett[ 'geometri'].apply( wkt.loads), crs=5973 )
    bkNY     = gpd.GeoDataFrame( bkNY,     geometry=      bkNY[    'geometri'].apply( wkt.loads), crs=5973 )
    bkGammal = gpd.GeoDataFrame( bkGammal, geometry=      bkGammal['geometri'].apply( wkt.loads), crs=5973 )
    
    # Jukser med objekttypeId på bkGammal
    bkGammal['objekttype'] = 9999

    t1 = datetime.now()
    print( f"Tidsbruk datanedlasting: {t1-t0}")


    bkNYcol = ['Bruksklasse',
       'Tillatt for modulvogntog 1 og 2 med sporingskrav',
        'veglenkesekvensid', 'detaljnivå', 'typeVeg',
       'kommune', 'fylke', 'vref', 'veglenkeType', 'vegkategori', 'fase',
       'vegnummer', 'startposisjon', 'sluttposisjon', 'segmentlengde',
       'adskilte_lop', 'trafikantgruppe', 'segmentretning', 'geometry' ]

    byttNavn = {    'Bruksklasse': 'GAMMEL BK',
                    'Tillatt for modulvogntog 1 og 2 med sporingskrav': 'GAMMEL tillat modulvt',
                    'Utgår_Maks totalvekt': 'GAMMEL maks totalvekt'
                    }

    bkGammal.rename(columns=byttNavn, inplace=True )

    bkGammalcol = [ 'GAMMEL BK', 'GAMMEL maks totalvekt',
                   'GAMMEL tillat modulvt', 
                   'veglenkesekvensid', 'vref',  'startposisjon', 'sluttposisjon',
                    'geometry']

    joined = segmentering.segmenter( bkNY[bkNYcol], bkGammal[bkGammalcol] )

    print( f"Tidsbruk segmentering: {datetime.now()-t1}")

    joinedcol = ['vegkategori', 'fylke', 'kommune', 'vref', 
                 'Bruksklasse', 'GAMMEL BK', 'GAMMEL maks totalvekt',
                 'Tillatt for modulvogntog 1 og 2 med sporingskrav',
                'GAMMEL tillat modulvt',
                 'veglenkesekvensid', 'startposisjon', 'sluttposisjon', 
                'geometry']
    
    bk10_60 = joined[ joined['Bruksklasse'] == 'Bk10 - 60 tonn']
    endret = bk10_60[ bk10_60['Bruksklasse'] !=  bk10_60['GAMMEL BK'] ]
    endret2 = endret[ endret['GAMMEL maks totalvekt'] != 60.0 ]

    nvdbgeotricks.skrivexcel( 'bktømmerEndretTil60tonn.xlsx',   [data, data2,   endret2[joinedcol]], 
                             sheet_nameListe=['BKverdi oppjustert Fv', 'BKverdi oppjustert ERF',   'strekninger'] )
    endret2.to_file( 'endretBKverdi.gdb', layer='endret_til_BK10_60', driver = 'OpenFileGDB' )