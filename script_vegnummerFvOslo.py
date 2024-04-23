"""
Finner alle veger som burde vært fylkesveg i Oslo i hht offisielle definisjonen i 
vegobjekttype  915 Funksjonsklasse som har 
egenskapen  "Normert fylkesvegnett i Oslo" = Ja
"""

import nvdbapiv3 
import pandas as pd
from datetime import datetime

if __name__ == '__main__': 

    t0 = datetime.now()

    # Tilsvarer dette vegkart-søket etter 915 Funksjonsklasse 
    # med egenskapsfilter "Normert fylkesvegnett i Oslo" = Ja
    # https://vegkart.atlas.vegvesen.no/#kartlag:geodata/@600000,7191389,3/hva:!(filter~!(operator~**E~type*_id~12096~verdi~!21072)~id~912)~
    vegsok = nvdbapiv3.nvdbFagdata( 912, filter={'egenskap' : '12096=21072'})


    mineVegnummer = { }

    for vegobjekt in vegsok: 

        for veg in vegobjekt['vegsegmenter']: 

            if 'vegsystemreferanse' in veg and 'kortform' in veg['vegsystemreferanse']: 
                # Henter det første elementet av vegsystemreferanse, f.eks "FV3448 S1D1 m4847-4861" => "FV3348"
                vegnr = veg['vegsystemreferanse']['kortform'].split()[0]

                if not vegnr in mineVegnummer: 
                    mineVegnummer[vegnr] = { 
                                            'vegkategori' : vegnr[0], 
                                            'kommune'     : set( [ veg['kommune'] ] ), 
                                            }
                
    # Ferdig med alt vegnett, gjør om til liste med en dictionary per vegnummer
    minListe = []
    for veg in mineVegnummer.keys(): 
        minListe.append({ 
            'vegnummer'           : str( veg), 
            'vegkategori'        : mineVegnummer[veg]['vegkategori'], 
            'Antall vegnrsiffer' : len( veg ) - 2, 
            # Gjør om fra python set => liste 
            # mest for å 
            'kommune'            : sorted( list( mineVegnummer[veg]['kommune'] )) 
        })

    # Gjør om til pandas dataframe 
    vegnrDF = pd.DataFrame( minListe )
    print( f"Tidsbruk: {datetime.now()-t0}")
    vegnrDF.to_csv( 'normertFylkesvegOslo.csv', sep=';', index=False )
