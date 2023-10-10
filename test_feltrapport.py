"""
Tester telling av antall kjørefelt i vegnettsrapport
"""
import pandas as pd
import geopandas as gpd 
from shapely import wkt


import STARTHER
import nvdbapiv3 

def tellfelt( feltoversikt, typefelt=[] ):
    felt = feltoversikt.split(',')
    count = 0
    for etfelt in felt:
        # Har vi eksplisitt angitt typefelt?
        if len(typefelt) > 0: 
            if etfelt.isdigit(): # Spesialbehanding av vanlige kjørefelt (1,2,3,...) 
                if any( etfelt == x for x in typefelt): 
                    count += 1 

            elif len( etfelt) > 1 and any( etfelt[1:] == x for x in typefelt ): 
                count += 1  

        # Kjører med standard felttyper
        elif 'O' in etfelt or 'H' in etfelt or 'V' in etfelt or 'S' in etfelt:
            pass
        else:
            count += 1
    return count

def telladskilte( adskilte_lop_tekst: str): 
    if adskilte_lop_tekst.upper() in ['MED', 'NEI']: 
        return 'MED eller NEI'
    else: 
        return 'MOT'


if __name__ == '__main__': 

    k_omraader = [  {'nummer': 9107, 'navn': '9107 Gudbrandsdalen 2021-2025'}, 
                    {'nummer': 3401, 'navn': '3401 Nordre Hedmarken 2022-2028'}, 
                    {'navn': 'I01E Innlandet fylkeskommune driftskontrakt Elektro 2021-2026'},
                    {'navn': 'Vegoppmerking Innlandet 2021-2023'},
                    {'nummer': 614, 'navn': '0614 Buskerud elektro og veglys 2023-2025'},
                    {'nummer': 102, 'navn': '30-102 Østfold Nord 2022-2027'}, 
                    {'nummer': 9352, 'navn': '9352 Bergen 2022-2027'}, 
                    {'nummer': 9361, 'navn': '9361 automasjon Vestland og Rogaland 2022-2025'} ]

    
    # for komr in k_omraader: 
    if True: 
        komr = k_omraader[0]
        print( f"Henter vegnett for kontraktsområde {komr['navn']}")

        mydf = pd.DataFrame( nvdbapiv3.nvdbVegnett( filter={'kontraktsomrade' : komr['navn'] } ).to_records() )
    

        # Uten Konnektering og kun vegtrasé-nivå 
        konnektering = mydf[ mydf['type'] == 'KONNEKTERING']
        # konnektering['geometry'] = konnektering['geometri'].apply( wkt.loads )
        # konnektering = gpd.GeoDataFrame( konnektering, geometry='geometry', crs=5973 )
        # konnektering.to_file( 'feltrapportdebug.gpkg', layer='konnektering', driver='GPKG' )

        mydf = mydf[ mydf['type'] == 'HOVED'].copy()

        # Legger på vegnummer
        mydf['vegnr'] = mydf['vref'].apply( lambda x : x.split()[0])

        # Håndtering adskilte løp
        mydf['TellAdskilteLøp'] = mydf['adskilte_lop'].apply( telladskilte )

        # Teller kjørefelt, vanlig metode
        mydf['Antall felt'] = mydf['feltoversikt'].apply( tellfelt )

        # Teller sykkelfelt
        mydf['Antall sykkelfelt'] = mydf['feltoversikt'].apply( lambda x : tellfelt( x, typefelt=['S']))

        # Legger på data for dem som mangler trafikantgruppe
        mydf['trafikantgruppe'].fillna( 'NULL', inplace=True  )

        # Kjørefeltlengde
        mydf['Kjørefeltlengde'] = mydf['lengde'] * mydf['Antall felt']
        mydf['Sykkelfeltlengde'] = mydf['lengde'] * mydf['Antall sykkelfelt']


        # Slår sammen kanalisert veg og enkel bilveg: 
        mydf['tellevegtype'] = mydf['typeVeg'].apply( lambda x : 'vanlig veg' if x in ['Enkel bilveg', 'Kanalisert veg'] else x )

        # Lager geodataframe
        mydf['geometry'] = mydf['geometri'].apply( wkt.loads )
        myGdf = gpd.GeoDataFrame( mydf, geometry='geometry', crs=5973 )

        # Kjørbart vegnett 
        bil = mydf[ mydf['trafikantgruppe'] == 'K']
        fot = mydf[ mydf['trafikantgruppe'] != 'K']


        print(  bil.groupby( [ 'vegnr', 'trafikantgruppe', 'tellevegtype', 'TellAdskilteLøp', 'Antall felt'  ] ).agg( {'Kjørefeltlengde' : 'sum' ,'lengde' : 'sum', 'Sykkelfeltlengde' : 'sum'}) ) 
        print(  mydf[ mydf['Antall sykkelfelt'] > 0 ].groupby( [ 'vegnr', 'trafikantgruppe', 'typeVeg', 'TellAdskilteLøp', 'Antall sykkelfelt'  ] ).agg( {'Kjørefeltlengde' : 'sum', 'Sykkelfeltlengde' : 'sum', 'lengde' : 'sum'}) ) 


        # Lengde bilveg

        # # Lagrer geopackage
        # for vegnr in myGdf['vegnr'].unique(): 
        #     myGdf[ myGdf['vegnr'] == vegnr ].to_file( 'feltrapportdebug.gpkg', layer=str(komr['nummer'])+'_'+vegnr, driver='GPKG')

    """
    Henter vegnett for kontraktsområde 9107 Gudbrandsdalen 2021-2025
                                                                Kjørefeltlengde      lengde  Sykkelfeltlengde
vegnr trafikantgruppe tellevegtype TellAdskilteLøp Antall felt
EV136 K               Rundkjøring  MED eller NEI   1                    148,925     148,925               0,0
                      vanlig veg   MED eller NEI   2                 121731,664   60865,832               0,0
EV6   K               Rampe        MED eller NEI   1                  17408,997   17408,997               0,0
                                                   2                    306,000     153,000               0,0
                      Rundkjøring  MED eller NEI   1                    290,202     290,202               0,0
                      vanlig veg   MED eller NEI   1                   2716,563    2716,563               0,0
                                                   2                 365774,380  182887,190               0,0
                                                   3                  26466,681    8822,227               0,0
                                                   4                  55257,584   13814,396               0,0
                                   MOT             1                    560,000     560,000               0,0
                                                   2                     21,498      10,749               0,0
RV15  K               Rundkjøring  MED eller NEI   1                    327,296     327,296               0,0
                      vanlig veg   MED eller NEI   1                    266,283     266,283               0,0
                                                   2                 283990,902  141995,451               0,0
                                                   3                    270,315      90,105               0,0
                                                                   Kjørefeltlengde  Sykkelfeltlengde  lengde
vegnr trafikantgruppe typeVeg   TellAdskilteLøp Antall sykkelfelt
EV136 G               Sykkelveg MED eller NEI   2                              0,0            52,352  26,176
    

Ev136 = mydf[ mydf['vegnr'] == 'EV136' ]

 Ev136.groupby( ['trafikantgruppe', 'feltoversikt']).agg( { 'Kjørefeltlengde' : 'sum', 'Sykkelfeltlengde' : 'sum', 'lengde' : 'sum' } )
Out[152]:
                              Kjørefeltlengde  Sykkelfeltlengde     lengde
trafikantgruppe feltoversikt
G               1,2                 84565.286             0.000  42282.643
                1S,2S                   0.000            52.352     26.176
K               1                     148.925             0.000    148.925
                1,1H1,2               186.236             0.000     93.118
                1,2                121245.374             0.000  60622.687
                1,2,2H1               300.054             0.000    150.027

 Ev136.groupby( ['trafikantgruppe', 'typeVeg',  'feltoversikt']).agg( { 'Kjørefeltlengde' : 'sum', 'Sykkelfeltlengde' : 'sum', 'lengde' : 'sum' } )
Out[153]:
                                                 Kjørefeltlengde  Sykkelfeltlengde     lengde
trafikantgruppe typeVeg            feltoversikt
G               Gang- og sykkelveg 1,2                 84534.598             0.000  42267.299
                Sykkelveg          1,2                    30.688             0.000     15.344
                                   1S,2S                   0.000            52.352     26.176
K               Enkel bilveg       1,1H1,2               186.236             0.000     93.118
                                   1,2                120944.034             0.000  60472.017
                                   1,2,2H1               300.054             0.000    150.027
                Kanalisert veg     1,2                   301.340             0.000    150.670
                Rundkjøring        1                     148.925             0.000    148.925                


Bør skille mellom sykkelfelt langs kjøreveg (trafikantgruppe=K) og typeVeg=[en av dem som er opprettet for gående og syklende]                

# Ser på vegnettsrapport 

ev6 = gpd.read_file( 'feltrapportdebug.gpkg', layer='9107_EV6' )
ev6.groupby( ['trafikantgruppe', 'feltoversikt' ] )
ev6.groupby( ['trafikantgruppe', 'feltoversikt' ] ).agg( { 'Kjørefeltlengde' : 'sum', 'Sykkelfeltlengde' : 'sum', 'lengde' : 'sum' } )
ev6.groupby( ['trafikantgruppe', 'typeVeg', 'feltoversikt' ] ).agg( { 'Kjørefeltlengde' : 'sum', 'Sykkelfeltlengde' : 'sum', 'lengde' : 'sum' } )
ev6.groupby( ['trafikantgruppe', 'tellevegtype', 'Antall felt' ] ).agg( { 'Kjørefeltlengde' : 'sum', 'Sykkelfeltlengde' : 'sum', 'lengde' : 'sum' } )
ev6.groupby( ['trafikantgruppe', 'tellevegtype', 'TellAdskilteLøp', 'Antall felt' ] ).agg( { 'Kjørefeltlengde' : 'sum', 'Sykkelfeltlengde' : 'sum', 'lengde' : 'sum' } )
ev136 = gpd.read_file( 'feltrapportdebug.gpkg', layer='9107_EV136' )
ev136.groupby( ['trafikantgruppe', 'tellevegtype', 'TellAdskilteLøp', 'Antall felt' ] ).agg( { 'Kjørefeltlengde' : 'sum', 'Sykkelfeltlengde' : 'sum', 'lengde' : 'sum' } )
rv15 = gpd.read_file( 'feltrapportdebug.gpkg', layer='9107_RV15' )
rv15.groupby( ['trafikantgruppe', 'tellevegtype', 'TellAdskilteLøp', 'Antall felt' ] ).agg( { 'Kjørefeltlengde' : 'sum', 'Sykkelfeltlengde' : 'sum', 'lengde' : 'sum' } )
rv15.groupby( ['trafikantgruppe', 'tellevegtype', 'TellAdskilteLøp', 'Antall felt', 'feltoversikt' ] ).agg( { 'Kjørefeltlengde' : 'sum', 'Sykkelfeltlengde' : 'sum', 'lengde' : 'sum' } )
ev136.groupby( ['trafikantgruppe', 'tellevegtype', 'TellAdskilteLøp', 'Antall felt', 'feltoversikt' ] ).agg( { 'Kjørefeltlengde' : 'sum', 'Sykkelfeltlengde' : 'sum', 'lengde' : 'sum' } )
k9107 = pd.concat( [ ev6, ev136, rv15 ] )
import pandas as pd
k9107 = pd.concat( [ ev6, ev136, rv15 ] )
k9107['lengde'].sum()
k9107[ k9107['vref'].str.contains( 'KS' )]
k9107[ k9107['vref'].str.contains( 'K' )]
k9107[ k9107['vref'].str.contains( 'KD' )]
k9107[ k9107['vref'].str.contains( 'SA' )]
k9107.groupby( ['trafikantgruppe']).agg( {'Kjørefeltlengde' : 'sum', 'Sykkelfeltlengde' : 'sum', 'lengde' : 'sum'}) )
k9107.groupby( ['trafikantgruppe']).agg( {'Kjørefeltlengde' : 'sum', 'Sykkelfeltlengde' : 'sum', 'lengde' : 'sum'})
k9107.groupby( ['trafikantgruppe', 'typeVeg']).agg( {'Kjørefeltlengde' : 'sum', 'Sykkelfeltlengde' : 'sum', 'lengde' : 'sum'})

# KOSTRA
kostra = k9107[ k9107['trafikantgruppe'] == 'K' ]

kostra = kostra[ kostra['adskilte_lop'] != 'Mot']

# Filtrerer vekk sideanlegg 
kostra = kostra[ ~kostra['vref'].str.contains( 'SA' )]

kostra['typeVeg'].value_counts()
kostra['lengde'].sum()

    """