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

def df2gdf( myDataFrame ): 
    """
    Konverterer Pandas Dataframe  => GeoDataFrame 
    """
    myDataFrame['geometry'] = myDataFrame['geometri'].apply( wkt.loads ) 
    myGdf = gpd.GeoDataFrame( myDataFrame, geometry='geometry', crs=5973) 
    if 'segmentlengde' in myGdf: 
        myGdf['lengde (km)'] = myGdf['segmentlengde'] / 1000
    elif 'lengde' in myGdf: 
        myGdf['lengde (km)'] = myGdf['lengde'] / 1000
    else:
        raise ValueError( f"Ingen lengde-egenskap i kolonnene: {','.join( list( myGdf.columns ))} ")
    myGdf.fillna( '', inplace=True )
    
    return myGdf

if __name__ == '__main__':

    t0 = datetime.now( )
    mittfilter = { 'vegsystemreferanse' : 'Ev,Rv,Fv,Kv', 'tidspunkt' : '2022-12-31'}

    bk = pd.DataFrame( nvdbapiv3.nvdbFagdata( 900, filter=mittfilter ).to_records())
    bk = df2gdf( spesialrapporter.KOSTRAfiltrering( bk, alledata=True  ))
    
    t1 = datetime.now()
    print( "Tidsbruk nedlasting BK tømmertransport\t", t1-t0 )

    bkmodul = pd.DataFrame( nvdbapiv3.nvdbFagdata( 889, filter=mittfilter ).to_records())
    bkmodul = df2gdf( spesialrapporter.KOSTRAfiltrering( bkmodul, alledata=True ))

    t2 = datetime.now()
    print( "Tidsbruk nedlasting BK Modulvogntog\t", t2-t1)

    veg = pd.DataFrame( nvdbapiv3.nvdbVegnett( filter=dict( {'veglenketype' : 'hoved,konnektering'}, **mittfilter ) ).to_records() )
    veg = df2gdf( spesialrapporter.KOSTRAfiltrering( veg, alledata=True ))

    t3 = datetime.now( )
    print( "Tidsbruk nedlasting vegnett\t", t3-t2)

    # Hack for å finne BK tømmer som IKKE overlapper med BK Modulvogntog
    # Dårlig erstatning for "left join", som ikke er implementert ennå. 
    bk['minindex'] = bk.index

    # Inner join for BK modulvogntog og BK tømmertransport
    joined_cut = overlapp.finnoverlapp( bk, bkmodul, prefixB='bk889_', klippgeometri=True,  klippvegsystemreferanse=True   )

    joined_cut['Grådig overlapp-lengde (km)'] = joined_cut['lengde (km)']
    joined_cut['Overlapp BK tømmer - BK ModulVT (km)'] = joined_cut['segmentlengde'] / 1000 

    bk_ikkemodulvogntog = bk[ ~bk['minindex'].isin( joined_cut['minindex'])]

    t4 = datetime.now( )
    print( "Tidsbruk join", t4-t3)


    bkNormal = pd.DataFrame( nvdbapiv3.nvdbFagdata( 900, filter=mittfilter ).to_records())
    bkNormal = df2gdf( spesialrapporter.KOSTRAfiltrering( bkNormal, alledata=True  ))

    hoydebegr = pd.DataFrame( nvdbapiv3.nvdbFagdata( 900, filter=mittfilter ).to_records())
    hoydebegr = df2gdf( spesialrapporter.KOSTRAfiltrering( hoydebegr, alledata=True  ))

    t5 = datetime.now()
    print( "Tidsbruk nedlasting BK normal", t5-t4)

    nvdbgeotricks.skrivexcel( 'raadata_bruksklasser_ERFK.xlsx', 
                        [ bkNormal,             bk,                   bkmodul,          joined_cut,                       bk_ikkemodulvogntog, hoydebegr  ],
        sheet_nameListe=[ 'BK Normaltransport', 'BK Tømmetransport', 'BK Modulvogntog', 'Overlapp BK Tømmer og ModulVT', 'BK Tømmer IKKE overlapp', 'Høydebegrensning' ]  )

    t6 = datetime.now()
    print( "Tidsbruk lagring til excel", t6-t5)

    gpkgfil = 'raadata_bruksklasser_ERFK.gpkg'
    bkNormal.to_file(            gpkgfil, layer='BK Normaltransport', driver='GPKG')
    bk.to_file(                  gpkgfil, layer='BK Tømmertransport', driver='GPKG')
    bkmodul.to_file(             gpkgfil, layer='BK Modulvogntog',    driver='GPKG')
    joined_cut.to_file(          gpkgfil, layer='Overlapp BK Tømmer og Modulvt', driver='GPKG')
    bk_ikkemodulvogntog.to_file( gpkgfil, layer='Bk Tømmer IKKE overlapp', driver='GPKG')
    hoydebegr.to_file(           gpkgfil, layer='Høydebegrensning', driver='GPKG')
    t7 = datetime.now()
    print( "Tidsbruk lagring til geopackage", t7-t6)


    print( "\nTidsbruk totalt: ", t7-t0)

