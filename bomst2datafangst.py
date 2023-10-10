
import requests
from requests.auth import HTTPBasicAuth
import json 
import pandas as pd 
import geopandas as gpd 

def finnDakatID( objektTypeId, ignorerEgengeometri=True ):
    """
    Oversetter egenskapsnavn til NVDB ID for den egenskapstypen. Første versjon er hardkodet, men kan (bør)  være 
    datakatalogdrevet
    """

    dakat = requests.get( 'https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekttyper/' + str( objektTypeId ) + '.json'  ).json()
    oversett = {  x['navn'] : x['id'] for x in   dakat['egenskapstyper'] }

    if ignorerEgengeometri: 
        oversett.pop('Geometri, linje'          , None )
        oversett.pop('Geometri, punkt'          , None )
        oversett.pop('Geometri, flate'          , None )
        oversett.pop('Geometri, hjelpelinje'    , None )

    hardkode = {}

    if objektTypeId == 45: 
        
        hardkode = {    
                        'Bomstasjon ID': 9595,
                        'Bompengeanlegg ID': 9596,
                        'Operatør ID': 11883,
                        'Timesregel (velg JA / NEI)': 9412,
                        'Timesregel, varighet i minutter': 10952,
                        'Hvilke andre bomstasjoner har samme timesregel-rabatt? Du kan f.eks hente egenskapen "Passeringsgruppe" for en av de andre bomstasjonene fra http://vegkart.no' : 10951,
                        'Gratis gjennomkjøring ved HC-brikke (JA/NEI)': 9404,
                        'Merknad': 11565, # Havner i egenskapen "11565 Tilleggsinformasjon"
                        'Prosjektreferanse': 11051,
                        'ProsjektInternObjekt_ID': 12289,
                        'Eier (Statens, vegvesen, Nye Veier, fylkeskommune, kommune, privat, uavklart)': 7992,
                        'Vedlikeholdsansvarlig (Statens, vegvesen, Nye Veier, fylkeskommune, kommune, privat, uavklart)': 5799,
        
        }

    else: 
        pass 
        # raise NotImplementedError( f'Har ikke skrevet kode som støtter for objekttype {objektTypeId} ennå' )
        # Ikke helt sant - koden er ferdig skrevet, men vi kjenner ikke til om det er behov for å lage hardkoding for evt andre objekttyper
        # Dette tar du stilling til når behovet er der. 

    oversett.update( hardkode )

    return oversett 

def datafangstNvdbEgenskaper( row, oversettDict={}  ): 
    """
    Lager dictionary med egenskapsTypeId : verdi i hht datafangst geojson
    Dvs alle NVDB-egenskaper blir lagret som egen  attributes - dictuonary 
    https://apiskriv.vegdata.no/datafangst/datafangst-api#nytt-objekt-med-geometriegenskaper 
    """

    attributes = { }

    for mykey in row.keys():
        if mykey in oversettDict and not pd.isnull( row[mykey] )  :
            attributes[ oversettDict[mykey] ] = row[mykey ]

    return attributes 

def gdf2geojson( myGdf, objektTypeId=None, dakatVersjon=2.31, tag='gjenopprett',  comment='Lukket NVDB objekt konvertert til geojson'): 
    """Oversetter en geodataframe laget fra autopass-regnark => geojson slik datafangst vil ha dem"""

    if not objektTypeId: 
        if 'objekttype' in myGdf.columns: 
            objektTypeId = myGdf.iloc[0]['objekttype'] 
        else: 
            raise ValueError("Må vite hvilken objekttype vi jobber med før vi går videre" )

    # NVDB-egenskaper på dictionary-struktur til datafangst 

    oversett = finnDakatID( objektTypeId )    
    myGdf['attributes'] = myGdf.apply( lambda x : datafangstNvdbEgenskaper(x, oversettDict=oversett ), axis=1 )

    nyGdf = myGdf[['attributes', 'geometry'] ].copy()
    nyGdf['tag'] = tag
    nyGdf['typeId'] = objektTypeId
    nyGdf['comment'] = comment 
    nyGdf['dataCatalogVersion'] = str( dakatVersjon )


    return json.loads( nyGdf.to_json() )


if __name__ == '__main__': 

    excelfil = 'Vegfinans - E16 Eggemoen-Olum - oppstart 08.07.22.xlsx'
    mydf = pd.read_excel( excelfil, header=12 )


    # Lager geoDataframe 
    crs = 4326 # Alternativt 5973 - men trenger vi i så fall reprojisere til 4623 for at det skal være gyldig geojson? 
    myGdf = gpd.GeoDataFrame( mydf, geometry=gpd.points_from_xy( mydf['X-koordinat UTM sone 33 eller lengdegrad (grader Øst)'], mydf['Y-koordinat UTM sone 33 eller breddegrad (grader N)']  ), crs=crs )

    myGeojson = gdf2geojson( myGdf )
    

    #  r = requests.post( url, headers=headers, auth=HTTPBasicAuth('jajens', '******'), data=myGeojson)
    dfApi = 'https://datafangst.test.vegvesen.no/api/v1/contract/'
    kontrakt = 'cce14c58-aefa-4543-baab-0e8ed1be0a04'

    url = dfApi + kontrakt +  '/featurecollection'

