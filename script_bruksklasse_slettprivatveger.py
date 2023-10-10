from datetime import datetime

import pandas as pd
import geopandas as gpd
from shapely import wkt 

import STARTHER
import nvdbapiv3 
import nvdbgeotricks 
import spesialrapporter

if __name__ == '__main__': 

    t0 = datetime.now()
    forb = nvdbapiv3.apiforbindelse()
    forb.login( miljo='prodles')

    filnavn = 'bruksklasse_multippelStedfesting'

    objektTyper = [900, 901, 902, 903, 904, 905 ] 
    endringListe = []
    for objekttype in objektTyper: 
        print( "Henter objekttype=", objekttype, "Tidsbruk:", datetime.now()-t0)

        endring = {     "lukk": { "vegobjekter": [] }, "datakatalogversjon": "2.32" }

        sok = nvdbapiv3.nvdbFagdata( objekttype )
        sok.forbindelse = forb 
        sok.filter( { 'vegsystemreferanse' : 'Pv', 'kommune' : 301 })
        for objekt in sok: 
            vegkategori = set( [x['vegsystem']['vegkategori'] for x in  objekt['lokasjon']['vegsystemreferanser']  ] )
            if vegkategori == { 'P' } : 
                endring['lukk']['vegobjekter'].append( {
                                                            "lukkedato": datetime.now().isoformat()[0:10],
                                                            "kaskadelukking": "NEI",
                                                            "typeId": objekttype,
                                                            "nvdbId": objekt['id'],
                                                            "versjon": objekt['metadata']['versjon']
                                                        }) 
            else: 
                print( f"Feil vegkategori {vegkategori} for objektID {objekt['id']}")

        endringListe.append( endring )

    print( "Tidsbruk datahenting:", datetime.now()-t0 )

    tidsbruk_totalt = datetime.now()-t0 
