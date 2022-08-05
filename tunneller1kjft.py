"""
Finner tunneller med kun 1 kjørefelt 

Ettersom NVDB api LES ikke oppgir hvilke kjørefelt som _*finnes*_ for vegobjektenes stedfesting
så må vi kombinere data fra vegobjekttype tunnelløp med data fra vegnettet (/vegnett/segmentert/)
"""

import pandas as pd
import geopandas as gpd 
from shapely import wkt 


import STARTHER
import nvdbapiv3
import nvdbgeotricks 

def lagestedfesting( row ):
    # Litt knot fordi python bruker eksponentnotasjon når tallene er mindre enn 1e-6 eller deromkring
    # Vi trenger 8 desimaler 
    mystr = f"{row['startposisjon']:.8f}-{row['sluttposisjon']:.8f}@{row['veglenkesekvensid']}"
    return mystr
    # OK, vi fikk ikke bruk for denne funksjonen denne gangen (ettersom vi ikke kan hente 
    # vegnet ut fra veglenkeposisjoner: Filteret veglenkesekvens=0-1@12235 funker kun for vegobjekter)
    # Men lar den ligge til senere bruk; dette er nok nyttig senere

if __name__ == '__main__': 

    gpkgfil = 'tunnel1felt.gpkg'

    # # Funker ikkke å laste ned vegnett med filter medium 
    # v = nvdbapiv3.nvdbVegnett()
    # v.filter( { 'medium' : 'U'})
    # mydf = pd.DataFrame( v.to_records())

    t = nvdbapiv3.nvdbFagdata( 67)
    mydf = pd.DataFrame( t.to_records() )
    mydf['geometry'] = mydf['geometri'].apply( wkt.loads )
    myGdf = gpd.GeoDataFrame( mydf, geometry='geometry', crs=5973 )

    # Lager stedfesting:
    # Overflødig, viste det seg - vi får ikke brukt den
    # myGdf['stedfesting'] = myGdf.apply(  lagestedfesting, axis=1)

    # Tar vekk tunneller der det er adskilte løp
    myGdf = myGdf[ myGdf['adskilte_lop'] == 'Nei'].copy()

    
    # Dropper dictionary datastrukturer, de støttes ikke i join og lagring til GPKG
    myGdf.drop( columns=['relasjoner', 'geometri'], inplace=True )
    myGdf.to_file( gpkgfil, layer='tunnelvegobjekt', driver='GPKG')

    # OK, ser ut som om vi må løse oppgaven på den harde måten: Laste ned ALT vegnett og filtrere på tunnel (medium=U)
    # veger = pd.DataFrame( veg.to_records() ) #TIDKREVENDE - 20 minutt? 
    # tunneller = veger[ veger['medium'] == 'U'].copy()
    # tunneller['geometry'] = tunneller['geometri'].appy( wkt.loads ) # Trenger geometri til join (slik jeg har implementert den)
    # col = [ 'veglenkesekvensid',  'startposisjon', 'sluttposisjon', 'type', 
    #         'detaljnivå', 'typeVeg', 'feltoversikt', 'kommune', 'vref', 'trafikantgruppe', 
    #         'adskilte_lop', 'medium', 'geometry' ]
    
    # tunneller = tunneller[col].copy()
    # tunneller = gpd.GeoDataFrame( tunneller, geometry='geometry', crs=5973)
    # tunneller.to_file( gpkgfil, layer='tunnel_vegnett', driver='GPKG')

    # # OK, sparer tid på å bare laste inn igjen det datasettet vi nettopp lagret
    tunneller = gpd.read_file( gpkgfil, layer='tunnel_vegnett')

    # Finner overlapp
    joined = nvdbgeotricks.finnoverlapp( myGdf, tunneller, prefixB='vegn_' )
    if isinstance( joined.iloc[0]['geometry'], str): 
        joined['geometry'] = joined['geometry'].apply( wkt.loads )
    joined = gpd.GeoDataFrame( joined, geometry='geometry', crs=5973)
    joined.to_file( gpkgfil, layer='joined', driver='GPKG' )

    ettfelt = joined[ joined['vegn_feltoversikt'] == '1']
    ettfelt.to_file( gpkgfil, layer='ettfelt', driver='GPKG')

    tofelt = joined[ joined['vegn_feltoversikt'] == '1,2']
    tofelt.to_file( gpkgfil, layer='tofelt', driver='GPKG')

    # Visuell inspeksjon i QGIS avslører at joda, metoden funker så fint som bare det - men det viser seg at problemet ikke er å finne
    # tunneller med ett kjørefelt. Problemet er å finne smale, kjipe tunneller med trafikk i begge retninger
    # Disse har typisk kjørefelt=1,2. Og det er 1078 av dem... Vi har ikke informasjon til å identifisere disse tunnellene, 
    # dessverre. 

