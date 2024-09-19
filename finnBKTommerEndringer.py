"""
Finner avvik mellom bruksklassene for normal- og tømmetransport. 

Egenskapene "Bruksklasse" og "Bruksklasse, vinter" skal jo være identiske for disse to 
objekttypene, men vi har en del datafeil 

Objekttype ID: 
901 = Bruksklasse tømmertransport, uoffisiell 
905 = Bruksklasse normaltransport, uoffisiell 
"""
from datetime import datetime

import pandas as pd
import geopandas as gpd 
from shapely import wkt 


import STARTHER
import nvdbapiv3 
import overlapp
import nvdbgeotricks

def dekodBruksklasser( verdi ): 

    # Bruksklasse 
    if '21699' in verdi: 
        return 'Bk10 - 60 tonn'
    elif '21700' in verdi: 
        return 'Bk10 - 56 tonn'
    elif '18205' in verdi: 
        return 'Bk10 - 50 tonn'
    elif '18206' in verdi: 
        return 'Bk10 - 42 tonn'
    elif '21617' in verdi: 
        return 'BkT8 - 60 tonn'
    elif '18207' in verdi: 
        return 'BkT8 - 50 tonn'
    elif '18208' in verdi: 
        return 'BkT8 - 40 tonn'
    elif '18209' in verdi: 
        return 'Bk8 - 32 tonn'
    elif '18210' in verdi: 
        return 'Bk6 - 28 tonn'
    elif '1821' in verdi: 
        return 'Spesiell begrensning'

    # Bruksklasse vinter
    elif '19637' in verdi: 
        return 'Bk10 - 60 tonn'
    if '21704' in verdi: 
        return 'Bk10 - 56 tonn'
    if '18222' in verdi: 
        return 'Bk10 - 50 tonn'
    if '21701' in verdi: 
        return 'Bk10 - 42 tonn'
    if '21616' in verdi: 
        return 'BkT8 - 60 tonn'
    if '21702' in verdi: 
        return 'BkT8 - 50 tonn'
    if '18223' in verdi: 
        return 'BkT8 - 40 tonn'
    if '18224' in verdi: 
        return 'Bk8 - 32 tonn'
    if '21703' in verdi: 
        return 'Bk6 - 28 tonn'
    else: 
        BK = ''

    return BK 

def oversettSQLverdi2BK( myText ): 
    """
    Oversetter kolonner fra SQL-logg til meningsfylte dataverdier for 901 BK tømmertransport, uoffisiell
    
    Skreddersydd for scriptet https://www.vegvesen.no/jira/browse/NVDB-12811 
    """
    
    # Returnerer tomme dataverdier 
    if not isinstance( myText, str) or len( myText ) < 10:
        return ''
    
    tmp1 = myText.split( ':' )

    egType = tmp1[-2] 
    verdi  = tmp1[-1]
    if '10922' in egType: # Utgår_Maks totalvekt 
        if '18270' in verdi: 
            return '50' 
        elif '18271' in verdi: 
            return '56'
        elif '18272' in verdi: 
            return '60'
        else: 
            raise ValueError( f"Feil dataverdi i SQL data {myText} tolket som egenskap 10922 Utgår_Maks totalvekt  " )

    elif '10898' in egType or '10904' in egType: # Bruksklasse 
        
        tmp2 = verdi.split( '->')
        startVerdi = dekodBruksklasser( tmp2[0])
        sluttVerdi = dekodBruksklasser( tmp2[1])
        return f"{startVerdi} -> {sluttVerdi}"

    else: 
        return ''


def leslogg( filnavn ): 
    """
    Leser script endringslogg ref https://www.vegvesen.no/jira/browse/NVDB-12811 
    
    Format på filen er 
    
    Nasjonal vegdatabank- UXPDBNVDB2_fra_PROD_24Okt23kl09:07          2023-10-31 09.27

    fid=777604042, vid=3: a10922: 18272 -> null, a10898: 18205 -> 21699
    fid=777604043, vid=4: a10922: 18272 -> null, a10898: 18205 -> 21699
    """
    loggdata = pd.read_csv( filnavn, skiprows=2, names=['fid', 'vid', 'col1', 'col2' ], skipfooter=5, engine='python' )
    
    loggdata['nvdbId']                      = loggdata['fid'].apply( lambda x : int( x.split('=')[1] ))
    loggdata['Utgår_Maks totalvekt']        = loggdata['vid'].apply(        oversettSQLverdi2BK )

    nyeData = []

    for ii, row in loggdata.iterrows(): 
        nyRad = { 'nvdbId' : row['nvdbId'], 'Utgår_Maks totalvekt' : row['Utgår_Maks totalvekt']  }

        if isinstance( row['col1'], str ) and  '10898' in row['col1']: # Bruksklasse i kolonne 3 
            nyRad['Endring Bruksklasse']         =    oversettSQLverdi2BK( row['col1']  )
        if isinstance( row['col1'], str ) and'10904' in row['col1']:  # Bruksklasse vinter i kolonne 3 
            nyRad['Endring Bruksklasse Vinter']  = oversettSQLverdi2BK(  row['col1'] )
        elif isinstance( row['col2'], str ) and '10904' in row['col2']: # Bruksklasse vinter i kolonne 4
            nyRad['Endring Bruksklasse Vinter']  = oversettSQLverdi2BK(  row['col2'] )

        nyeData.append( nyRad )

    loggdata2 = pd.DataFrame( nyeData )
    return loggdata2


if __name__ == '__main__': 

    pd.options.display.float_format = '{:.2f}'.format

    bk901 = nvdbapiv3.nvdbFagdata(901 )
    bk905 = nvdbapiv3.nvdbFagdata(905 )

    forb = nvdbapiv3.apiforbindelse()
    forb.login( miljo='prodles')
    # forb.login( miljo='testles')
    # forb.login( miljo='utvles')
    bk901.forbindelse = forb
    bk905.forbindelse = forb


    # Testdatasett med et par av de feila vi fant på https://www.vegvesen.no/jira/browse/NVDB-12683
    # mittFilter = { 'vegsystemreferanse' : '3035 KV10210,3805 KV43348,5025 KV6060,3420 KV2240,3448 KV3378', 'tidspunkt' : '2023-06-03'}
    # bk901.filter( mittFilter )
    # bk905.filter( mittFilter )

    t0 = datetime.now()
    df901 = pd.DataFrame( bk901.to_records())
    df905 = pd.DataFrame( bk905.to_records())
    t1 = datetime.now()
    print( f"Datanedlasting tidsbruk: {t1-t0}")
    df901['geometry'] = df901['geometri'].apply( wkt.loads )
    df905['geometry'] = df905['geometri'].apply( wkt.loads )
    df901 = gpd.GeoDataFrame( df901, geometry='geometry', crs=5973 )
    df905 = gpd.GeoDataFrame( df905, geometry='geometry', crs=5973 )

    if not 'Bruksklasse vinter' in df905.columns:
        df905['Bruksklasse vinter'] = ''

    if not 'Bruksklasse vinter' in df901.columns:
        df901['Bruksklasse vinter'] = ''

    t2 = datetime.now()
    bkOverlapp = overlapp.finnoverlapp( df905, df901)
    print( f"Overlapp tidsbruk: {datetime.now()-t2}")
    bkOverlapp.fillna( '', inplace=True )

    # Spleiser med loggdata fra UTV 
    # loggdata = leslogg( 'removeMaxWeight_utv.log' )
    loggdata = leslogg( 'bk_31okt/removeMaxWeight_0.log' )
    loggdata.fillna( '', inplace=True )
    loggdata.rename( columns={'nvdbId' : 't901_nvdbId'}, inplace=True )
    bkOverlapp = pd.merge( bkOverlapp, loggdata[['t901_nvdbId', 'Utgår_Maks totalvekt', 'Endring Bruksklasse', 'Endring Bruksklasse Vinter']], on='t901_nvdbId', how='left' )

    bkOverlapp.fillna( '', inplace=True)

    # Finner alle mulige datakombinasjoner: 
    kombo = bkOverlapp.groupby( ['Bruksklasse', 't901_Bruksklasse', 
                    'Bruksklasse vinter', 't901_Bruksklasse vinter', 'Utgår_Maks totalvekt', 'Endring Bruksklasse', 'Endring Bruksklasse Vinter']).agg( {'t901_nvdbId' : 'nunique', 
                                                                            'segmentlengde' : 'sum' } ).reset_index()


    # kombo = bkOverlapp.groupby( ['Utgår_Maks totalvekt', 'Endring Bruksklasse', 'Endring Bruksklasse Vinter']).agg( {'t901_nvdbId' : 'nunique', 'segmentlengde' : 'sum' } ).reset_index()
    # kombo.sort_values( by='segmentlengde', ascending=False, inplace=True )
    kombo.sort_values( by=['Utgår_Maks totalvekt', 'segmentlengde'], ascending=False, inplace=True )    

    # kombo = pd.merge( kombo, gyldigRegneark[ gyldig_col + ['kommentarer']], on=gyldig_col, how='left')
    # nvdbgeotricks.skrivexcel( 'kombinasjonerBKnormal_tommer.xlsx', kombo )

    col = [ 'Endring Bruksklasse','Endring Bruksklasse Vinter', 'Utgår_Maks totalvekt',   
            'Bruksklasse', 't901_Bruksklasse', 'Bruksklasse vinter',    
           't901_Bruksklasse vinter', 't901_Tillatt for modulvogntog 1 og 2 med sporingskrav',
           'vref',  
           'nvdbId', 'Maks vogntoglengde',
          'typeVeg', 'kommune',
       'fylke', 'veglenkeType', 'vegkategori', 'fase', 'vegnummer',
        'segmentlengde', 'adskilte_lop',
       'trafikantgruppe', 
       'Merknad', 'Strekningsbeskrivelse', 'Maks totalvekt kjøretøy, skiltet',
        'Maks totalvekt vogntog, skiltet', 
       't901_objekttype', 't901_nvdbId', 
       't901_Maks vogntoglengde', 
       't901_Strekningsbeskrivelse', 't901_Merknad', 
        'veglenkesekvensid', 'startposisjon', 'sluttposisjon', 'geometry' ] 
    
    nvdbgeotricks.skrivexcel( 'BKtommerMedMaksTotalvekt_PROD_ETTERscript.xlsx', [kombo, bkOverlapp[col] ], 
                              sheet_nameListe=['Statistikk', 'Alle objekter'])

    bkOverlapp[col].to_file( 'BKtommerMedMaksTotalvekt_PROD_ETTERscript.gpkg', layer='overlapp901_905', driver='GPKG')