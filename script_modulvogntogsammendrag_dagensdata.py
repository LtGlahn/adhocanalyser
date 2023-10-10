"""
Lager KOSTRA-konstistent statistikk for modulvogntog 
"""
from datetime import datetime

import pandas as pd
import geopandas as gpd
from shapely import wkt 

import STARTHER
import nvdbapiv3
import nvdbgeotricks 
import spesialrapporter
import overlapp
import segmentering

if __name__ == '__main__':

    t0 = datetime.now( )
    mittfilter = { 'vegsystemreferanse' : 'Rv', 'tidspunkt' : '2022-12-31'}
    mittfilter = { 'vegsystemreferanse' : 'Ev,Rv,Fv,Kv', 'tidspunkt' : '2022-12-31'}
    mittfilter = { 'vegsystemreferanse' : 'Ev,Rv,Fv,Kv', 'tidspunkt' : '2022-12-31'}

    bktommer = pd.DataFrame( nvdbapiv3.nvdbFagdata( 900, filter=mittfilter ).to_records())
    bktommer = spesialrapporter.KOSTRAfiltrering( bktommer, alledata=True )
    bktommer['geometry'] = bktommer['geometri'].apply( wkt.loads ) 
    bktommer = gpd.GeoDataFrame( bktommer, geometry='geometry', crs=5973) 
    bktommer['Lengde (km)'] = bktommer['segmentlengde'] / 1000
    bktommer.fillna( '', inplace=True )
    bkTommerStat = bktommer.groupby( [ 'fylke', 'vegkategori', 
            'Tillatt for modulvogntog 1 og 2 med sporingskrav', 'Bruksklasse', 
            'Maks vogntoglengde', 'Maks totalvekt']).agg( {'Lengde (km)' : 'sum' } ).reset_index()
    bklengder = bktommer.groupby( ['fylke', 'vegkategori']).agg( {'Lengde (km)': 'sum'})
    bklengder.rename( columns={'engde (km)' : 'BK tømmertransport (km)'}, inplace=True )

    t1 = datetime.now()
    print( "Tidsbruk nedlasting BK tømmertransport\t", t1-t0 )

    bkmodul = pd.DataFrame( nvdbapiv3.nvdbFagdata( 889, filter=mittfilter ).to_records())
    bkmodul = spesialrapporter.KOSTRAfiltrering( bkmodul )
    bkmodul['geometry'] = bkmodul['geometri'].apply( wkt.loads ) 
    bkmodul = gpd.GeoDataFrame( bkmodul, geometry='geometry', crs=5973) 
    bkmodul['Lengde (km)'] = bkmodul['segmentlengde'] / 1000
    bkmodul.fillna( '', inplace=True )    
    bkmodulvogntogstat = bkmodul.groupby( [ 'fylke', 'vegkategori', 
            'Gjelder ikke linksemitrailer']).agg( { 'Lengde (km)' : 'sum' } ).reset_index()
    bkModullengder = bkmodul.groupby( ['fylke', 'vegkategori']).agg( {'Lengde (km)': 'sum'})
    bkModullengder.rename( columns={'Lengde (km)' : 'BK Modulvogntog (km)'}, inplace=True )

    t2 = datetime.now()
    print( "Tidsbruk nedlasting BK Modulvogntog\t", t2-t1)

    bknormal = pd.DataFrame( nvdbapiv3.nvdbFagdata( 904, filter=mittfilter ).to_records())
    bknormal = spesialrapporter.KOSTRAfiltrering( bknormal )
    bknormal['geometry'] = bknormal['geometri'].apply( wkt.loads ) 
    bknormal = gpd.GeoDataFrame( bknormal, geometry='geometry', crs=5973) 
    bknormal['Lengde (km)'] = bknormal['segmentlengde'] / 1000
    bknormal.fillna( '', inplace=True )    

    t2b = datetime.now()
    print( f"Tidsbruk nedlasting BK normaltransport: {t2b-t2} ")

#     bknormalstat = bknormal.groupby( [ 'fylke', 'vegkategori', 
#             'Gjelder ikke linksemitrailer']).agg( { 'Lengde (km)' : 'sum' } ).reset_index()
#     bknormalstat = bknormal.groupby( ['fylke', 'vegkategori']).agg( {'Lengde (km)': 'sum'})
#     bknormalstat.rename( columns={'Lengde (km)' : 'BK Modulvogntog (km)'}, inplace=True )




    veg = pd.DataFrame( nvdbapiv3.nvdbVegnett( filter=dict( {'veglenketype' : 'hoved,konnektering', 'trafikantgruppe' : 'K'}, **mittfilter ) ).to_records() )
    veg = spesialrapporter.KOSTRAfiltrering( veg, alledata=True )
    veg['geometry'] = veg['geometri'].apply( wkt.loads ) 
    veg = gpd.GeoDataFrame( veg, geometry='geometry', crs=5973) 
    veg['Lengde (km)'] = veg['lengde'] / 1000    
    veglengdestat = veg.groupby( ['fylke', 'vegkategori'] ).agg( { 'Lengde (km)' : 'sum' } ).reset_index()
    veglengdestat.rename( columns={'Lengde (km)' : 'Lengde KOSTRA-vegnett (km)'}, inplace=True )
    t3 = datetime.now( )
    print( "Tidsbruk nedlasting vegnett\t", t3-t2b)

    # LEFT join for BK modulvogntog og BK tømmertransport
    joined_cut = overlapp.finnoverlapp( bktommer, bkmodul, prefixB='bk889_', join='left' )
    t4 = datetime.now()
    print(f"Tidsbruk left join BK tømmer - BK modul: {t4-t3} ")
    joinedCol  = [ 'objekttype', 'nvdbId', 'versjon', 'startdato', 'Bruksklasse',
                'Vegliste gjelder alltid',
                'Tillatt for modulvogntog 1 og 2 med sporingskrav',
                'Maks vogntoglengde', 'veglenkesekvensid', 'detaljnivå', 'typeVeg',
                'kommune', 'fylke', 'vref', 'veglenkeType', 'vegkategori', 'fase',
                'vegnummer', 'startposisjon', 'sluttposisjon', 'segmentlengde',
                'adskilte_lop', 'trafikantgruppe', 'geometri', 'Strekningsbeskrivelse',
                'Maks totalvekt', 'Bruksklasse vinter', 'sluttdato', 'Merknad',
                'bk889_objekttype', 'bk889_nvdbId',
                'bk889_versjon', 'bk889_startdato', 'bk889_Strekningsbeskrivelse',
                'bk889_Maks totalvekt', 'bk889_Maks vogntoglengde', 'geometry' ]
    joined_cut = joined_cut[joinedCol].copy()
    col_overlappBK889 = 'Overlapp BK tømmer-BK modul'
    joined_cut[col_overlappBK889] = 'Overlapp BK Tømmertransport - BK Modulvogntog' 
    joined_cut.loc[ joined_cut['bk889_nvdbId'].isnull(), col_overlappBK889 ] = 'Kun data for BK Tømmertransport'

    t5 = datetime.now()
    # joined_cut.to_file( 'testleftjoin2.gpkg', layer='bkmodul', driver='GPKG' )

    t6 = datetime.now()
    print( "Tidsbruk lagring", t6-t5)

    # Dataprep for left join 
    col_bknormal = ['Bruksklasse',  'Maks vogntoglengde',
                    'Strekningsbeskrivelse', 'Bruksklasse vinter', 'Merknad',
                    'veglenkesekvensid', 'vref', 'startposisjon', 'sluttposisjon', 'geometry', 'segmentretning' ]
    bknormal2 = bknormal[col_bknormal].copy()
    bknormal2.rename( columns={ 'Bruksklasse'           : 'BK Normal - Bruksklasse',  
                                'Maks vogntoglengde'    : 'BK Normal - Maks vtlengde',
                                'Strekningsbeskrivelse' : 'BK Normal - Strekningsbeskrivelse', 
                                'Bruksklasse vinter'    : 'BK Normal - Bruksklasse vinter', 
                                'Merknad'               : 'BK Normal - Merknad'  }, inplace=True )
                 
    col_bktommer = [  'Bruksklasse',  'Maks vogntoglengde', 'veglenkesekvensid',
                    'vref',  'startposisjon', 'sluttposisjon', 'Tillatt for modulvogntog 1 og 2 med sporingskrav',
                   'Strekningsbeskrivelse', 'Maks totalvekt', 'Bruksklasse vinter',
                    'Merknad', 'sluttdato', 'geometry', 'segmentretning' ]
    bktommer2 = bktommer[col_bktommer].copy()
    bktommer2.rename( columns={ 'Bruksklasse'                                       : 'BK Tømmer - Bruksklasse',  
                                'Maks vogntoglengde'                                : 'BK Tømmer - Maks vtlengde',
                                'Tillatt for modulvogntog 1 og 2 med sporingskrav'  : 'BK Tømmer - Tillatt for modulvt 1,2',
                                'Strekningsbeskrivelse'                             : 'BK Tømmer - Strekningsbeskrivelse', 
                                'Maks totalvekt'                                    : 'BK Tømmer - Maks totalvekt', 
                                'Bruksklasse vinter'                                : 'BK Tømmer - Bruksklasse vinter',
                                'Merknad'                                           : 'BK Tømmer - Merknad' }, inplace=True    )

    col_bkmodul = [ 'Strekningsbeskrivelse', 'Maks totalvekt', 'Maks vogntoglengde', 'veglenkesekvensid', 
                   'vref', 'startposisjon', 'sluttposisjon',  'Gjelder ikke linksemitrailer',
                    'Vinterstengt for 60 tonn', 'Merknad', 'geometry', 'segmentretning' ]
    bkmodul2 = bkmodul[col_bkmodul].copy()
    bkmodul2.rename( columns={ 'Strekningsbeskrivelse'          : 'BK Modulvt - Strekningsbeskrivelse',
                               'Maks totalvekt'                 : 'BK Modulvt - Maks totalvekt', 
                               'Maks vogntoglengde'             : 'BK Modulvt - Maks vogntoglengde', 
                               'Gjelder ikke linksemitrailer'   : 'BK Modulvt - Gjelder ikke linksemitrailer',
                               'Vinterstengt for 60 tonn'       : 'BK Modulvt - Vinterstengt for 60 tonn', 
                               'Merknad'                        : 'BK Modulvt - Merknad'}, inplace=True )

    t7=datetime.now()

    veg2 = veg[ ~veg['typeVeg'].isin( [  'Bilferje', 'Gågate', 'Gang- og sykkelveg', 'Trapp', 'Gatetun', 'Sykkelveg', 'Gangveg']  )]
    segmentert = segmentering.segmenter( veg2, [bknormal2, bktommer2, bkmodul2]  )
    print( f"Tidsbruk segmentering: {datetime.now()-t7 } ")
    t7b = datetime.now()

    # joined_cut.loc[ joined_cut['bk889_nvdbId'].isnull(), col_overlappBK889 ] = 'Kun data for BK Tømmertransport'
    # segmentert.loc[ (segmentert['Bruksklasse'].isnull()) & (segmentert['BK Modulvt - Strekningsbeskrivelse'].isnull()) ]
    segmentert['Overlapp'] = 'Ingen fagdata overlapper, kun vegnett'
    segmentert.loc[ (~segmentert['BK Normal - Bruksklasse'].isnull())  & 
                    (~segmentert['BK Tømmer - Bruksklasse'].isnull())  & 
                    (~segmentert['BK Modulvt - Strekningsbeskrivelse'].isnull()), 'Overlapp' ] = 'Overlapp Normal, tømmer og modulvogntog'

    segmentert.loc[ (~segmentert['BK Normal - Bruksklasse'].isnull())  & 
                    ( segmentert['BK Tømmer - Bruksklasse'].isnull())  & 
                    ( segmentert['BK Modulvt - Strekningsbeskrivelse'].isnull()), 'Overlapp' ] = 'Kun BK Normaltransport'

    segmentert.loc[ ( segmentert['BK Normal - Bruksklasse'].isnull())  & 
                    (~segmentert['BK Tømmer - Bruksklasse'].isnull())  & 
                    ( segmentert['BK Modulvt - Strekningsbeskrivelse'].isnull()), 'Overlapp' ] = 'Kun BK Tømmertransport'

    segmentert.loc[ ( segmentert['BK Normal - Bruksklasse'].isnull())  & 
                    ( segmentert['BK Tømmer - Bruksklasse'].isnull())  & 
                    (~segmentert['BK Modulvt - Strekningsbeskrivelse'].isnull()), 'Overlapp' ] = 'Kun BK ModulVT'

    segmentert.loc[ (~segmentert['BK Normal - Bruksklasse'].isnull())  & 
                    (~segmentert['BK Tømmer - Bruksklasse'].isnull())  & 
                    ( segmentert['BK Modulvt - Strekningsbeskrivelse'].isnull()), 'Overlapp' ] = 'Overlapp Normal og tømmer'


    segmentert.loc[ (~segmentert['BK Normal - Bruksklasse'].isnull())  & 
                    ( segmentert['BK Tømmer - Bruksklasse'].isnull())  & 
                    (~segmentert['BK Modulvt - Strekningsbeskrivelse'].isnull()), 'Overlapp' ] = 'Overlapp Normal og ModulVT'

    segmentert.loc[ ( segmentert['BK Normal - Bruksklasse'].isnull())  & 
                    (~segmentert['BK Tømmer - Bruksklasse'].isnull())  & 
                    (~segmentert['BK Modulvt - Strekningsbeskrivelse'].isnull()), 'Overlapp' ] = 'Overlapp KUN Tømmer og ModulVT'

    segmentert['Lengde (km)'] = segmentert['geometry'].apply( lambda x : x.length / 1000 )
    segmentert['vegkategori'] = segmentert['vref'].apply( lambda x : x[0] )
    segmentert['vegnummer'] = segmentert['vref'].apply( lambda x : x.split()[0] )    


    t8 = datetime.now()
    print( f"Tidsbruk datamassasje: {t8-t7b} ")

    t9 = datetime.now()
    segmentert.to_file( 'dagensBKmodul.gpkg', layer='BK Modul, Normal og Tømmer',  driver='GPKG' )
    print( "Lagringstid", datetime.now()-t9 )

    print( "\nTidsbruk totalt: ", t9-t0)
