"""
Demo og konseptutvikling opptegning av relasjonstre. 
"""

from shapely import wkt, buffer, centroid, force_2d
from shapely.geometry import LineString, GeometryCollection
from shapely.ops import nearest_points

import STARTHER
import nvdbapiv3 

def byggVisningsTre( relasjonstre, kortesteLinje=False ): 

    morGeom = relasjonstre['geometriliste'][0]
    visningGeom = [ morGeom ]
    countRings = 0
    for barnGeom in relasjonstre['geometriliste'][1:]:
        if morGeom.geom_type == 'Point' and barnGeom.geom_type == 'Point' and morGeom.distance( barnGeom ) < 0.5: 
            countRings += 1
            visningGeom.append( buffer( barnGeom, 1*countRings ) )
        else: 
            if kortesteLinje: 
                visningGeom.append( LineString( nearest_points( barnGeom, morGeom)))
                visningGeom.append( barnGeom  )

            else: 
                visningGeom.append( LineString([ centroid( morGeom ), centroid( barnGeom )] ) )
                visningGeom.append( barnGeom  )


    return GeometryCollection( visningGeom )


def byggRelasjonstre( nvdbObj, relasjonstre={}): 

    # Sjekker først at vi er gyldige vegobjekter med geometri osv. Hvis ikke returnerer vi
    if isinstance( nvdbObj, int): 
        return relasjonstre 
    if 'geometri' in nvdbObj and 'id' in nvdbObj:
        pass
    else: 
        return relasjonstre



    if not relasjonstre: # Første iterasjon: Morobjekt
        relasjonstre['morId'] = nvdbObj['id']
        relasjonstre['geometriliste'] = [ force_2d( wkt.loads( nvdbObj['geometri']['wkt'] ))  ]
    else: 
        relasjonstre['geometriliste'].append( force_2d( wkt.loads( nvdbObj['geometri']['wkt'] )) )

    if 'relasjoner' in nvdbObj and 'barn' in nvdbObj['relasjoner']: 
        for enRelasjonstype in nvdbObj['relasjoner']['barn']: 
            print( f"Relasjonstype {enRelasjonstype['type']}")
            for etBarn in enRelasjonstype['vegobjekter']:
                print( f"Henter barn-relasjon {etBarn['id']}")
                relasjonstre = byggRelasjonstre( etBarn, relasjonstre=relasjonstre )

    return relasjonstre 

if __name__ == '__main__': 

    forb = nvdbapiv3.apiforbindelse()
    # morObj = forb.les( '/vegobjekt', params={'id' : 579137713, 'dybde' : 3} ).json() # Skiltpunkt 
    morObj = forb.les( '/vegobjekt', params={'id' : 674319527, 'dybde' : 3} ).json()  # Belysningsstrekning
    relasjonstre = byggRelasjonstre( morObj )
    visningsgeom = byggVisningsTre( relasjonstre )
    visningsgeom2 = byggVisningsTre( relasjonstre, kortesteLinje=True  )

