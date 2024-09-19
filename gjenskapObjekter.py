"""
Rutiner for å gjenopprette historiske NVDB-objekter som nye objekter, med samme relasjoner, men med stedfesting på nytt vegnett. 
"""
from datetime import datetime
from copy import deepcopy
import requests
import json 

import pandas as pd 
import geopandas as gpd 
from shapely import wkt, wkb
from shapely.geometry import LineString, MultiLineString

import STARTHER
import nvdbapiv3 
import skrivnvdb

def hentObjekter( nvdbIdListe, forb=None ): 
    """
    Henter siste (historiske) objektversjon av liste av objekter. Gir advarsel dersom objektene har relasjon til barn som ikke 
     er med i med i listen over ID'er.  
     (Dette er eksperimentelt, må nesten prøve det ut for å finne ut hvordan vi håndterer hjørnetilfellene når vi møter dem
     Uavklart hva som er rett hvis f.eks barna fremdeles er gyldige objekt i NVDB)

    Returnerer dictionary med NVDB ID som nøkkel 

    ARGUMENTS
        nvdbIdListe: Liste eller annen itererbar struktur med NVDB ID 

    KEYWORDS
        forb: None eller en instans av nvdbapiv3.apiforbindelse() (brukes f.eks for å hente sensitive data, eller 
                   for å lese fra andre miljøer enn PROD)

    RETURNS
        dictionary, 
    """


    if not forb: 
        forb = nvdbapiv3.apiforbindelse()

    data = {}
    count = 0
    for minId in nvdbIdListe: 
        count += 1 
        if count == 1 or count == 10 or count == 50 or count % 100 == 0: 
            print( f"Henter nvdb objekt {count} av {len(nvdbIdListe)}")
        r = forb.les( '/vegobjekt', params={'id': int(minId)})
        if not r.ok: 
            print( f"Klarte ikke hente NVDB objekt {minId}: HTTP {r.status_code} {r.text[0:500]} ...")
        else: 
            data[int(minId)] = r.json()

    return data 

def gjenskapFraCsv( filnavn, nvdbIDkolonne, sluttDatoKolonne, sluttdato, forb=None, **kwargs): 
    """
    Leser CSV fil og henter objekter fra NVDB api LES

    ARGUMENTS
        filnavn: text, filnavn og plassering til CSV-fil

        nvdbIDkolonne: text, Navn på den kolonnen som inneholder NVDB ID i CSV-fila

        sluttDatoKolonne: tekst, Navn på den kolonnen som inneholder sluttdato 

        sluttdato: Den sluttdatoen vi er interessert i

    KEYWORDS: 
        forb: None eller en instans av nvdbapiv3.apiforbindelse() (brukes f.eks for å hente sensitive data, eller 
                   for å lese fra andre miljøer enn PROD)
    
        Alle andre nøkkelord blir videresendt til pandas.read_csv(), les dokukumentasjon 
        https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html 

    RETURNS
        Datastruktur hentet fra funksjonen hentObjekter(nvdbIdListe)
    """

    mydf = pd.read_csv( filnavn, **kwargs)
    # Fjerner hvitrom fra kolonnenavnene, vi har selvsagt et grisete opplegg med formattering og mellomrom 
    # på kolonnene. GRRRR 
    byttnavn = {}
    for col in list( mydf.columns ): 
        byttnavn[col] = col.strip( )
    mydf.rename( columns=byttnavn, inplace=True )
    assert nvdbIDkolonne in mydf.columns, f"Finner ikke angitt kolonnenavn {nvdbIDkolonne} i CSV-fil {filnavn}"
    assert sluttDatoKolonne in mydf.columns, f"Finner ikke angitt kolonnenavn {sluttDatoKolonne} i CSV-fil {filnavn}"

    # Tar bare med dem som ble lukket på angitt sluttdato 
    mydf = mydf[ mydf[sluttDatoKolonne] == sluttdato ]

    # Fjerner duplikater (dette er pga multippel stedfesting)
    mydf.drop_duplicates( subset=nvdbIDkolonne, inplace=True )

    data = hentObjekter( mydf[nvdbIDkolonne].to_list(), forb=forb )
    return data 


def forenkleGeometri( myWkt:str, godkjentLengde:int ):
    """
    Forenkler (tynner) geometri så WKT-streng blir kortere enn godkjentLengde tegn

    ARGUMENTS
        myWkt : text, geometri formulert som WKT (well known tekst) 

        godkjentLengde:int Heltall, maks antall tegn i WKT-streng 
    """
    geom = wkt.loads( myWkt )
    my2Dgeom = wkb.loads( wkb.dumps( geom , output_dimension=2  ))
    # print( f"Antall tegn: {len(myWkt)} 2D: {len(my2Dgeom.wkt)}, maks tillatt: {godkjentLengde}" )
    toleranserAlternativ = [0.1, 0.5, 1, 2, 5, 10, 20, 50, 100] 
    while len( my2Dgeom.wkt ) > godkjentLengde and len(toleranserAlternativ) > 0: 
        toleranse = min( toleranserAlternativ )
        toleranserAlternativ.remove( toleranse)
        # junk = deepcopy( my2Dgeom ) # For debugging
        my2Dgeom = my2Dgeom.simplify( toleranse )
        # print( f"Forenkler geometri, fra {len(junk.wkt)} tegn / {len(junk.coords)} punkt => {len(my2Dgeom.wkt)} tegn / {len(my2Dgeom.coords)} punkt toleranse={toleranse}" )
        
    # print( f"Lengde WKT-streng: {len(my2Dgeom.wkt)}")
    return my2Dgeom.wkt


def stedfest( nvdbData, startdato=None, datakatalogversjon=None, maks_antall=10 ): 
    """
    Stedfester datastrukturen fra hentObjekter 

    Returnerer to dictionaries: 
     - endringssett som kan sendes til SKRV, med relasjoner og stedfesting - OBS! Kun for de 
       objektene der stedfestingen var vellykket 

     - Den orginale datastrukturen nvdbData påført informasjon om stedfestingen var vellykket eller ei

    EKSPERIMENTELT 

    ARGUMENTS
        nvdbData - dictionary returnert fra funksjon hentObjekter(nvdbId) hver nøkkel = nvdbId 

    KEYWORDS
        startdato - None, eventuelt ISO-dato for start gyldighetsperiode hvis du ønsker noe annet enn dagens dato

    RETURNS 
        dictionary, endringssett som kan sendes til SKRIV
    """

    myDict = deepcopy( nvdbData )

    if not startdato: 
        startdato = datetime.today().strftime('%Y-%m-%d')    

    if not datakatalogversjon: 
        # r = requests.get( 'https://nvdbapiles-v3.atlas.vegvesen.no/status', headers={ 'accept' : 'application/json' })
        # status = r.json()
        # datakatalogversjon = status['datagrunnlag']['datakatalog']['versjon'] 
        datakatalogversjon = '2.33'
        print( f"Datakatalogversjon hardkodet til {datakatalogversjon} den 17.9.2023")

    # Må først lage relasjonstre med datter-> mor kobling, fordi det er hva stedfesting-endepunktet akseptere 
    mor = {}
    # Lagrer også mor -> datter kobling (for å kunne samle relasjonstrær)
    datterRelasjoner = {}

    for objId in myDict.keys(): 
        temp = skrivnvdb.fagdata2skrivemal( myDict[objId], operasjon='registrer', ignorerRelasjoner=False, effektDato=startdato, 
                                         datakatalogversjon=datakatalogversjon ) 
        etObj = temp['registrer']['vegobjekter'][0]
        etObj['tempId'] = str( objId )
        if 'assosiasjoner' in etObj: 
            assosiasjoner = etObj.pop( 'assosiasjoner' )
            etObj['assosiasjoner'] = []
            for enRelasjon in assosiasjoner:
                assert enRelasjon['nvdbId']['verdi'] in myDict, f"ObjektId {objId} har relasjon til {enRelasjon['nvdbId']['verdi']}, som ikke inngår i datasettet"
                etObj['assosiasjoner'].append( { 'typeId' : enRelasjon['typeId'],
                                                 'tempId' : str( enRelasjon['nvdbId']['verdi'] ) 
                                                 })
        myDict[objId]['endringssett'] = etObj

        # Hekter på datter-mor relasjon
        # TODO: Sjekke mot datakatalog-definisjon av denne relasjonen, og kun bry deg om dem som har 
        #       regelverk som berører stedfesting (innafor_mor = True )
        if 'assosiasjoner' in etObj: 
            for datter in etObj['assosiasjoner']: 
                assert datter['tempId'] not in mor, f"Multiple mødre for NVDB objekt {datter['tempId'] }"
                mor[ datter['tempId'] ] = myDict[objId]['id']
                if not objId in datterRelasjoner: 
                    datterRelasjoner[ objId ] = []
                datterRelasjoner[ objId ].append( datter['tempId'] )

    # Da er vi klare til å komponere data som sendes til stedfesting-endepunktet
    stedObjekter = {}
    count = 0
    for objId in myDict.keys():
        count += 1  
        geom = deepcopy(myDict[objId]['geometri'] )
        # geom['wkt'] = forenkleGeometri( geom['wkt'], 4999)
        # geom['wkt'] = forenkleGeometri( geom['wkt'], 9000 ) 
        geom.pop( 'egengeometri', None )
        etSted = {  'typeId' : myDict[objId]['metadata']['type']['id'], 
                   "tempId": str( objId ),
                    "gyldighetsperiode": {
                        "startdato": startdato,
                    },
                    "geometri" : geom
        }
        print( f"Tekstlengde WKT {etSted['tempId']:12} rad{count:4} {len(etSted['geometri']['wkt']):5}")
        if objId in mor: 
            # Føyer på info om mor-relasjon 
            etSted['mor'] =  { 
                "typeId" : myDict[ mor[ objId ] ]['metadata']['type']['id'], 
                "tempId" : str( mor[ objId ] )
             }

        stedObjekter[ objId ] = etSted 

    antallTotalt = len( stedObjekter )
    # Plukker ut relasjonstrær for seg. Lager liste med lister, der hver underliste
    # inneholder et relasjonstre som skal sendes samlet til stedfesting-API
    stedfestingObjektListe = [] 


    debug_alleObjektID = set()
 
    # TODO  NB! Denne logikken må utvides til å håndtere mer enn ett nivå i relasjonstreet
    while len( datterRelasjoner ) > 0:
        # morId har datter-relasjon til datterId  
        morId = list( datterRelasjoner.keys())[0]

        # Legger mor-objektet i samlingen
        tempListe = [ stedObjekter.pop( morId ) ]
        debug_alleObjektID.add( int( morId ) )
        
        # Itererer over alle datter-relasjoner som denne mora har
        alleBarn = datterRelasjoner.pop( morId )
        # alleBarn = datterRelasjoner[ morId ] 
        for ettBarn in alleBarn: 
            tempListe.append( stedObjekter.pop( int( ettBarn ) ) )
            debug_alleObjektID.add( int( ettBarn ))
            assert int(ettBarn) not in datterRelasjoner, f"Sorry, vi har ikke implementert kompette relasjonstrær ennå (datter {ettBarn} har relasjon til {datterRelasjoner[ettBarn]})"
        
        # Sjekker at vi ikke har mer enn ett nivå med relasjoner (bestemor -> morId -> ettBarn -> barnebarn)
        assert morId not in mor, f"Sorry, vi har ikke implementert komplette relasjonstrær ennå (mor-Id {morId} er datter av {mor[morId]})"

        stedfestingObjektListe.append( tempListe )

    antall_relasjonstre = len( stedfestingObjektListe )
    antall_i_relasjonstre = antallTotalt - len( stedObjekter )

    # Iterer over resten av objektene (som da ikke har relasjoner)
    count = 0 
    # maks_antall = PARAMETERSTYRT # Antall objekt av gangen i samme liste
    tempListe = []
    for objId in stedObjekter.keys(): 
        count += 1 
        tempListe.append( stedObjekter[objId] )
        debug_alleObjektID.add( int( objId ))
        if len( tempListe ) >= maks_antall: 
            stedfestingObjektListe.append( tempListe )
            tempListe = []
            count = 0

    if len( tempListe ) > 0: 
        stedfestingObjektListe.append( tempListe )

    # Nå er vi klare til å sende inn til stedfest-endepunktet
    parametere = {
                "maksimalAvstandTilVeg": 20,
                "beregnSideposisjon": False,
                "beregnKjørefelt": False,
                "konnekteringslenker": False,
                "beholdTrafikantgruppe": False
            }

    
    feil = {}
    advarsler = { }
    notabene = { }


    count = 0
    countObjekt = 0
    debug_returnerteObjektId = set( )
    for liste in stedfestingObjektListe: 
        sted = { "parametere" : parametere,
                "vegobjekter": liste 
                }
        count += 1
        countObjekt += len( liste )
        print( f"Iterasjon {count} av {len(stedfestingObjektListe)}, {len(liste)} objekter, totalt {countObjekt}")

        url = 'https://nvdbstedfesting.test.atlas.vegvesen.no/api/v1/stedfest'
        headers={ 'accept' : 'application/json', 'Content-Type' : 'application/json' }
        r = requests.post( url, headers=headers, data=json.dumps( sted )  )
        if r.ok: 
            returdata = r.json()
            for feiltype in ['feil', 'advarsel', 'notabener']: 
                if feiltype in returdata and len( returdata[feiltype]) > 0: 
                    print( f"Generisk feilmelding gruppenivå: {feiltype.upper()} {returdata[feiltype]}")

            for etObj in returdata['vegobjekter']: 

                debug_returnerteObjektId.add( int( etObj['tempId']))
                    
                for feiltype in ['feil', 'advarsel', 'notabener']: 
                    if feiltype in etObj and len( etObj[feiltype]) > 0: 
                        
                        if feiltype == 'feil': 
                            feil[int( etObj['tempId'])] = etObj[feiltype]
                        if feiltype == 'advarsel': 
                            advarsler[int( etObj['tempId'])] = etObj[feiltype]
                        if feiltype == 'notabene': 
                            notabene[int( etObj['tempId'])] = etObj[feiltype]

                if 'feil' in etObj and len( etObj['feil']) > 0: 
                    print( f"Stedfesting FEIL: {etObj['tempId']} {etObj['feil']}")
                    myDict[int( etObj['tempId'] ) ]['STEDFESTING'] = 'FEILER'
                    myDict[int( etObj['tempId'] ) ]['feilkode']    = etObj['feil'][0]['kode']
                    myDict[int( etObj['tempId'] ) ]['feilmelding']    = etObj['feil'][0]['melding']

                else: 

                    if len( etObj['stedfesting']['linje']) > 0: 
                        print( f"Håndter stedfesting linje {etObj['tempId']}")
                        linjeSted = []
                        for eiLinje in etObj['stedfesting']['linje']: 
                            nyLinje = { 'veglenkesekvensNvdbId' : eiLinje['nvdbId'], 
                                          'fra'                 : eiLinje['fra'], 
                                          'til'                 : eiLinje['til'] }
                            # Tar kun med sideposisjon og kjørefelt hvis de har dataverdier 
                            if 'sideposisjon' in eiLinje and eiLinje['sideposisjon']: 
                                nystedfesting['sideposisjon'] = eiLinje['sideposisjon']
                            if 'kjørefelt' in eiLinje and len( eiLinje['kjørefelt'] ) > 0: 
                                nystedfesting['kjørefelt'] = eiLinje['kjørefelt']

                            linjeSted.append( nyLinje )

                        myDict[int( etObj['tempId'] ) ]['endringssett']['stedfesting'] = { 'linje' : linjeSted  }
                        myDict[int( etObj['tempId'] ) ]['STEDFESTING'] = 'OK linje'
                        tempGeom = MultiLineString( [ wkt.loads(  x['geometri']['wkt']) for x in etObj['stedfesting']['linje'] ] ) 
                        myDict[int( etObj['tempId'] ) ]['Ny stedfestingWKT'] = tempGeom.wkt
                        myDict[int( etObj['tempId'] ) ]['Ny VREF'] =  ','.join( 
                                [ x['vegsystemreferanse']['kortform'] for x in  etObj['stedfesting']['linje'] if 'vegsystemreferanse' in x ] )
                    elif len( etObj['stedfesting']['punkt']) > 0: 
                        print( f"Håndter stedfesting punkt {etObj['tempId']}")
                        punkt = etObj['stedfesting']['punkt'][0]
                        nystedfesting = { 'veglenkesekvensNvdbId' : punkt['nvdbId'], 
                                          'posisjon'              : punkt['posisjon'] }
                        
                        # Tar kun med sideposisjon og kjørefelt hvis de har dataverdier 
                        if 'sideposisjon' in punkt and punkt['sideposisjon']: 
                            nystedfesting['sideposisjon'] = punkt['sideposisjon']
                        if 'kjørefelt' in punkt and len( punkt['kjørefelt'] ) > 0: 
                            nystedfesting['kjørefelt'] = punkt['kjørefelt']

                        myDict[int( etObj['tempId'] ) ]['endringssett']['stedfesting'] = { 'punkt' :  [ nystedfesting ]}
                        myDict[int( etObj['tempId'] ) ]['STEDFESTING'] = 'OK punkt'
                        myDict[int( etObj['tempId'] ) ]['Ny stedfestingWKT'] = etObj['stedfesting']['punkt'][0]['geometri']['wkt']
                        myDict[int( etObj['tempId'] ) ]['Ny VREF'] = etObj['stedfesting']['punkt'][0]['vegsystemreferanse']['kortform']
                    else: 
                        print( f"Hverken punkt eller linje, FEILSITUASJON??")
                        myDict[int( etObj['tempId'] ) ]['STEDFESTING'] = 'FEILER'

                    if 'notabener' in etObj and len( etObj['notabener']) > 0: 
                        print( f"Stedfesting NOTABENE: {etObj['tempId']} {etObj['notabener']}")
                        myDict[int( etObj['tempId'] ) ]['STEDFESTING']      += ' NotaBene'
                        myDict[int( etObj['tempId'] ) ]['notabenekode']      = etObj['notabener'][0]['kode']
                        myDict[int( etObj['tempId'] ) ]['notabeneMelding']   = etObj['notabener'][0]['melding']

                    if 'advarsler' in etObj and len( etObj['advarsler']) > 0: 
                        print( f"Stedfesting ADVARSEL: {etObj['tempId']} {etObj['advarsler']}")
                        myDict[int( etObj['tempId'] ) ]['STEDFESTING']      += ' advarsler'
                        myDict[int( etObj['tempId'] ) ]['advarselkode']      = etObj['advarsler'][0]['kode']
                        myDict[int( etObj['tempId'] ) ]['advarselMelding']   = etObj['advarsler'][0]['melding']

                if not 'STEDFESTING' in myDict[ int( etObj['tempId'] )]: 
                    raise ValueError( f"Mangler STEDFESTING - tagg for objekt {etObj['tempId']}")

        else: 
            print( f"Stedfesting FEILET TOTALT {len(liste)} objekter: http {r.status_code} {r.text[0:500]}")
            # Må tagge alle elementer i den listen
            for feilObj in liste: 
                myDict[ int( feilObj['tempId']) ]['STEDFESTING'] = f"FEILER TOTALT http {r.status_code}"

            # Lagrer JSON-fil
            print( f"\n\n==============================================")
            print( f"\n\n\n=> Lagrer 500-feil til JSON fil stedfesting500feil.json\n\n")
            with open( 'stedfesting500feil.json', 'w') as f:
                json.dump( sted, f )

    # Validering
    endringsett = []
    for minId in myDict.keys():
        endringsett.append( myDict[minId]['endringssett'] )
    stedfestingStatus = []
    for minId in myDict.keys():
        stedfestingStatus.append( myDict[minId]['STEDFESTING' ] )

    # from IPython import embed; embed()
 

    return myDict
    # if r.ok: 
    #     return r
    # else: 
    #     raise ValueError( f"Feilmelding stedfesting HTTP {r.status_code} {r.text[0:500]}"  )
    

def lagreGPKG( myDict:dict, filnavn:str, layerPrefix='' ): 
    """
    Lager datastrukturen fra stedfest som to kartlag i gpkg-fil 
    """

    mydf = pd.DataFrame( [ myDict[x] for x in myDict.keys() ]  )

    mydf['objektTypeId']   = mydf['metadata'].apply( lambda x : x['type']['id'])
    mydf['objektTypeNavn'] = mydf['metadata'].apply( lambda x : x['type']['navn'])
    mydf['Ny VREF'].fillna( '', inplace=True )
    mydf['Nytt vegnummer'] = mydf['Ny VREF'].apply( lambda x : x.split()[0] if len(x) > 0 else '' )
    # Fjerner liste med egenskapsverdier 
    mydf.drop( columns=['egenskaper'], inplace=True )

    egengeom = mydf.copy()
    egengeom['geometry'] = egengeom['geometri'].apply( lambda x: wkt.loads(x['wkt'] ) )
    egengeom = gpd.GeoDataFrame( egengeom, geometry='geometry', crs=5973 )
    egengeom.to_file( filnavn, layer= layerPrefix+'egengeometri', driver='GPKG')

    sted = mydf[ ~mydf['Ny stedfestingWKT'].isnull() ].copy()
    sted['geometry'] = sted['Ny stedfestingWKT'].apply( wkt.loads )
    sted = gpd.GeoDataFrame( sted, geometry='geometry', crs=5973 )
    sted.to_file( filnavn, layer=layerPrefix+'Ny stedfesting', driver='GPKG')




if __name__ == '__main__': 
    gamledata = gjenskapFraCsv( 'Gjenåpning_Ånestad-csv.csv', 'FID', 'EDATE', 20200730, sep=';', encoding='latin1' )
    myDict = stedfest( gamledata, startdato='2020-07-30', maks_antall=2 )
