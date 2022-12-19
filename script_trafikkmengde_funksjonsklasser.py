"""
Kombinerer trafikkmengde med funksjonsklasse og 
motorveg/motortrafikkveg.  

`script_oppsummerModulvogntog.py` kombinerer ÅDT-verdier (fra objekttype 540 trafikkmengde) med motorveg og multipliserer ÅDT * lengden 
av de kombinerte vegsegmentene *365 for å få trafikkarbeidet (kjøretøy kilometer per år), som vi oppgir i millioner kjøretøy kilometer per år 
- på Europa-, Riks- og Fylkesveger. Kjøretida for scriptet er om lag 10 minutt.

$$
Trafikkarbeid\; i\; millioner\; kjt\; kilometer\; per\; år = \frac{365}{10^6} \sum  ÅDT (kjt/døgn) * Lengde (km)
$$

For å kombinere data for trafikkmengde med data for motorveg har jeg brukt metoden `finnoverlapp` i `nvdbgeotricks.py`, men først 
har jeg filtrert vekk sideanlegg, konnekteringslenker og adskilte løp = Mot med metoden `KOSTRAfiltrering` i `spesialrapporter.py`, 
som begge finnes i reposet `https://github.com/LtGlahn/nvdbapi-V3` Her er resultater per 17.12.2022:

|             |                               |                                  |                       |
|-------------|------------------------------:|---------------------------------:|----------------------:|
| Motorvegtype | trafikkarbeid mill kjt km/år  | Lengde traf.arbeid+motorveg (km) | Lengde motorveg (km)  |
| Motortrafikkveg |	1898                      | 	559                          |	563 |
| Motorveg	| 5810 	| 813  | 862

Merk at lengden vi får når vi kombinerer _540 Trafikkmengde_ med _595 Motorveg_ er noe kortere enn samlet lengde av motorveg.  
Dette har flere årsaker. En årsak er at  trafikkmengde-objektet ikke dekker alle veglenker. Den mest sannsynlige årsaken er at vi 
har fått nye motorveger som ikke får ÅDT-verdi før neste år. I noen tilfeller så kan vi også ha registrert Motorveg på litt snåle ramper, 
kryssdeler etc som ikke nødvendigvis skal ha en ÅDT-verdi.

Vi gjør tilsvarende for funksjonsklasse.  

|             |                               |                                  |                       |
|-------------|------------------------------:|---------------------------------:|----------------------:|
| Funksjonsklasse | trafikkarbeid mill kjt km/år  |	Lengde traf.arbeid+funksjonsklasse (km) | Lengde Funksjonsklasse-objekter (km) |
| A - Nasjonale hovedveger | 19942 | 10345 | 10527 |
| B - Regionale hovedveger |  8076 |  8928 |  9036 |
| C - Lokale hovedveger	   |  4593 |  8250 |  8304 |
| D - Lokale samleveger	   |  4088 | 13791 | 13842 |
| E - Lokale adkomstveger  |  1693 | 13595 | 13623 |

Igjen ser vi at lengden av funksjonsklasse-data (som ideelt sett er lik lengden av alt E-,R-,F-vegnettet) er 
noe større enn det vi får når vi tar overlappet av trafikmmengde + funksjonsklasse. Dette kan ha mange årsaker, at det har kommet 
til nye veger som ikke får ÅDT-verdi før i 2023 er den mest sannsynlige forklaringen. Men det kan også være _"snålheter"_ i vegnettet 
(kryssdeler, ramper etc) som ikke får ÅDT-verdi med dagens trafikkmengde-metodikk.   

"""
import pandas as pd
import geopandas as gpd 
from shapely import wkt
from datetime import datetime

import STARTHER
import nvdbapiv3 
import nvdbgeotricks
import spesialrapporter 

def dobleAdskilteTrafmengde( row ):
    """
    Dobler ÅDT-verdien der vi har adskilte løp
    """
    if row['adskilte_lop'] == 'Med':
        return row['ÅDT, total'] * 2
    else:
        return row['ÅDT, total']

if __name__ == '__main__': 
    # Bryr oss kun om ERF-veger 
    t0 = datetime.now()
    mittfilter = { 'vegsystemreferanse' : 'Ev,Rv,Fv'}

    # Henter vegnett
    veg = pd.DataFrame( nvdbapiv3.nvdbVegnett( filter=mittfilter ).to_records() )
    veg['geometry'] = veg['geometri'].apply( wkt.loads )
    veg = gpd.GeoDataFrame( veg, geometry='geometry', crs=5973 )
    veg2 = spesialrapporter.KOSTRAfiltrering( veg )
    tveg = datetime.now()
    print( f"Tidsbruk nedlasting vegnett {tveg-t0} ")

    # Henter funksjonsklasse 
    funk1 = pd.DataFrame( nvdbapiv3.nvdbFagdata( 912, filter=mittfilter ).to_records())
    funk1['geometry'] = funk1['geometri'].apply( wkt.loads )
    funk1 = gpd.GeoDataFrame( funk1, geometry='geometry', crs=5973 )
    funk2 = spesialrapporter.KOSTRAfiltrering( funk1 )

    # Henter motorveg 
    motorveg = pd.DataFrame( nvdbapiv3.nvdbFagdata( 595, filter=mittfilter ).to_records() )
    motorveg['geometry'] = motorveg['geometri'].apply( wkt.loads )
    motorveg = gpd.GeoDataFrame( motorveg, geometry='geometry', crs=5973 )
    motorveg2 = spesialrapporter.KOSTRAfiltrering( motorveg )

    # Henter trafikkmengde 
    traf = pd.DataFrame( nvdbapiv3.nvdbFagdata(540, filter=mittfilter).to_records() )
    traf['geometry'] = traf['geometri'].apply( wkt.loads )
    traf = gpd.GeoDataFrame( traf, geometry='geometry', crs=5973 )
    traf2 = spesialrapporter.KOSTRAfiltrering( traf )
    traf2['ÅDT, total'] = traf2.apply( dobleAdskilteTrafmengde, axis=1 ) # Dobler for adskilte løp

    t1 = datetime.now()
    print( f"Har hentet fagdata, tidsbruk= {t1-tveg} ")
    # Kombinerer trafikkmengde og funksjonsklasse


    # Kombinerer trafikkmengde og motorveg
    motorTraf = nvdbgeotricks.finnoverlapp( traf2, motorveg2, prefixB='motorveg_', klippgeometri=True )
    motorTraf['trafikkarbeid kjt km/år'] = motorTraf['segmentlengde'] * motorTraf['ÅDT, total'] * 365 / 1000 

    # Statistikk, trafikkarbeid motorveg 
    motorArb = motorTraf.groupby( 'motorveg_Motorvegtype').agg( { 'trafikkarbeid kjt km/år' : 'sum', 'segmentlengde' : 'sum'}).reset_index()
    motorArb['segmentlengde'] = motorArb['segmentlengde'] / 1000
    motorArb['trafikkarbeid kjt km/år'] = motorArb['trafikkarbeid kjt km/år'] / 1e6
    motorArb.rename( columns={ 'motorveg_Motorvegtype' : 'Motorvegtype', 'trafikkarbeid kjt km/år' : 'trafikkarbeid mill kjt km/år', 'segmentlengde' : 'Lengde traf.arbeid+motorveg (km)'}, inplace=True )
    mveglengde = motorveg2.groupby( 'Motorvegtype' ).agg( {'segmentlengde' : 'sum'}).reset_index()
    mveglengde['segmentlengde'] = mveglengde['segmentlengde'] / 1000 
    mveglengde.rename( columns={ 'segmentlengde' : 'Lengde motorveg (km)'}, inplace=True)
    motorArb = motorArb.merge( mveglengde, on='Motorvegtype')


    t2 = datetime.now()
    print( f"Har joinet trafikkmengde og motorveg, tidsbruk= {t2-t1} ")

    # Kombinerer trafikkmengde og funksjonsklasse
    funkTraf = nvdbgeotricks.finnoverlapp( traf2, funk2, prefixB='funk_', klippgeometri=True )
    funkTraf['trafikkarbeid kjt km/år'] = funkTraf['segmentlengde'] * funkTraf['ÅDT, total'] * 365 / 1000 


    t3 = datetime.now()

    print( f"Har joinet trafikkmengde og funksjonsklasse, tidsbruk= {t3-t2} ")

    # Oppsummerer trafikkarbeid per funksjonsklasse
    funkArb1 = funkTraf.groupby( [ 'funk_Funksjonsklasse'  ]).agg( { 'trafikkarbeid kjt km/år' : 'sum', 'segmentlengde' : 'sum' }).reset_index()
    funkArb1['trafikkarbeid kjt km/år'] = funkArb1['trafikkarbeid kjt km/år'] / 1e6
    funkArb1['segmentlengde'] = funkArb1['segmentlengde'] / 1000
    funkArb1.rename( columns={'funk_Funksjonsklasse' : 'Funksjonsklasse', 'trafikkarbeid kjt km/år' : 'trafikkarbeid mill kjt km/år',
                                 'segmentlengde' : 'Lengde traf.arbeid+funksjonsklasse (km)' }, inplace=True )

    # Legger til lengden av funksjonsklasse-objekter 
    funklengder = funk2.groupby( 'Funksjonsklasse' ).agg( {'segmentlengde' : 'sum' } ).reset_index()
    funklengder['segmentlengde'] = funklengder['segmentlengde'] / 1000
    funklengder.rename( columns={'segmentlengde' : 'Lengde Funksjonsklasse-objekter (km)' }, inplace=True )
    funkArb1 = funkArb1.merge( funklengder, on='Funksjonsklasse' )

    # Lager lengde-statistikk for vegnett + alle fagdata som inngår i analysen 
    # Dette er en grei ekstra kontroll over hvor heldekkende data vi reelt har 
    datalengder = veg2.groupby( 'vegkategori').agg( {'lengde' : 'sum'}).reset_index()
    datalengder['lengde'] = datalengder['lengde'] / 1000
    datalengder.rename( columns={'lengder' : 'Lengde vegnett (km)'})

    tmp = traf2.groupby( 'vegkategori').agg( {'segmentlengde' : 'sum'})
    tmp['segmentlengde'] = tmp['segmentlengde'] / 1000
    tmp.rename( columns={'segmentlengde' : 'Lengde trafikkmengde-data (km)'}, inplace=True)
    datalengder = datalengder.merge( tmp, on='vegkategori')

    tmp = funk2.groupby( ['vegkategori']).agg( { 'segmentlengde' : 'sum' })
    tmp['segmentlengde'] = tmp['segmentlengde'] / 1000
    tmp.rename( columns={'segmentlengde' : 'Lengde funksjonsklasse-data (km)'}, inplace=True)
    datalengder = datalengder.merge( tmp, on='vegkategori')

    # Lagrer til fil
    filnavn = 'trafikkarbeid_funksjonsklasser_motorveg'

    metadata = pd.DataFrame(  [ [ 'Uttaksdato fra NVDB',  t0.strftime('%Y-%m-%d') ],
                                ['KOSTRA-filtrering: Fjerner data for vegnett som er:',  'konnekteringslenke, adskilte løp=Mot, sideanlegg'],
                                ['Vi dobler ÅDT-verdien der vi har adskilte løp = MED' , ' (neste år kan vi bruke egenskapen "Trafikkmengde på adskilte løp")'], 
                                ['Merk at det er overlapp mellom motorveg og funksjonsklasse', 'Motorveger er typisk nasjonale eller regionale hovedveger'],
                                ['Du kan altså IKKE legge sammen trafikkarbeid på motorveg med trafikkarbeid på landsdekkende funksjonsklasser', ' '] 
                                ], columns=['Metadata', 'oppføring']   ) 

    nvdbgeotricks.skrivexcel( filnavn+'.xlsx', [ funkArb1,  motorArb, datalengder, metadata ],
                                    sheet_nameListe=[ 'Trafikkarb per funk.klasse', 'Trafikkarb per motorvegtype', 'Utstrekning grunnlagsdata', 'metadata'  ]   )


    gpkgfil = filnavn + '.gpkg'
    veg2.to_file(       gpkgfil, layer='KOSTRA-filtrert vegnett',                   driver='GPKG')
    traf2.to_file(      gpkgfil, layer='KOSTRA-filtrert trafikkmengde',             driver='GPKG')
    funk2.to_file(      gpkgfil, layer='KOSTRA-filtrert funksjonsklasse',           driver='GPKG')
    motorveg2.to_file(  gpkgfil, layer='KOSTRA-filtrert motorveg',                  driver='GPKG')
    motorTraf.to_file(  gpkgfil, layer='Motorveg pluss trafikkmengde',              driver='GPKG')
    funkTraf.to_file(   gpkgfil, layer='Funksjonsklasse pluss trafikkmengde',       driver='GPKG')
    
