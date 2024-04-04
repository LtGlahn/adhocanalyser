# Fattigmanns nettverksanalyse 

I stedet for en skikkelig nettverksanalyse kan man gjøre ett kall til ruteplantjenesten for hver eneste start-målpunkt 
kombinasjon i datasettet. Dette kaller vi _fattigmanns nettverksanalyse_. For så vidt en grei løsning på små datasett, men det skalerer innmari dårlig når antall start- og målpunkt vokser. 
Akkurat denne gangen her har vi valgt å kjøre analysen mot Vegvesenets testmiljø for ruteplantjenesten. Dette er ikke alltid mulig. 

### Dataprep 

Hver rad i CSV-filene `store_covenant_combinations.csv` og `store_store_combinations.csv` inneholder start- og 
målpunkt for ruteberegning. Scriptet `dataprepp.py` leser disse filene og lager en linjegeometri fra startpunkt til sluttpunkt, og konverterer til UTM sone 33 (EPSG:25833). Dernes regner vi ut avstand i luftlinje mellom start- og sluttpunkt. Til sist lagres data som separate tabeller i GIS-formatet [geopackage](https://www.geopackage.org/) i filen `luftlinje.gpkg`. 

### Ruteberegning 

For hver rad i Geopackage-filene fra dataprep-steget så gjør vi et kall til ruteplantjenesten, der koordinatene hentes fra geometrien og formuleres om til parameter `stops` i ruteplan-kallet. [API-referanse](https://www.vegvesen.no/ws/no/vegvesen/ruteplan/routingservice_v3_0/open/routingService/openapi/index.html). I tillegg bruker vi parameteren `ReturnFields=Geometry`. 

Ruteplantjenesten vil "snappe" start- og sluttpunkt til nærmeste punkt på det kjørbare vegnettet, og beregne ruten i mellom. 

Svaret fra ruteplantjenesten inneholder en liste med ett eller inntil tre ruteforslag, vi velger konsekvent det første (beste/korteste) forslaget i listen. Denne ruten har igjen en overordnet beskrivelse med statistikk og minst ett - men gjerne mange - segmenter, på formatet [gejoson](https://geojson.org/) featurecollection. Det siste objektet i samlingen er et linjeobjekt med lengde 0 og egenskapen `maneuverType=EsriDmtStop`. Dette objektet filtreres ut. De øvrige objektene slås sammen til ett sammenhengende linjeobjekt, slik at vi har ett sammenhengende geografisk objekt for hele ruten. Vi henter ut noen av egenskapene fra statistikkdelen (kjøretid, lengde ruteforslag, lengde som evt er på ferje) og lagrer objektet. 

### Feilhåndtering 

Noen steder havner start- eller sluttpunktet på en  "øy" adskilt fra det øvrige vegnettet. Dette er gjerne et lukket område (f.eks et torgområde eller serviceveger på kjøpesenter) der man har kjørbart vegnett - men publikum har ikke lov til å kjøre inn dit. Typisk står det en vegsperring eller innkjøring forbudt restriksjon som blokkerer navigasjon. 

I slike tilfeller vil ruteplantjenesten gi opp og returnere feilkode og feilmelding _Ingen rute funnet_. Jeg har valgt å inkludere disse dataene i resultatene. Man har da ingen kjøretid eller _totalLength_ egenskap. Geometrien for disse radene er luftlinje-avstand fra start til sluttpunkt. Disse bør filtreres ut i videre bearbeiding. 

Disse feilsituasjonene er også lagret som to kartlag i geopackage-filen `feilmeldinger.gpkg`. 
