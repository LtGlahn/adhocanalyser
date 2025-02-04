"""
Henter datakatalogen, tilrettelegger for effektiv oversettelse objektTypeId => objektTypeNavn med eksempler  
"""

import requests
headers = { "X-Client" : "Python kode fra tonhan",
 "X-Kontaktperson" : "tony.andre.hansen@vegvesen.no" }

dakatListe = requests.get( 'https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekttyper', headers=headers ).json()
# Oversetter fra liste => dictionary der objekttype ID er nøkkel og objekttypeNavn er verdien 
# Bruker såkalt "list & dictionary comprehension", som er et litt over middels avansert pythontricks  
# https://www.w3schools.com/python/python_lists_comprehension.asp 
# https://www.geeksforgeeks.org/python-dictionary-comprehension/ 
objTyper =  { x['id'] : x['navn'] for x in dakatListe }

# Eksempler på hvordan man bruker denne datastrukturen 
featureType = 938 
print( f"ObjektType {featureType} {objTyper[featureType]}")


# Møter en gjeng med ulike objekter av varierende type, lager oppsummering
oppsummering = {}
for featureType in [ 5, 5, 5, 938, 938, 45 ]: 
    if featureType in oppsummering.keys(): 
        oppsummering[featureType] += 1 
    else: 
        oppsummering[featureType] = 1


print( f"Oppsummering fra kontrakt")
for key, value in oppsummering.items(): 
    print( f"fant {value} objekter av type {key} {objTyper[key]}")

