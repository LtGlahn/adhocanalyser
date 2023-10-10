"""
Finner boundingboks for WMTS-tjeneste
"""
import requests 
import xmltodict
import geojson 
from shapely import geometry
import geopandas as gpd

if __name__ == '__main__': 

    url = 'https://next.pointscene.com/api/v2/wmts/site/eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2NjMxNTMwMzYsImV4cCI6MTk3ODUxMzAzNiwiand0aWQiOiI4NWFhODAwMi02YzBkLTRmNmYtOGYwMi1lMWE4ODBkNDMwMjYiLCJkYXRhIjp7InZlcnNpb24iOjEsInNjb3BlIjoic2l0ZSBEMXEgdmlld2VyIn19.kuN0PWYSmpJQh-7-xXt230p4jYJDeuGEfEx-RLrMg-HVgFEdkwKVgXCeORiA2hPi3cixEd4YhLNGeye_tUQl6KJEi_GrpA-WaCCXkTX1_jQ4O5zDT_Pcoojm2MaLXtWOxfDyYKt7ZnY8H5Jtlf5t0G0oUfwfFz9a_FAESLTqpo_DR3rZy2mBaXBryE5puCIjfA3ewv76OWV0AE9E5PVLqEsOJalEow07RDlEBn8x2MmpcEiw7cOqXUtJmXZSzcLbVDpqvZGXboLf7Pmht--OYVphWFcfC-P7PSUJa04FtqPKLt5fUN_8eX8CHoW6Sdec0r9fqlpg-EzK8xE_cAD0Xjev8w73sEZ44xbZpzsLQw7LXH4ELmhYoKeX9XRAiOJ_xV8zdmdgfroFp25asViZs2csje84-rkui4TrHZsgHsqDHIZi7bNOcPA-b2NOiGama4OlaxLccbDUNtadkhZjjwxDfVXuw_0ucju-JKnfOMXen__hwL4QMvcsOjDhFARlFohf6Fzl1kAycs4l1t9DU5YU3jLAtljSwYeqZMyameEIcvwplj5b8Yo4Pc0lsxGIUI88LyGs_pw3F2HXnePOtJF32s3Vs66e5IwhXJFnaxUiBDBaiF9ShIfAs38i_5yXVlE3tkW1XOG_9v9Vf7yVs-ibT10rWYd85pdJKhzRqpc?service=WMTS&request=GetCapabilities'

    r = requests.get( url )
    if r.ok:

        xmldata = r.text
        data = xmltodict.parse( xmldata )
        kartlagliste = []   
        crsliste = set()     

        for kartlag in data['Capabilities']['Contents']['Layer']: 
            kart  = { 'title' : kartlag['ows:Title'], 'identifier' : kartlag['ows:Identifier'] }
            x_ll = float( kartlag['ows:BoundingBox']['ows:LowerCorner'].split()[0])
            y_ll = float( kartlag['ows:BoundingBox']['ows:LowerCorner'].split()[1])
            x_ur = float( kartlag['ows:BoundingBox']['ows:UpperCorner'].split()[0])
            y_ur = float( kartlag['ows:BoundingBox']['ows:UpperCorner'].split()[1])
            kart['geometry'] = geometry.box( x_ll, y_ll, x_ur, y_ur )
            kartlagliste.append( kart )
            crsliste.add( kartlag['ows:BoundingBox']['@crs'] )

        if len( crsliste ) == 1: 
            crs = int( list( crsliste )[0].split( ':')[1] )
            minekartlag = gpd.GeoDataFrame( kartlagliste, geometry='geometry', crs=crs)
        else: 
            print( f"Må håndtere ulike CRS i getCapabilities-fila {crsliste} ")