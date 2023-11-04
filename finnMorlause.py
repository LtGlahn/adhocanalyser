"""
Finner objekter som ikke har mor, men som burde ha det
"""

import pandas as pd
import geopandas as gpd
from shapely import wkt 
import requests
from datetime import datetime

import STARTHER
import nvdbapiv3 
import nvdbgeotricks 


def lesForeldreRelasjon( relasjoner ):
    """
    Dekoder foreldrerelasjon - hvis den finnes
    """

    resultat = []
    if 'foreldre' in relasjoner: 
        for mor in relasjoner['foreldre']: 
            if 'innhold' in mor: 
                resultat.append( mor['innhold']['navn'])
            else: 
                resultat.append( mor['type']['navn'])

    return ','.join( resultat )

def lesBestillingsregneark( filnavn ): 
    """
    Leser regnerak med navn og kategorisering / gruppering av relevante objekttyper

    Kobler mot datakatalogen, datamasserer littegrann og returnerer pandas dataframe 
    """

    dfObjTyper = pd.read_excel( filnavn )
    url = 'https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekttyper'
    dakat = pd.DataFrame( requests.get( url, params={'inkluder' : 'relasjonstyper'} ).json() )

    dakat['Må ha mor'] = dakat['må_ha_mor'].map( { False : 'Nei', True : 'Ja'} )
    dakat['Mulige foreldre'] = dakat['relasjonstyper'].apply( lesForeldreRelasjon )
    dakat['Kan ha mor'] = dakat['Mulige foreldre'].map( {'' : 'Nei'}).fillna( 'Ja')

    col = ['id', 'navn', 'Må ha mor', 'Kan ha mor', 'Mulige foreldre']
    nyDakat = pd.merge( dfObjTyper, dakat[col], left_on='VT_Navn', right_on='navn', how='left' )
    nyDakat.drop( columns='navn', inplace=True )

    return nyDakat

def morlaus( sokeobjekt ): 
    """
    Løper gjennom alle objektene i et søkeobjekt og returerer to Geodataframes

    Ei Geodataframe med morlause, og ei for dem med mor

    Hvis det er null treff returneres tom liste 
    """


    morlause = []
    harMor = []

    for feat in sokeobjekt: 
        if 'relasjoner' in feat and 'foreldre' in feat['relasjoner']: 
            harMor.append( feat )
        else: 
            morlause.append( feat )

    if len( morlause ) > 0: 
        morlause = pd.DataFrame( nvdbapiv3.nvdbfagdata2records( morlause, geometri=True, vegsegmenter=False ))
        morlause['vegkategori'] = morlause['vegsystemreferanser'].apply( lambda x : x[0] if x else '' )
        morlause['vegnummer'] = morlause['vegsystemreferanser'].apply( lambda x : x.split()[0] if x else '' )


        morlause = gpd.GeoDataFrame( morlause, geometry=morlause['geometri'].apply( wkt.loads ), crs=5973 )
        kolonner = list( morlause.columns )
        morlause['vegkart'] = morlause['nvdbId'].apply( lambda x : 'https://vegkart.atlas.vegvesen.no/#valgt:' + str( x )  + ':' + str( sokeobjekt.objektTypeId)  ) 
        slettes = [ 'stedfesting', 'relasjoner', 'vegsegmenter', 
                   'Geometri, punkt',  'Geometri, linje', 'Geometri, flate', 'geometri', 'Geometri'  ]
        flyttes_frem = [ 'objekttype', 'nvdbId', 'vegkategori', 'vegnummer', 'vegkart',  'vegsystemreferanser']
        flyttes_bak = ['stedfesting_detaljer' ]
        for slett in flyttes_frem+slettes+flyttes_bak: 
            if slett in kolonner: 
                kolonner.remove( slett )

        if 'stedfesting_detaljer' in morlause:
            kolonner.append( 'stedfesting_detaljer' )
        else: 
            kolonner.append( 'stedfesting')

        kolonner = flyttes_frem + kolonner 
        # Spesialhåndtering kontraktsområde
        mittFilter = sok.filter()
        if 'kontraktsomrade' in mittFilter: 
            morlause['Kontraktsområder'] = mittFilter['kontraktsomrade']
            kolonner = [ 'Kontraktsområder'  ] + kolonner 

        morlause = morlause[kolonner].copy()
    
    if len( harMor ) > 0: 
        harMor = pd.DataFrame( nvdbapiv3.nvdbfagdata2records( harMor, geometri=True, vegsegmenter=False ) )
        harMor = gpd.GeoDataFrame( harMor, geometry=harMor['geometri'].apply( wkt.loads), crs=5973 )
    return ( morlause, harMor ) 

if __name__ == '__main__': 
    pd.options.display.float_format = '{:.2f}'.format
    dakat = lesBestillingsregneark( 'NVDB_ObjekterElektro_og_tunnelfase1.xlsx' )

    sammendrag = []

    t0 = datetime.now()

    kontrakter = [  '9304 Bergen 2021-2026', '9107 Gudbrandsdalen 2021-2025', '9506 Vest-Finnmark 2021-2026', '9254 Vestfold og Telemark Øst Elektro 2023-2028', 
                  '9255 Agder og Telemark Vest Elektro 2023-2028', 'E9554 Finnmark 2023-2028' ]

    # Henter tunnelløp for kontrakter slik at vi kan gjøre "nærmeste nabo" - analyse
    tunnel = pd.DataFrame( nvdbapiv3.nvdbFagdata( 67, filter={'kontraktsomrade' : ','.join( kontrakter ) } ).to_records() )
    tunnel.rename( columns={ 'nvdbId' : 'nvdbId Tunnelløp', 'Navn' : 'Navn tunnelløp'}, inplace=True  )
    tunnel = gpd.GeoDataFrame( tunnel, geometry=tunnel['geometri'].apply( wkt.loads ), crs=5973 )

    # Data beholdere
    sammendrag = []
    resultater = { }
    # dakat2 = dakat[ dakat['id'].isin( [212, 458] ) ]
    for ii, objType in dakat.iterrows(): 

        data_utenmor = [ ]
        print( '##########################################################################################')
        print( f"##\n##\n## Henter objekttype {ii+1} av {len( dakat)}: {objType['id']} {objType['VT_Navn']}\n##\n##")
        print( '##########################################################################################')

        for kontrakt in kontrakter:

            print( f"Henter objekttype {objType['id']} {objType['VT_Navn']} for {kontrakt}")

            sok = nvdbapiv3.nvdbFagdata( objType['id'], filter={'kontraktsomrade' : kontrakt})
            utenMor, harMor = morlaus( sok )

            # Finner overlapp med tunnel. Pga denne bugen her: https://www.vegvesen.no/jira/browse/NVDB-7605
            # må jeg laste ned ALLE objekter som overlapper med tunnel og så filtrere mot dem som er på kontraktsområdet

            utenMorItunnel = []
            harMorItunnel  = []
            if len( utenMor ) > 0 or len( harMor ) > 0: 
                tunnelsok = nvdbapiv3.nvdbFagdata( objType['id'], filter={'overlapp' : '67'}) 
                utenMorItunnelNorge, medMorItunnelNorge = morlaus( tunnelsok )

                if len( utenMor) > 0 and len( utenMorItunnelNorge ) > 0: 
                    utenMorItunnel = utenMor[ utenMor['nvdbId'].isin( utenMorItunnelNorge['nvdbId']  )]
                    utenMor['I tunnel'] = 'Utafor tunnel'
                    utenMor['I tunnel'].mask( utenMor['nvdbId'].isin( utenMorItunnelNorge['nvdbId']), 'Overlapper med tunnelløp', inplace=True )
                    kolonner = list( utenMor.columns )
                    kolonner.remove( 'I tunnel')
                    kolonner = ['I tunnel'] + kolonner
                    utenMor = utenMor[kolonner]
                    
                if len( harMor ) > 0 and len( medMorItunnelNorge ) > 0: 
                    harMorItunnel = harMor[ harMor['nvdbId'].isin( medMorItunnelNorge['nvdbId'] )]
                    
            sammendrag.append( { 'Kontraktsområde' : kontrakt, 'id' : objType['id'], 'Antall uten mor' : len( utenMor ), 'Antall med mor' : len( harMor ), 
                                'I tunnel uten mor' : len( utenMorItunnel), 'I tunnel med mor' : len( harMorItunnel )  } )

            print( f"Kontrakt {kontrakt} Hentet { len(utenMor)+len(harMor) } objekter, {len(utenMor)} morlause av type {objType['id']} {objType['VT_Navn']} \t\tTidsbruk{datetime.now()-t0}")
            if len( utenMor) > 0:
                data_utenmor.append( utenMor )
        
        # Legger data uten mor inn i 
        if len( data_utenmor ) > 0: 
            data_utenmor = pd.concat( data_utenmor )
            kolonner = list( data_utenmor.columns )
            data_utenmor = data_utenmor.sjoin_nearest( tunnel[['nvdbId Tunnelløp', 'Navn tunnelløp', 'geometry']], how='left', distance_col='Avstand tunnelløp' )
            kolonner = ['Avstand tunnelløp', 'nvdbId Tunnelløp', 'Navn tunnelløp'] + kolonner 

            resultater[str(objType['id']) + ' ' + nvdbapiv3.esriSikkerTekst( objType['VT_Navn']) ] = data_utenmor[kolonner]
    
    sammendrag = pd.DataFrame( sammendrag )
    sammendrag = pd.merge( dakat[['id', 'VT_Navn', 'Må ha mor', 'Kan ha mor']], sammendrag, on='id' )

    print( f"Lagrer til excel, tidsbruk så langt: {datetime.now()-t0}")
    excelDump = [ sammendrag ]
    excelFaneNavn = [ 'Statistikk' ]
    for fane in resultater.keys(): 
        excelDump.append( resultater[fane] )
        excelFaneNavn.append( fane[0:30] )

    print( f"Lagrer til geopackage, tidsbruk så langt: {datetime.now()-t0}")
    for fane in resultater.keys(): 
        resultater[fane].to_file( 'pilotkontraktar_morlause.gpkg', layer=fane[0:30], driver='GPKG'   )

    nvdbgeotricks.skrivexcel( 'pilotkontraktar_morlause.xlsx', excelDump, sheet_nameListe=excelFaneNavn )

    print( f"Kjøretid totalt: {datetime.now()-t0}")