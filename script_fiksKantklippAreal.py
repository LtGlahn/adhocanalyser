"""
Vi har noen driftskontrakter der objekttypen "Kantklippareal" har upresise verdier for "Geometri, flate". 
Dataverdien i egenskapen "Areal" blir dermed upresis. Fylkeskommunen 
ønsker å overskrive denne verdiene med areal regnet ut fra klippebredde * utstrekning langs vegnett 
"""
import pandas as pd
import geopandas as gpd
from shapely import wkt
import pickle

import STARTHER
import nvdbapiv3 
import skrivnvdb 
import overlapp 
import nvdbgeotricks

def fiksKantklippAreal( mittFilter:dict, miljo='PRODLES' ): 
    
    """
    Leser objekttypen kantklippAreal og regner ut areal basert på bredde X utstrekning langs vegnett

    Returnerer DataFrame 

    HACK: Leser inn liste med NVDB ID som skal oppdateres, dvs dem som feilet 15.11 
    def lesKantklippListe( minNvdbIDListe ): 
    """

    sok = nvdbapiv3.nvdbFagdata( 301, filter=mittFilter )
    if miljo.upper() != 'PRODLES': 
        sok.forbindelse.velgmiljo( miljo )
        print( f"Henter data fra {miljo}")

    # # HACK 
    # sok = []
    # forb = nvdbapiv3.apiforbindelse( miljo='prodles')
    # for minId in minNvdbIDListe: 
    #     etObj = forb.les( '/vegobjekt', params={'id' : minId })
    #     sok.append( etObj.json() )

    myList = []
    for feat in sok: 

        nyFeat = { 'nvdbId' : feat['id'] }
        meta = feat['metadata']
        meta.pop( 'type', None )
        nyFeat.update( meta )
        vref =  [x['kortform'] for x in feat['lokasjon']['vegsystemreferanser'] ] 
        if len( vref ) == 0: 
            pass 
        elif len( vref ) == 1: 
            nyFeat['vegnr'] = vref[0].split()[0]
            nyFeat['vegkategori'] = nyFeat['vegnr'][0]
            nyFeat['vegsystemreferanser'] = vref[0]
        elif len( vref ) > 1: 
            vref.sort()

            nyFeat['vegnr']         = ','.join( list( set( [ x.split()[0] for x in vref ]  ))  )
            nyFeat['vegkategori']   = ','.join( list( set( [ x.split()[0][0] for x in vref ]  ))  )

            for ix, junk in enumerate( vref):
                if ix == 0:
                    tempVref = vref[0]
                if ix < len(vref)-1:
                    print( vref[ix], vref[ix+1] )
                    tempVref = overlapp.vegsystemreferanseoverlapp( tempVref, vref[ix+1] )
            if tempVref != '':
                nyFeat['vegsystemreferanser'] = tempVref 
            else: 
                nyFeat['vegsystemreferanser'] = ','.join( vref )

        egenskaper = nvdbapiv3.egenskaper2records( feat['egenskaper'] )
        nyFeat.update( egenskaper )
        nyFeat['lengde langs veg'] = feat['lokasjon']['lengde']
        geom = wkt.loads( feat['geometri']['wkt'] ) 
        nyFeat['geometrisk areal'] = geom.area

        # Ny areal-utregning 
        if 'Klippebredde, faktisk' in nyFeat: 
            nyFeat['NYTT areal' ] = nyFeat['lengde langs veg'] * nyFeat['Klippebredde, faktisk']
        
        nyFeat['geometry'] = geom 
        nyFeat['vegkart lenke'] = 'https://vegkart.atlas.vegvesen.no/#valgt:' + str( feat['id'] ) + ':301'
        # https://vegkart.atlas.vegvesen.no/#valgt:1011014355:301

        myList.append( nyFeat )
    
    myDf = pd.DataFrame( myList )
    myDf['Areal differanse'] = myDf['Areal'] - myDf['NYTT areal']

    # col = ['nvdbId', 'vegsystemreferanser', 'lengde langs veg', 'Klippebredde, faktisk', 
    #        'geometrisk areal', 'Areal',  'NYTT areal', 'Areal differanse']
    return myDf 


def lagEndringsSett( myDf ): 
    """
    Konstruerer endringssett til SKRIV ut av resultatene fra fiksKantklippAreal

    Returnerer liste med endringssett 
    """

    # Lager liste med alle objekter som skal endres
    myList = []


    pass


def korrigerEgenskap( row ): 
    """
    Lager vegobjekter til DelvisKorreksjon 
    """
    vegobjekt = {
            "validering": {
            "lestFraNvdb": "2023-11-16T22:29:14"
            },
            "typeId": 301,
            "nvdbId": row['nvdbId'],
            "versjon": row['versjon'],
            "egenskaper": [
            {
                "typeId": 11312, # Areal 
                "verdi": [
                    round( row['NYTT areal'] )
                ],
                "operasjon": "oppdater"
            }
            ]
        }
    return vegobjekt 

def lagKorreksjonEndringsett( myList:list ):
    """
    Lager komplett endringssett ut fra liste med vegobjekt som skal endres
    """

    endring = {
                    "delvisKorriger": {
                        "vegobjekter":  myList 
                    },
                    "datakatalogversjon": "2.34"
                }

    return endring 


def delOppEndringssett( endringsListe:list, maksAntall=500 ):
    """
    Lager liste med komplette endringssett, delt opp i passe store (maksAntall) deler 
    """ 

    assert isinstance( maksAntall, int), f"Parameter maksAntall må være heltall større enn 0"
    assert maksAntall > 0, f"Parameter maksAntall må være heltall større enn 0"

    count = 0
    endringSett = []
    while count < len( endringsListe): 
        endringSett.append( lagKorreksjonEndringsett( endringsListe[ count : count + maksAntall ]  ))
        count += maksAntall

    return endringSett

def listeMedSKRIV( endringsListe:list, forb ): 
    """
    Registrerer endringssett til APISKRIV og starter skriving. forb=pålogget nvdbapiv3.apiforbindelse objekt 
    """

    returListe = []
    for ii, minEndring in enumerate( endringsListe ) :
        skrivObj = skrivnvdb.endringssett( minEndring )
        skrivObj.forbindelse = forb 
        skrivObj.registrer()
        if skrivObj.status == 'registrert': 
            print( f"Starter skriving på endringsett {ii} av {len(endringsListe)} \n\t{skrivObj.minlenke}")
            skrivObj.startskriving()

        else: 
            print( f"Registrering av endringsett {ii} av {len(endringsListe)} FEILER"  )

        returListe.append( skrivObj )
    return returListe

def sjekkFremdrift( endringListe ): 
    """
    Sjekker fremdrift på alle endringssett i en liste
    """
    for ii, skrivObj in enumerate( endringListe): 
        fremdrift =   skrivObj.sjekkfremdrift()
        print( f"Endringsett {ii} av {len(endringListe)}: {fremdrift}   {skrivObj.minlenke}")

def sjekkSkrivefeil( endringsSett , forb ): 
    endringsSett.forbindelse = forb 
    skrivstatus = endringsSett.sjekkstatus( returjson=True )

    for ff in skrivstatus['resultat']['vegobjekter']: 
        if ff['feil']: 
            print( f"{ff['nvdbId']} {ff['feil']}")

    return skrivstatus




if __name__ == '__main__':
    kontrakter = ','.join( ['4607 Sunnfjord sør 2023', # 4607 = flere muligheter
                  '4608 Sogn 2022-2027',
                  '4609 Sunnfjord Nord 2024-2029', 
                  '4610 Nordfjord 2023-2028' ] )
    mittFilter = { 'kontraktsomrade' : kontrakter, 'egenskap' : '9136!=null'}
        # egenskap=(9136!=null)&
        # kontraktsomrade=4607 Sunnfjord sør 2023,4608 Sogn 2022-2027,4609 Sunnfjord Nord 2024-2029,4610 Nordfjord 2023-2028

    with open( 'kantklippareal_sendpaany.pickle', 'rb' ) as f:
        nvdbID_sendpaany = pickle.load( f )


    # myDf = fiksKantklippAreal( mittFilter, miljo='PRODLES')
    # myDf.sort_values( by='vegsystemreferanser', inplace=True )
    myDfTEST = fiksKantklippAreal( mittFilter, miljo='prodles')
    myDfTEST.sort_values( by='vegsystemreferanser', inplace=True )

    col = ['nvdbId', 'versjon', 'startdato', 'sist_modifisert', 'vegnr',
       'vegkategori', 'vegsystemreferanser', 'Kantklipp, anbefalt intervall',
        'Klippebredde, kvalitet', 
         'Tilleggsinformasjon',
       'Vedlikeholdsansvarlig', 'Eier','geometrisk areal', 
       'Areal',  'Klippebredde, faktisk', 'lengde langs veg', 'NYTT areal',
       'Prosjektreferanse', 'Areal differanse', 'geometry', 'vegkart lenke' ]

    # nvdbgeotricks.skrivexcel( 'kantklipparealfiks_forFK.xlsx', myDf[col] )
    # myGdf = gpd.GeoDataFrame( myDf, geometry='geometry', crs=5973 )
    # myGdf.to_file( 'kantklipparealfiks_forFK.gpkg', layer='kantklippareal', driver='GPKG' )
    
    # endringListe = []
    # for ii, row in myDfTEST.iterrows(): 
    #     endringListe.append( korrigerEgenskap( row ))

    ## Prøver mer dataFrame - måte å gjøre det på: 
    myDfTEST['korreksjon'] = myDfTEST.apply( korrigerEgenskap, axis=1 )
    endringsListe = myDfTEST['korreksjon'].to_list()

    endringer = delOppEndringssett( endringsListe )