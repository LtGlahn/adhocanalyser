import requests
import getpass
import json

if __name__ == '__main__': 

    authapi = 'https://nvdbauth.atlas.vegvesen.no/api/v1/auth/autentiser'

    innlogging_headers =  { 'X-Client' : 'LtGlahn python' }
    innlogging_body    =  {'brukernavn' : 'jajens', 'brukertype' : 'ANSATT'  }
    innlogging_body['passord'] = getpass.getpass( f"Passord for {innlogging_body['brukernavn']} :>" )
    r_innlogging = requests.post( authapi, headers=innlogging_headers, json=innlogging_body  )
    if r_innlogging.ok: 
        print( "SUKSESS, vi er logget inn")
        id_token = r_innlogging.json()
        # MERK MELLOMROM mellom 'Bearer' og id_token  
        df_headers =  { 'X-Client': 'LtGlahn python',
                        'Authorization' : 'Bearer' + ' ' + id_token['id_token'] }
        
        # Sjekker at vi kan hente ut en kontraktsliste 
        kontraktAPI = 'https://datafangst-api-gateway.atlas.vegvesen.no/api/v2/contracts' 
        kontraktsParam = { 'pageNo' : 0,
                             'pageSize' : 20,
                             'sortBy' : 'lastModifiedDate',
                             'isAscending' : False,
                            # 'search' : ,
                            # 'contractType' : ,
                            # 'roadCategory' : ,
                            # 'status' : ,
                            # 'contractGroupId' : ,
                             'archivedStates' : 'OPEN' }
                             
        r2 = requests.get( kontraktAPI, headers=df_headers, params=kontraktsParam )
        if r2.ok:
            print( "HURRA, vi har hentet kontraktliste fra Datafangst 2.0")
            print( json.dumps( r2.json(), indent=4, ensure_ascii=False))
        else: 
            print( f"Feilmelding http {r2.status_code} {r2.text} ved henting av kontraktliste")
    else: 
        print( f"Innlogging feilet: http {r_innlogging.status_code} {r_innlogging.text}" )
            