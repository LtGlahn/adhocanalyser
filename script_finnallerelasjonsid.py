import json
import requests 

if __name__ == '__main__': 

    url = 'https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekttyper/'

    objTypeId = 79
    relasjoner = []

    # objType = requests.get( url + str( objTypeId) + '.json' ).json()
    dakat = requests.get( url  + '.json', params={'inkluder': 'egenskapstyper'} ).json()
    for objType in dakat: 

        for egenskap in objType['egenskapstyper']: 

            if 'Assosiert' in egenskap['navn']: 

                if 'innhold' in egenskap: 
                
                    relasjoner.append( {'morType' : objType['id'], 'datterType' : egenskap['innhold']['vegobjekttypeid'],  'relasjonId' : egenskap['id'] }  )
                else: 
                    relasjoner.append( {'morType' : objType['id'], 'datterType' : egenskap['vegobjekttypeid'],  'relasjonId' : egenskap['id'] }  )

