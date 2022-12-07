"""
Oppsummerer data for modulvogntog, med sikte på å svare ut spørsmålene fra 

ToS bes om å levere følgende:
1. Modulvogntog: Angi hvor mange km og prosent av veinettet som er og ikke er åpnet for
modulvogntog type 1 og 2, fordelt på fylkesveier og riksveier.

2. Modulvogntog: Angi om strekninger vil åpnes som følge av prioriterte større investeringstiltak. Beskriv effekter for toppmålene for øvrige trafikantgrupper, som for eksempel økt trafikksikkerhet og reduserte reisetider gjennom fjerning av gjeldende flaskehalser.

3. Tømmervogntog: Angi hvor mange km og prosent av veinettet som er og ikke er åpnet for 24 m lange og 60 tonn tunge tømmervogntog eller større, fordelt på fylkesveier og riksveier.

4. Modul- og tømmervogntog: Vurder om noen strekninger av fylkesveinettet som er åpnet for 24m lange og 60 tonn tunge tømmervogntog, med mindre tiltak sannsynligvis også kan åpnes modulvogntog type 1 og 2. Angi hvilke tiltak dette for eksempel kan dreie seg om.

5. Punktene 1 til 4 visualiseres på kart: 
   a) Synliggjøring av strekninger som verken er åpnet for modulvogntog (type 1 og 2) eller tømmervogntog (24 m og 60 tonn), 
   b) strekninger som er åpnet for tømmervogntog (24 m og 60 tonn), men ikke er åpnet for modulvogntog (type 1 og 2),
   c) lokalisering av mulige mindre tiltak og 
   d) store prosjekter som vil medføre åpning av nye strekninger.

6. Trafikksikkerhet: Vurder behovet for trafikksikkerhetstiltak direkte rettet mot laste- og varebiler inkludert kostnader (utover prioriterte generelle trafikksikkerhetstiltak) og effekter. Arbeidet gjøres i samarbeid med ToS og DIA (mulighetene for økt bruk av data og teknologi).
"""

from shapely import wkt 

import STARTHER
import nvdbapiv3
import nvdbgeotricks
import pandas as pd
import geopandas as gpd


if __name__ == '__main__': 
    mittfilter = { 'vegsystemreferanse' : 'Ev,Rv,Fv' }
    sok = nvdbapiv3.nvdbFagdata(900)
    sok.filter( mittfilter ) 
    bk = pd.DataFrame( sok.to_records() )
    bk = bk[ bk['veglenkeType'] == 'HOVED' ]
    bk = bk[ bk['trafikantgruppe'] == 'K' ]
    bk = bk[ bk['adskilte_lop'] != 'Mot' ].copy()
    bk['lengde (km)'] = bk['segmentlengde'] / 1000

    tillattTommer = bk.groupby( ['vegkategori', 
            'Tillatt for modulvogntog 1 og 2 med sporingskrav', 'Bruksklasse', 
            'Maks vogntoglengde', 'Maks totalvekt']).agg( {'lengde (km)' : 'sum' } ).reset_index()

    bk['geometry'] = bk['geometri'].apply( wkt.loads ) 
    bk = gpd.GeoDataFrame( bk, geometry='geometry', crs=5973) 

    sok = nvdbapiv3.nvdbFagdata( 889)
    sok.filter( mittfilter ) 
    bkmodul = pd.DataFrame( sok.to_records() )
    bkmodul = bkmodul[ bkmodul['veglenkeType'] == 'HOVED' ]
    bkmodul = bkmodul[ bkmodul['trafikantgruppe'] == 'K' ]
    bkmodul = bkmodul[ bkmodul['adskilte_lop'] != 'Mot' ].copy()
    bkmodul['lengde (km)'] = bkmodul['segmentlengde'] / 1000
    bkmodul['Gjelder ikke linksemitrailer'].fillna( '', inplace=True )    
    bkmodul['geometry'] = bkmodul['geometri'].apply( wkt.loads ) 
    bkmodul = gpd.GeoDataFrame( bkmodul, geometry='geometry', crs=5973) 

    modulvogntoglengde = bkmodul.groupby( ['vegkategori', 
            'Gjelder ikke linksemitrailer']).agg( { 'lengde (km)' : 'sum' } ).reset_index()

    sok = nvdbapiv3.nvdbVegnett()
    sok.filter( mittfilter )
    sok.filter( { 'veglenketype' : 'hoved', 'trafikantgruppe' : 'K' } )
    veg = pd.DataFrame( sok.to_records())
    veg = veg[ veg['type'] == 'HOVED' ]
    veg = veg[ veg['trafikantgruppe'] == 'K' ]
    veg = veg[ veg['adskilte_lop'] != 'Mot' ].copy()
    veg['lengde (km)'] = veg['lengde'] / 1000

    veg['geometry'] = veg['geometri'].apply( wkt.loads ) 
    veg = gpd.GeoDataFrame( veg, geometry='geometry', crs=5973) 
    
    veglengde = veg.groupby( 'vegkategori' ).agg( { 'lengde (km)' : 'sum' } ).reset_index()
    
    nvdbgeotricks.skrivexcel( 'modulvogntogOskar.xlsx', [ veglengde, modulvogntoglengde, tillattTommer], 
                        sheet_nameListe=['Lengde vegnett', 'BK modulvogntog', 'BK tømmertransport']) 
                       
    gpkgfil = 'modulvogntogOskar.gpkg'
    veg.to_file(  gpkgfil, layer='vegnett', driver='GPKG') 
    bkmodul.to_file(    gpkgfil, layer='BK Modulvogntog', driver='GPKG') 
    bk.to_file(         gpkgfil, layer='BK Tømmertransport', driver='GPKG') 
