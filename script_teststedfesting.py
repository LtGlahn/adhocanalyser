"""
Tester stedfestingautomatikk

Ref https://nvdbstedfesting.atlas.vegvesen.no/swagger-ui/index.html#/Stedfesting/localizeFeatures
og https://nvdb.atlas.vegvesen.no/docs/stedfest/API-referanse 

Fokuserer spesielt på retning-problematikk 

curl -X 'POST' \
  'https://nvdbstedfesting.utv.atlas.vegvesen.no/api/v1/stedfest' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "parametere": {
    "maksimalAvstandTilVeg": 10,
    "veger": [
      {
        "kategori": "K",
        "fase": "V",
        "nummer": 4900
      }
    ],
    "typeVeger": [
      "ENKEL_BILVEG"
    ],
    "beregnSideposisjon": false,
    "forankring": {
      "srid": 5973,
      "startWkt": "POINT (270301.2328106925 7042034.742957044)"
    },
    "trafikantgruppe": "K"
  },
  "vegobjekter": [
    {
      "typeId": 95,
      "tempId": "skiltpunkt#1",
      "gyldighetsperiode": {
        "startdato": "2022-06-28",
        "sluttdato": "2022-10-30"
      },
      "geometri": {
        "srid": 5973,
        "wkt": "POINT (270301.2328106925 7042034.742957044)"
      }
    }
  ]
}


"""
import json 
import requests 

import pandas as pd
import geopandas as gpd

import STARTHER
import nvdbapiv3 

if __name__ == '__main__': 

    # Stedfestingeksempel 
    url = 'https://nvdbstedfesting.atlas.vegvesen.no/api/v1/stedfest'
    headers = { 'accept' : 'application/json', 'Content-Type' : 'application/json'}
    data = {  "parametere": {
                "maksimalAvstandTilVeg": 20,
                "veger": [  { "kategori": "P",
                                "fase": "V",
                                # "nummer": 4900
                            }, { "kategori" : "E", "fase" : "V"} ],
                "beregnSideposisjon": True,
                # "forankring": {
                # "srid": 5973,
                # "startWkt": "POINT (270301.2328106925 7042034.742957044)"
                # },
                "trafikantgruppe": "K"
            },
            "vegobjekter": [
                {
                "typeId": 95,
                "tempId": "skiltpunkt#1",
                "gyldighetsperiode": {
                    "startdato": "2023-03-07"
                },
                "geometri": {
                    "srid": 5973,
                    "wkt": "POINT (146122.74682430 7006185.61897353)"
                }
                }
            ]
            }
    
    r = requests.post( url, headers=headers, data=json.dumps( data ) )
