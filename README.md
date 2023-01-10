# adhocanalyser

Forskjellige ad-hoc analyser. Mest NVDB data, men litt anna morro også

Hovedgreina til dette reposet er altså et "boilerplate" utgangspunkt. 

Selve analysene ligger som branches til dette reposet. Disse lages fortløpende etter behov. Flere av dem er ikke annet enn arbeidsområder 
som er gyldige en viss tid inntil det blir uoversiktlig mange filer inni der. Men det er også enkelte analyseoppgaver som fortjener en grein helt for seg sjøl. 


Ymse "work in progress" - oppgaver fra november 20222 og fram til det blir passe mye her...


# Arbeidsfiler november 2022 -- januar 2023

## Trafikkarbeid på motorveg og per funksjonsklasse

`script_trafikkmengde_funksjonsklasser.py` kombinerer ÅDT-verdier (fra objekttype 540 trafikkmengde) med motorveg og multipliserer ÅDT * lengden av de kombinerte vegsegmentene *365 for å få trafikkarbeidet (kjøretøy kilometer per år), som vi oppgir i millioner kjøretøy kilometer per år - på Europa-, Riks- og Fylkesveger. Kjøretida for scriptet er om lag 10 minutt.

$$
Trafikkarbeid\; i\; millioner\; kjt\; kilometer\; per\; år = \frac{365}{10^6} \sum  ÅDT (kjt/døgn) * Lengde (km)
$$

For å kombinere data for trafikkmengde med data for motorveg har jeg brukt metoden `finnoverlapp` i `nvdbgeotricks.py`, men først har jeg filtrert vekk sideanlegg, konnekteringslenker og adskilte løp = Mot med metoden `KOSTRAfiltrering` i `spesialrapporter.py`, som begge finnes i reposet `https://github.com/LtGlahn/nvdbapi-V3` Her er resultater per 17.12.2022:

|             |                               |                                  |                       |
|-------------|------------------------------:|---------------------------------:|----------------------:|
| Motorvegtype | trafikkarbeid mill kjt km/år  | Lengde traf.arbeid+motorveg (km) | Lengde motorveg (km)  |
| Motortrafikkveg |	1898                      | 	559                          |	563 |
| Motorveg	| 5810 	| 813  | 862

Merk at lengden vi får når vi kombinerer _540 Trafikkmengde_ med _595 Motorveg_ er noe kortere enn samlet lengde av motorveg.  Dette har flere årsaker. En årsak er at  trafikkmengde-objektet ikke dekker alle veglenker. Den mest sannsynlige årsaken er at vi har fått nye motorveger som ikke får ÅDT-verdi før neste år. I noen tilfeller så kan vi også ha registrert Motorveg på litt snåle ramper, kryssdeler etc som ikke nødvendigvis skal ha en ÅDT-verdi. _Vi kunne fjernet ramper og kryssdeler fra analysen, men det ble ikke vurdert pga tidspress._

Vi gjør tilsvarende for funksjonsklasse: Finner overlapp med trafikkmengde-objekter og regner ut trafikkarbeidet per funksjonsklasse. 

|             |                               |                                  |                       |
|-------------|------------------------------:|---------------------------------:|----------------------:|
| Funksjonsklasse | trafikkarbeid mill kjt km/år  |	Lengde traf.arbeid+funksjonsklasse (km) | Lengde Funksjonsklasse-objekter (km) |
| A - Nasjonale hovedveger | 19942 | 10345 | 10527 |
| B - Regionale hovedveger |  8076 |  8928 |  9036 |
| C - Lokale hovedveger	   |  4593 |  8250 |  8304 |
| D - Lokale samleveger	   |  4088 | 13791 | 13842 |
| E - Lokale adkomstveger  |  1693 | 13595 | 13623 |

Igjen ser vi at lengden av funksjonsklasse-data (som ideelt sett er lik lengden av alt E-,R-,F-vegnettet) er noe større enn det vi får når vi tar overlappet av trafikmmengde + funksjonsklasse. Dette kan ha mange årsaker, at det har kommet til nye veger som ikke får ÅDT-verdi før i 2023 er den mest sannsynlige forklaringen. Men det kan også være _"snålheter"_ i vegnettet (kryssdeler, ramper etc) som ikke får ÅDT-verdi med dagens trafikkmengde-metodikk.   

## Hvor mye av hovedvegnettet er åpent for modulvogntog?

`sript_oppsummerModulvogntog.py` oppsummerer fordelingen av de ulike egenskapverdiene som er relevante for modulvogntog for objekttypene _889 Bruksklasse modulvogntog_ og _900 Bruksklasse tømmertransport_ på ERF-vegnettet. I tillegg lages en datadump til kartproduksjon. Vi oppsummerer også lengde vegnettet for debugging pluss at vi også kan si noe om hvor stor andel av vegnettet som mangler data for 900 BK tømmertransport. 

Pga tidsnød er IKKE tallene konsistente med KOSTRA-rapportering ved at de også inkluderer _sideanlegg_ og vegtypen _Bilferje_, men de tre datasettene (vegnett, 889 BK modulvogntog og 900 BK tømmertransport) skal være internt konsistente. 

Avvik fra de offisielle KOSTRA-tallene: 

| Avvik             | vegnett | 900 BK Tømmertransport | 889 BK Modulvogntog | 
|-------------------|---------|------------------------|---------------------|
| Vegtype Bilferjer | +503 km  |               +365km |                   0 |
| Sideanlegg        | +310 km  |               +146km |               +45km |

Cirka 80 km av KOSTRA-vegnettet (per 20.12.2022) mangler data for objekttypen _900 Bruksklasse Tømmertransport_ - som jo skal være heldekkende på det kjørbare ERFK - vegnettet. P.t. (januar 2023) har vi betydelige aktiviter for å fylle disse "hullene", dels maskinelt og dels manuelt. 

Ved fremtidige uttak av denne typen anbefaler jeg å gjøre filtrering konsistent med KOSTRA-utregningen, så tallene blir mer sammenlignbare med annen statistikk. 

Scriptet lager en tabell med lengdefordeling for de ulike kombinasjonene av egenskapverdier for objekttypen 900 BK Tømmertransport, og tilsvarende tabell for 889 BK Modulvogntog. Disse tabellene må selvsagt brukes med forbeholdet om at lengdene er littegrann større enn lengden av KOSTRA-vegnettet ved at lengdene også inkluderer bilferjer og sideanlegg. 

## Hvor kan vi kjøre tømmer-modulvogntog, men ikke vanlig modulvogntog? 

`script_modulvogntogdifferanser.py` har et helt annet fokus: Her skal vi finne det vegnettet der man kan kjøre tømmer-modulvogntog (maks vogntoglengde=24m) og vanlig modulvogntog. Såkalt tømmer-modulvogntog (24m) er regulert via objekttypen 900 Bruksklasse Tømmertransport. Fokuset for denne dataproduksjonen er altså **OVERLAPP** (og manglende overlapp) mellom datasettene. 

Bortsett fra at vi tar vekk konnekteringslenker _(og i ettertid tror jeg kanskje de også burde vært med, fordi vegnettet er jo ikke navigerbart uten konnekteringslenker?)_ så gjør vi INGENTING av den filtreringen som er relevant for annen type statistikk, f.eks KOSTRA. Fokuset er veger som er kjørbare eller ikke kjørbare med ulike typer modulvogntog. 

Anbefalingen videre her er jo å skille statistikk-behovene _(der vi må gjøre KOSTRA-type filtrering for å unngå å telle vegnett to ganger, sideanlegg etc)_ tydelig fra behovet for et datasett som har alt kjørbart vegnett (som jo _IKKE_ skal ha slik filtrering). For denne analysen her er det relevant å tilby begge deler: 
  * En komplett oversikt over navigerbart vegnett med de ulike modulvogntog-relevante datavariantene. 
  * Statistikk som er konsistent med KOSTRA-beregningen

Dette er ikke spesielt arbeidskrevende å få til.  

I tillegg må overlapp-funksjonene videreutvikles. P.t. får vi en skjevhet der det er delvis overlapp mellom et vegsegment for BK Tømmertransport og tilsvarende vegsegment for BK Modulvogntog. Problemet er at vi "mister" den biten som IKKE overlapper. Heldigvis er oppdelingen i vegsegmenter slik at man som regel enten har full overlapp eller ingen overlapp. **Men like fullt: I denne analysen så mangler totalt cirka 165km der vi IKKE overlapp**. 

