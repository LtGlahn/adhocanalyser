# adhocanalyser

Forskjellige ad-hoc analyser. Mest NVDB data, men litt anna morro også

Hovedgreina til dette reposet er altså et "boilerplate" utgangspunkt. 

Selve analysene ligger som branches til dette reposet. Disse lages fortløpende etter behov. Flere av dem er ikke annet enn arbeidsområder 
som er gyldige en viss tid inntil det blir uoversiktlig mange filer inni der. Men det er også enkelte analyseoppgaver som fortjener en grein helt for seg sjøl. 


Ymse "work in progress" - oppgaver fra november 20222 og fram til det blir passe mye her...


# Arbeidsfiler november 2022 -- XXX 

## Trafikkarbeid på motorveg og per funksjonsklasse

`script_oppsummerModulvogntog.py` kombinerer ÅDT-verdier (fra objekttype 540 trafikkmengde) med motorveg og multipliserer ÅDT * lengden av de kombinerte vegsegmentene *365 for å få trafikkarbeidet (kjøretøy kilometer per år), som vi oppgir i millioner kjøretøy kilometer per år - på Europa-, Riks- og Fylkesveger. 

$$
Trafikkarbeid\; i\; millioner\; kjt\; kilometer\; per\; år = \frac{365}{10^6} \sum  ÅDT (kjt/døgn) * Lengde (km)
$$

For å kombinere data for trafikkmengde med data for motorveg har jeg brukt metoden `finnoverlapp` i `nvdbgeotricks.py`, men først har jeg filtrert vekk sideanlegg, konnekteringslenker og adskilte løp = Mot med metoden `KOSTRAfiltrering` i `spesialrapporter.py`, som begge finnes i reposet `https://github.com/LtGlahn/nvdbapi-V3` Her er resultater per 17.12.2022:

|             |                               |                                  |                       |
|-------------|------------------------------:|---------------------------------:|----------------------:|
| Motorvegtype | trafikkarbeid mill kjt km/år  | Lengde traf.arbeid+motorveg (km) | Lengde motorveg (km)  |
| Motortrafikkveg |	1898                      | 	559                          |	563 |
| Motorveg	| 5810 	| 813  | 862

Merk at lengden vi får når vi kombinerer _540 Trafikkmengde_ med _595 Motorveg_ er noe kortere enn samlet lengde av motorveg.  Dette har flere årsaker. En årsak er at  trafikkmengde-objektet ikke dekker alle veglenker. Den mest sannsynlige årsaken er at vi har fått nye motorveger som ikke får ÅDT-verdi før neste år. I noen tilfeller så kan vi også ha registrert Motorveg på litt snåle ramper, kryssdeler etc som ikke nødvendigvis skal ha en ÅDT-verdi.

Vi gjør tilsvarende for funksjonsklasse.  

|             |                               |                                  |                       |
|-------------|------------------------------:|---------------------------------:|----------------------:|
| Funksjonsklasse | trafikkarbeid mill kjt km/år  |	Lengde traf.arbeid+funksjonsklasse (km) | Lengde Funksjonsklasse-objekter (km) |
| A - Nasjonale hovedveger | 19942 | 10345 | 10527 |
| B - Regionale hovedveger |  8076 |  8928 |  9036 |
| C - Lokale hovedveger	   |  4593 |  8250 |  8304 |
| D - Lokale samleveger	   |  4088 | 13791 | 13842 |
| E - Lokale adkomstveger  |  1693 | 13595 | 13623 |

Igjen ser vi at lengden av funksjonsklasse-data (som ideelt sett er lik lengden av alt E-,R-,F-vegnettet) er noe større enn det vi får når vi tar overlappet av trafikmmengde + funksjonsklasse. Dette kan ha mange årsaker, at det har kommet til nye veger som ikke får ÅDT-verdi før i 2023 er den mest sannsynlige forklaringen. Men det kan også være _"snålheter"_ i vegnettet (kryssdeler, ramper etc) som ikke får ÅDT-verdi med dagens trafikkmengde-metodikk.   