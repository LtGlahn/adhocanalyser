"""
Finner tunneller med kun 1 kjørefelt 

Ettersom NVDB api LES ikke oppgir hvilke kjørefelt som _*finnes*_ for vegobjektenes stedfesting
så må vi kombinere data fra vegobjekttype tunnelløp med data fra vegnettet (/vegnett/segmentert/)
"""
import requests 
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from copy import deepcopy

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

def finnMortunnell( relasjonsDict: dict  ): 

    morTunnelId = None 
    morTunnelNavn = None 
    morTunnelLengde = None 

    if 'foreldre' in relasjonsDict:
        tunnellobj = [ x for x in relasjonsDict['foreldre'] if x['type']['id'] == 581 ] 
        if len( tunnellobj ) == 1 and len( tunnellobj[0]['vegobjekter'] ) == 1: 
            mittobj = nvdbapiv3.finnid( tunnellobj[0]['vegobjekter'][0] )
            if len( mittobj ) == 1: 
                mittobj = nvdbapiv3.nvdbFagObjekt( mittobj[0 ])
                morTunnelId = mittobj.id
                morTunnelNavn = mittobj.egenskapverdi( 'Navn')
                morTunnelLengde = mittobj.egenskapverdi( 'Lengde, offisiell')

    return  (morTunnelId, morTunnelNavn, morTunnelLengde)



if __name__ == '__main__': 

    gpkgfil = 'tunnel1felt.gpkg'

    # # Funker ikkke å laste ned vegnett med filter medium 
    # # v = nvdbapiv3.nvdbVegnett()
    # # v.filter( { 'medium' : 'U'})
    # # mydf = pd.DataFrame( v.to_records())

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
    veg = nvdbapiv3.nvdbVegnett()
    veger = pd.DataFrame( veg.to_records() ) #TIDKREVENDE - 20 minutt? 
    tunneller = veger[ veger['medium'] == 'U'].copy()
    tunneller['geometry'] = tunneller['geometri'].apply( wkt.loads ) # Trenger geometri til join (slik jeg har implementert den)
    col = [ 'veglenkesekvensid',  'startposisjon', 'sluttposisjon', 'type', 
            'detaljnivå', 'typeVeg', 'feltoversikt', 'kommune', 'vref', 'trafikantgruppe', 
            'adskilte_lop', 'medium', 'geometry' ]
    
    tunneller = tunneller[col].copy()
    tunneller = gpd.GeoDataFrame( tunneller, geometry='geometry', crs=5973)
    tunneller.to_file( gpkgfil, layer='tunnel_vegnett', driver='GPKG')

    # # OK, sparer tid på å bare laste inn igjen det datasettet vi nettopp lagret
    # tunneller = gpd.read_file( gpkgfil, layer='tunnel_vegnett')

    # # Finner overlapp
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

    # # Leser data fra FME analyse, som henter metadata om vegbilder fra WFS-tjeneste og plukker ut ett av dem
    # bilde = gpd.read_file( '../wip_tungedata/vegbilderWFS.gpkg', layer='vegbilder2020-til2022-08-05')

    # # Henter liste med bilder
    # vegbilder = []
    # for ix, row in bilde.iterrows(): 
    #     if  len( row['URL']) > 10: 
    #         try: 
    #             im = Image.open(requests.get(row['URL'], stream=True).raw)
    #         except UnidentifiedImageError: 
    #             vegbilder.append( None )
    #             print( f"Henting av vegbilde feiler {row['nvdbId']} {row['Navn']} ")
    #         else: 
    #             vegbilder.append( deepcopy( im ) )
    #     else: 
    #         vegbilder.append( None )

    # bilde['vegbilde'] = ' '
    # bilde['vegkart'] = 'https://vegkart.atlas.vegvesen.no/#valgt:' + bilde['nvdbId'].astype(str) + ':67'

    # # Skriver excel-rapport
    # col = [ 'vegkategori', 'vref', 'Navn', 'Lengde', 'Bredde',  'kommune', 'nvdbId', 'vegkart', 'vegbilde'  ]
    # writer = pd.ExcelWriter( 'tunnelvegbilder.xlsx',engine='xlsxwriter')
    # arknavn = 'Vegbilder i tunnel'
    # bilde.to_excel( writer, sheet_name=arknavn, index=False )
    # # Auto-adjust columns' width. 
    # # Fra https://towardsdatascience.com/how-to-auto-adjust-the-width-of-excel-columns-with-pandas-excelwriter-60cee36e175e
    # for column in bilde: 
    #     col_idx = bilde.columns.get_loc(column)
    #     if str(column) == 'vegbilde': 
    #         column_width = 700
    #     else:
    #         column_width = max(bilde[column].astype(str).map(len).max(), len(column)) + 3
    #     writer.sheets[arknavn].set_column(col_idx, col_idx, column_width)

    # # Setter kolonnehøyde = 250px eller noe, slik at det blir plass til bilde
    # # https://stackoverflow.com/a/70434277
    # workbook = writer.book
    # worksheet = writer.sheets[arknavn]
    # for k in range( 0, len( bilde )): 
    #     worksheet.set_row( k+1, 300)

    # # Setter inn bilde
    # for ix, im in enumerate( vegbilder): 

    #     if im: 
    #         # skalerer bildet
    #         newHeight = 250 
    #         imWidth, imHeigth = im.size 
    #         scale_factor = imHeigth / newHeight 
    #         newWidth = round( imWidth / scale_factor )
    #         nedskalert = im.resize((newWidth,newHeight))
    #         nedskalert.save( 'vegbilde.jpg')

    #         byte_io = BytesIO()
    #         nedskalert.save(byte_io, format='png' )
    #         worksheet.insert_image( 'Q'+ str( ix+1 ), 'vegbilde.jpg', { 'data' : byte_io, 'x_offset': 15, 'y_offset': 10 }  )

    # writer.save()