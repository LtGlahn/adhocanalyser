"""
Tester DF10 problemet med cutoff av feilmeldinger med duplikate relasjoner

Derfor lager vi kode for å generere endringssett som gir digre SKRIV-feilmeldinger 
"""
import json


import STARTHER
import nvdbapiv3 
import skrivnvdb 

if __name__ == '__main__': 

    sok = nvdbapiv3.nvdbFagdata( 95 ) # Henter skiltpunkt og lager endringssett med relasjoner som allerede finnes i NVDB 
    sok.miljo( 'test' )

    feilskriv = skrivnvdb.endringssett_mal()

    count = 0
    while count < 100: 
         
        skilt = sok.nesteForekomst()
        if 'relasjoner' in skilt and 'barn' in skilt['relasjoner']:
            skiltPlateRelasjoner = [ x for x in skilt['relasjoner']['barn']  ]
            if len( skiltPlateRelasjoner ) > 0: 
                count += 1
                print( f"Føyde til objekt {skilt['id']} og datter {skiltPlateRelasjoner[0]['vegobjekter'][0]}")
                nyOppdater = {
                    "gyldighetsperiode": {
                    "startdato": "2025-02-13"
                    },
                    "typeId": 95,
                    "nvdbId": skilt['id'],
                    "versjon": skilt['metadata']['versjon'],
                    "assosiasjoner": [
                        {
                            "typeId": 220004,
                            "nvdbId": [
                            {
                                "verdi": skiltPlateRelasjoner[0]['vegobjekter'][0],
                                "operasjon": "ny"
                            },
                            {
                                "verdi": skiltPlateRelasjoner[0]['vegobjekter'][0],
                                "operasjon": "ny"
                            }
                            ],
                            "operasjon": "oppdater"
                        }
                        ] 
                }
                feilskriv['delvisOppdater']['vegobjekter'].append( nyOppdater )
        
    endr = skrivnvdb.endringssett( data=feilskriv )

    # 
    #  "assosiasjoner": [
        #   {
        #     "typeId": 220004,
        #     "nvdbId": [
        #       {
        #         "verdi": ID,
        #         "operasjon": "ny"
        #       }
        #     ],
        #     "operasjon": "oppdater"
        #   }
        # ] 
        # 
        #   "assosiasjoner": [
        #   {
        #     "nvdbId": [
        #       {
        #         "verdi": 123
        #       }
        #     ],
        #     "typeId": 220710