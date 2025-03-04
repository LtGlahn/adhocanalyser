"""
FLYT-sak https://svvflytprod.service-now.com/now/cwf/agent/record/x_stve_svv_case_0_nvdb_case/9ab68c19873f5e505de2c95e8bbb35c5

Bytte mor på en gjeng belysningspukt. Trøbbelet er at LES presenterer den gamle mora, selv om det er frakoblet i NVDB 
"""
import STARTHER
import skrivnvdb 

if __name__ == '__main__': 
    nyMor =  [ 907581415,  907581416,  907581417,  907581418,  907581419,  907581420, 907581421, 907581422, 907581423,
             907581424, 907581425, 907581426, 907581427, 907581428, 907581429, 907581430, 907581431, 907581432, 907581433, 907581434,
             907581435, 907581436, 907581437, 907581438, 907581439, 907581440, 907581441, 907581442, 907581443, 907581444, 907581445,
             1014131086, 1014131088 ]
    

    print( f"{len(nyMor)} belysningspunkt skal ha ny mor ")

    relasjon_mal = { "typeId": 220026,
                        "nvdbId": [{
                                        "verdi": "xxx",
                                        "operasjon": "ny"
                                    }]
    }

    belStrekning =  {
                        "gyldighetsperiode": {
                            "startdato": "2025-02-22"
                        },
                        "typeId": 86,
                        "nvdbId": 1022245455,
                        "versjon": 2,
                        "assosiasjoner": [{ "typeId": 220026, 
                                          "nvdbId" : [ ],
                                        "operasjon": "oppdater" }]
                    }
                        
    for lyspunkt in nyMor: 
        belStrekning['assosiasjoner'][0]['nvdbId'].append( { "verdi":  lyspunkt, "operasjon": "ny" } )

    skrivemal = skrivnvdb.endringssett_mal()
    skrivemal['delvisOppdater']['vegobjekter'].append( belStrekning )


