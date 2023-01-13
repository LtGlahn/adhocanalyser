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

if __name__ == '__main__':

    t0 = datetime.now( )
    mittfilter = { 'vegsystemreferanse' : 'Fv', 'tidspunkt' : '2022-12-31'}

    bk = pd.DataFrame( nvdbapiv3.nvdbFagdata( 900, filter=mittfilter ).to_records())
    bk = spesialrapporter.KOSTRAfiltrering( bk )
    bk['geometry'] = bk['geometri'].apply( wkt.loads ) 
    bk = gpd.GeoDataFrame( bk, geometry='geometry', crs=5973) 
    bk['lengde (km)'] = bk['segmentlengde'] / 1000
    bk.fillna( '', inplace=True )
    bkTommerStat = bk.groupby( [ 'fylke', 'vegkategori', 
            'Tillatt for modulvogntog 1 og 2 med sporingskrav', 'Bruksklasse', 
            'Maks vogntoglengde', 'Maks totalvekt']).agg( {'lengde (km)' : 'sum' } ).reset_index()
    bklengder = bk.groupby( ['fylke', 'vegkategori']).agg( {'lengde (km)': 'sum'})
    bklengder.rename( columns={'lengde (km)' : 'BK tømmertransport (km)'}, inplace=True )

    t1 = datetime.now()
    print( "Tidsbruk nedlasting BK tømmertransport\t", t1-t0 )

    bkmodul = pd.DataFrame( nvdbapiv3.nvdbFagdata( 889, filter=mittfilter ).to_records())
    bkmodul = spesialrapporter.KOSTRAfiltrering( bkmodul )
    bkmodul['geometry'] = bkmodul['geometri'].apply( wkt.loads ) 
    bkmodul = gpd.GeoDataFrame( bkmodul, geometry='geometry', crs=5973) 
    bkmodul['lengde (km)'] = bkmodul['segmentlengde'] / 1000
    bkmodul.fillna( '', inplace=True )    
    bkmodulvogntogstat = bkmodul.groupby( [ 'fylke', 'vegkategori', 
            'Gjelder ikke linksemitrailer']).agg( { 'lengde (km)' : 'sum' } ).reset_index()
    bkModullengder = bkmodul.groupby( ['fylke', 'vegkategori']).agg( {'lengde (km)': 'sum'})
    bkModullengder.rename( columns={'lengde (km)' : 'BK Modulvogntog (km)'}, inplace=True )

    t2 = datetime.now()
    print( "Tidsbruk nedlasting BK Modulvogntog\t", t2-t1)

    veg = pd.DataFrame( nvdbapiv3.nvdbVegnett( filter=dict( {'veglenketype' : 'hoved'}, **mittfilter ) ).to_records() )
    veg = spesialrapporter.KOSTRAfiltrering( veg)
    veg['geometry'] = veg['geometri'].apply( wkt.loads ) 
    veg = gpd.GeoDataFrame( veg, geometry='geometry', crs=5973) 
    veg['lengde (km)'] = veg['lengde'] / 1000    
    veglengdestat = veg.groupby( ['fylke', 'vegkategori'] ).agg( { 'lengde (km)' : 'sum' } ).reset_index()
    veglengdestat.rename( columns={'lengde (km)' : 'Lengde KOSTRA-vegnett (km)'}, inplace=True )
    t3 = datetime.now( )
    print( "Tidsbruk nedlasting vegnett\t", t3-t2)

    # Hack for å finne BK tømmer som IKKE overlapper med BK Modulvogntog
    # Dårlig erstatning for "left join", som ikke er implementert ennå. 
    bk['minindex'] = bk.index

    # Inner join for BK modulvogntog og BK tømmertransport
    joined_cut = nvdbgeotricks.finnoverlapp( bk, bkmodul, prefixB='bk889_', klippgeometri=True,  klippvegsystemreferanse=True   )

    joined_stat = joined_cut.groupby( [ 'fylke', 'vegkategori', 'bk889_Gjelder ikke linksemitrailer', 
            'Tillatt for modulvogntog 1 og 2 med sporingskrav', 'Bruksklasse', 
            'Maks vogntoglengde', 'Maks totalvekt']).agg( {'lengde (km)' : 'sum' } ).reset_index()    

    joined_cut['Grådig overlapp-lengde (km)'] = joined_cut['lengde (km)']
    joined_cut['Overlapp BK tømmer - BK ModulVT (km)'] = joined_cut['segmentlengde'] / 1000 
    joinedLengder = joined_cut.groupby( ['fylke', 'vegkategori']).agg( {'Overlapp BK tømmer - BK ModulVT (km)' : 'sum', 'Grådig overlapp-lengde (km)' : 'sum'})
    # joinedLengder.rename( columns={'lengde (km)' : 'Overlapp BK Tømmer - BK ModulVT (km)'}, inplace=True )

    bk_ikkemodulvogntog = bk[ ~bk['minindex'].isin( joined_cut['minindex'])]
    ikkeModulStat = bk_ikkemodulvogntog.groupby( [ 'fylke', 'vegkategori', 
            'Tillatt for modulvogntog 1 og 2 med sporingskrav', 'Bruksklasse', 
            'Maks vogntoglengde', 'Maks totalvekt']).agg( {'lengde (km)' : 'sum' } ).reset_index()

    ikkeModulLengde = bk_ikkemodulvogntog.groupby(['fylke', 'vegkategori'] ).agg( { 'lengde (km)' : 'sum' })
    ikkeModulLengde.rename( columns={ 'lengde (km)' :  'IKKE med i grådig join (km)' }, inplace=True )

    t4 = datetime.now( )
    print( "Tidsbruk join", t4-t3)

    # Setter sammen statistikk for lengder 
    tmp = veglengdestat.merge( bklengder, on=['fylke', 'vegkategori'])
    tmp = tmp.merge( bkModullengder, on=['fylke', 'vegkategori'])
    tmp = tmp.merge( joinedLengder, on=['fylke', 'vegkategori'])
    lengdeStat = tmp.merge( ikkeModulLengde, on=['fylke', 'vegkategori'])

    # Lagrer... 

    nvdbgeotricks.skrivexcel( 'lengder_BKtømmer_BKModulvt_Fylkesveg.xlsx',
                        [ lengdeStat,    bkTommerStat,                 bkmodulvogntogstat,      joined_stat,                         ikkeModulStat],
        sheet_nameListe=[ 'Lengde vegnett', 'Lengde BK Tømmertransport', 'Lengde BK Modulvogntog',  'Overlapp BK Tømmer og ModulVT',   'BK Tømmer IKKE overlapp'] )

    nvdbgeotricks.skrivexcel( 'raadata_forModulvogntog_Fylkesveg.xlsx', 
                        [ bk,                   bkmodul,          joined_cut,                       bk_ikkemodulvogntog  ],
        sheet_nameListe=[ 'BK Tømmetransport', 'BK Modulvogntog', 'Overlapp BK Tømmer og ModulVT', 'BK Tømmer IKKE overlapp' ]  )


    t5 = datetime.now()
    print( "Tidsbruk lagring", t5-t4)
    print( "\nTidsbruk totalt: ", t5-t0)