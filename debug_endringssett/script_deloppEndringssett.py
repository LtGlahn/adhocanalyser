"""
Deler opp endringssett i mindre biter 
"""
import pandas as pd
import json 
from copy import deepcopy

import STARTHER
import nvdbapiv3 
import skrivnvdb 

def sammendrag( myList ): 
    """
    Lager sammendrag av hvilke objekttyper og ID'er som finnes i vegobjekt
    """

    resultat = []
    for org in myList: 
        feat = { 'typeId' : org['typeId']}
        if 'nvdbId' in org: 
            feat['nvdbId'] = org['nvdbId']
        elif 'tempId' in org: 
            feat['tempId'] = org['tempId']
        else: 
            raise ValueError( f"Ingen tempId eller NVDB id i objekt")
        
        resultat.append( feat )

    return pd.DataFrame( resultat )


def finnAssosiasjoner( myList ): 
    """
    Returnerer dataframe med forenklet oversikt over vegobjekter som har relasjon 
    til andre vegobjekt 
    """
    temp = [ x for x in myList if 'assosiasjoner' in x ]
    if len( temp ) == 0: 
        return temp

    resultat = []

    for org in temp: 
        feat = {}
        feat['typeId'] = org['typeId']
        if 'nvdbId' in org: 
            feat['nvdbId'] = org['nvdbId']
        elif 'tempId' in org: 
            feat['tempId'] = org['tempId']
        else: 
            raise ValueError( f"Ingen tempId eller NVDB id i objekt")
    
        for relasjon in org['assosiasjoner']: 
            if 'nvdbId' in relasjon: 
                for nvdbObj in relasjon['nvdbId']: 
                    nytt = deepcopy( feat )
                    nytt['relasjonstype'] = relasjon['typeId']
                    nytt['nvdbDatter'] = nvdbObj['verdi'] 
                    resultat.append( nytt )

                for tempObj in relasjon['tempId']: 
                    nytt = deepcopy( feat )
                    nytt['relasjonstype'] = relasjon['typeId']
                    nytt['tempDatter'] = tempObj['verdi'] 
                    resultat.append( nytt )

    return pd.DataFrame( resultat )


if __name__ == '__main__': 

    with open( 'endringssett_2ecbe574-04a1-4608-8227-2886aaf3a6b3_modifisert.json') as f: 
        orginal = json.load( f )

    registrer      = sammendrag( orginal['registrer']['vegobjekter']      )
    lukk           = sammendrag( orginal['lukk']['vegobjekter']          )
    delvisOppdater = sammendrag( orginal['delvisOppdater']['vegobjekter'])
    registrer_relasjon = finnAssosiasjoner( orginal['registrer']['vegobjekter'] )
    oppdater_relasjon  = finnAssosiasjoner( orginal['delvisOppdater']['vegobjekter'] )
    nyeNVDBbarn = registrer_relasjon[ ~registrer_relasjon['nvdbDatter'].isnull() ].copy()
    nyeNVDBbarn['nvdbDatter'] = nyeNVDBbarn['nvdbDatter'].astype( int )

    oppdatertNvdbBarn = oppdater_relasjon[ ~oppdater_relasjon['nvdbDatter'].isnull() ].copy()
    oppdatertNvdbBarn['nvdbDatter'] = oppdatertNvdbBarn['nvdbDatter'].astype( int )

    # Er det NVDB ID  i LUKK - delen av endringssettet som også finnes i DelvisOppdater? 

    # Er det NVDB ID i lukk - delen som finnes i de nye relasjonene? 

    # Paste fra det som er kjørt interaktivt i shell
    # nyeBarn['relasjonstype'].value_counts()
    # nyeBarn[ ~nyeBarn['nvdbDatter'].isnull()]
    # nyeNVDBbarn = registrer_relasjon[ ~registrer_relasjon['nvdbDatter'].isnull() ]
    # lukk[ lukk['nvdbId'].isin( nyeNVDBbarn['nvdbDatter'] ) ]
    # lukk[ lukk['nvdbId'].isin( oppdatertNvdbBarn['nvdbDatter'] ) ]
    # lukk[ lukk['nvdbId'].isin( delvisOppdater['nvdbId'] ) ]
    # som fikk meg til å konkludere: INGEN LUKK - objekter er referert til i de andre endringsettene

    ### ------------------
    # 
    # Del opp endringssett i LUKK og resten 

    temp = deepcopy( orginal )
    temp.pop( 'id')
    temp.pop( 'status')
    nyLukk = deepcopy( temp )
    nyLukk.pop( 'registrer')
    nyLukk.pop( 'delvisOppdater')
    nyRegistrerOppdater = deepcopy( temp )
    nyRegistrerOppdater.pop( 'lukk' )

    forb = nvdbapiv3.apiforbindelse( )
    forb.login( miljo='prodskriv')

    SKRIV_nylukk = skrivnvdb.endringssett( nyLukk)
    SKRIV_nylukk.forbindelse = forb 
    # https://nvdbapiskriv.atlas.vegvesen.no/kontrollpanel/#/jobs/view/c9c9aa4d-492c-461b-88e5-f2ba14f3c901 
    # Venter på vegnettslås https://nvdbapiskriv.atlas.vegvesen.no/kontrollpanel/#/locks/view/24762263
    # fordi det er et kommentar-objekt i følgeoppdateringene (og kommentarobjektet er låst)

    SKRIV_nyReg = skrivnvdb.endringssett( nyRegistrerOppdater )
    SKRIV_nyReg.forbindelse = forb 
    # AVVIST - valideringsfeil! 
    # https://nvdbapiskriv.atlas.vegvesen.no/kontrollpanel/#/jobs/view/d0dde7d2-2eeb-4da0-aa2a-d54c00e9c3f0
    # 914312036:2	delvisOppdater	  Feil	MER ENN ETT MOROBJEKT	Objektet er datterobjekt i en hierarkisk sammenheng 
    # (komposisjon eller aggregering) som bare tillater ett morobjekt, men det har flere. Morobjektversjoner: 
    # VEGOBJEKTTYPE=79; ID=914312037; VERSJON=1; STARTDATO=2019-01-08; SLUTTDATO=null og 
    # VEGOBJEKTTYPE=79; ID=1cd56b2e-6204-492f-8ad0-383e9b343734; VERSJON=1; STARTDATO=2024-09-27; SLUTTDATO=null
    # 
    # Tipper vi har TO 79-objekt med relasjon til 914312036
    # Niks - men eksisterende NVDB objekt 79:914312037 er mor-objekt til 83:914312036
    # Samtidig som ny feature 
    # Optimal LØSNING: 
    #   - Endrer LUKK-endringssett slik at KASKADELUKK=NEI for objekt 79:914312037
    #       83:914312036 
    #   - Vente til dagen etter
    #   - sende REGISTRER-endringssettet på ny
    # 
    # Nest beste løsning 
    #   - LUKK-endringssettet går igjennom
    #   - Opprette stikkrenna 914312036 på ny ved å laste opp SOSI fil 
    #   - Endre REGISTRER-relasjon for id 1cd56b2e-6204-492f-8ad0-383e9b343734 -> den nye stikkrenna 


    # Sjekker data i LUKK-datasettet litt mer grundig: 
    # leseforb = nvdbapiv3.apiforbindelse()
    # nvdbdata = []
    # for lukkobj in orginal['lukk']['vegobjekter']: 
    #     r = leseforb.les( '/vegobjekter/' + str( lukkobj['typeId'] ) + '/' + str( lukkobj['nvdbId'] ), params={'inkluder' : 'alle' } )
    #     if r.ok: 
    #         nvdbdata.append( r.json())
    #     else: 
    #         print( f"Feil med henting av NVDB objekt {lukkobj['typeId']}:{lukkobj['nvdbId']}")
