# Demo - datanedlasting for sykkelrute-planlegging Trondheim

Eksempler på pythonkode for å laste ned ALT av vegnettsdata. Som kjent har NVDB fått mye data for nettverk for gående og syklende.
I tillegg til  trafikantgruppe G og K har vi også veglenker uten metrering eller  trafikantgruppe, f.eks. gangfelt, trapp, Sti m.m.

Nedlastet vegnett blir også segmentert på fartsgrense.



# Installasjon

Mange av eksemplene forutsetter at dette biblioteket er tilgjengelig (installert, eller lastet ned fra github) https://github.com/LtGlahn/nvdbapi-V3, og at [pandas](https://pandas.pydata.org), [geopandas](https://geopandas.org/en/stable/) og [shapely](https://shapely.readthedocs.io/en/stable/manual.html) - bibliotekene er installert. 