"""
Hjelper Heine & co med rapportering til et CEDR prosjekt 

Tre søk etter BK tømmertransport relevant for modulvogntog type 1 og 2, samt et modulvogntog BK. 
"""

import pandas as pd
import geopandas as gpd
from shapely import wkt

import STARTHER
import nvdbapiv3 
import nvdbgeotricks


if __name__ == '__main__': 

    filnavn = 'sample2_CEDR_Heine'
    gpkgfil = filnavn + '.gpkg'


    # sampleFilter = { 'kommune' : '4204' }
    sampleFilter = {}

    # BK modulvogntog 
    bk889 = nvdbgeotricks.kostraFiltrerDF(   nvdbgeotricks.nvdbsok2GDF( nvdbapiv3.nvdbFagdata( 889, filter=sampleFilter ) ))
    bk889.to_file( gpkgfil, driver='GPKG', layer='BK modulvogntog')
    tabell_bk889 = bk889.groupby( [ 'vegkategori', 'Maks totalvekt' ]).agg( {'segmentlengde' : 'sum' }).reset_index()
    tabell_bk889['Lengde [km]'] = tabell_bk889['segmentlengde'] / 1000 
    tabell_bk889 = tabell_bk889.drop( columns='segmentlengde' ) 

    # BK tømmetransport tillatt for mvt 1 og 2 = Ja
    # Henter ALT, filtrerer ut Bk10-50 og Bk10-60 og oppsummerer de variantene Heine vil ha 
    bk900 = nvdbgeotricks.kostraFiltrerDF(   nvdbgeotricks.nvdbsok2GDF( nvdbapiv3.nvdbFagdata( 900, filter=sampleFilter ) ))

    # Filtrerer vekk dårlige verdier for bruksklasse og maks. vogntoglengde 
    b900 = bk900[ bk900['Bruksklasse'].isin( ['Bk10 - 60 tonn', 'Bk10 - 50 tonn'] )]
    bk900 = bk900[ bk900['Maks vogntoglengde'].isin( ['19,50', '22,00', '24,00'] )]
    bk900.to_file( gpkgfil, driver='GPKG', layer='BK tømmertransport')

    tabell_bk900 = bk900.groupby( ['vegkategori', 'Tillatt for modulvogntog 1 og 2 med sporingskrav', 
                                    'Bruksklasse', 'Maks vogntoglengde' ]).agg( {'segmentlengde' : 'sum'}).reset_index()
    tabell_bk900['Lengde [km]'] = tabell_bk900['segmentlengde'] / 1000 
    tabell_bk900 = tabell_bk900.drop( columns='segmentlengde' ) 

    nvdbgeotricks.skrivexcel( filnavn + '.xlsx', [ tabell_bk900, tabell_bk889 ], sheet_nameListe=['BK tømmer', 'BK modulvogntog' ])

    # ['objekttype', 'nvdbId', 'versjon', 'startdato', 'Bruksklasse',
    #    'Strekningsbeskrivelse', 'Vegliste gjelder alltid',
    #    'Tillatt for modulvogntog 1 og 2 med sporingskrav',
    #    'Maks vogntoglengde', 'veglenkesekvensid', 'detaljnivå', 'typeVeg',
    #    'kommune', 'fylke', 'vref', 'veglenkeType', 'vegkategori', 'fase',
    #    'vegnummer', 'startposisjon', 'sluttposisjon', 'segmentlengde',
    #    'adskilte_lop', 'trafikantgruppe', 'segmentretning', 'geometri',
    #    'stedfesting_retning', 'Merknad', 'geometry']
