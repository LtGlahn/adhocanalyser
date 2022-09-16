import requests
from datetime import datetime

data = []
url = 'https://hjortevilt2-utv.miljodirektoratet.no/api/v0/fallvilt'

page = 0
pageSize = 1000
tempdata = []
data = []
if __name__ == '__main__':

    t0 = datetime.now()

    while len( tempdata ) > 0 or page <= 1: 

        page += 1 
        if page == 1 or page == 10 or page % 100 == 0: 
            print( f"Henter side {page} fra hjorteviltregister-paginering" )
        
        r = requests.get( url, params={ 'pageSize' : pageSize, 'page' : page  })
        if r.ok: 
            tempdata = r.json()
            if isinstance( tempdata, list): 
                if len( tempdata ) > 0: 
                    data.extend( tempdata )
            else: 
                print( f"Fikk annet resultat enn liste: {type( tempdata )}, avbryter ")
                break 

        else: 
            print( f"Feilrespons {r.status_code} fra hjortevilt-API, avbryter")
            break 
                
 
    tidsbruk = datetime.now() - t0 
    print( f"Hentet {len(data)} objekter fra hjorteviltregister, fordelt på {page-1} pagineringssider, tidsbruk: {tidsbruk}"  )
