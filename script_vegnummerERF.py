"""
Finner alle veger som burde vært fylkesveg i Oslo i hht offisielle definisjonen i 
vegobjekttype  915 Funksjonsklasse som har 
egenskapen  "Normert fylkesvegnett i Oslo" = Ja
"""
import STARTHER
import nvdbapiv3 
import pandas as pd
from datetime import datetime

if __name__ == '__main__': 

    t0 = datetime.now()

    mineVegnummer = { }

    vegsok = nvdbapiv3.nvdbVegnett( filter={'vegsystemreferanse' : 'Ev,Rv,Fv', 'trafikantgruppe' : 'K'})

    for veg in vegsok: 

        vegnr = veg['vegsystemreferanse']['kortform'].split()[0]
        if vegnr in mineVegnummer: 
            mineVegnummer[vegnr]['kommune'].add( veg['kommune'])
            mineVegnummer[vegnr]['fylke'].add(   veg['fylke']  )
        else: 
            mineVegnummer[vegnr] = { 
                                    'vegkategori' : vegnr[0], 
                                    'kommune'     : set( [ veg['kommune'] ] ), 
                                    'fylke'       : set( [ veg['fylke'] ] )
                                    }
                
    # Ferdig med alt vegnett, gjør om til liste med en dictionary per vegnummer
    minListe = []
    for veg in mineVegnummer.keys(): 
        minListe.append({ 
            'vegnummer'           : str( veg), 
            'vegkategori'        : mineVegnummer[veg]['vegkategori'], 
            'Antall vegnrsiffer' : len( veg ) - 2, 
            'Antall fylker'      : len( list( mineVegnummer[veg]['fylke']   )),
            'Antall kommuner'    : len( list( mineVegnummer[veg]['kommune'] )),
            # Gjør om fra python set => liste 
            'fylke'              : sorted( list( mineVegnummer[veg]['fylke']    )), 
            'kommune'            : sorted( list( mineVegnummer[veg]['kommune'] )) 
        })

    # Gjør om til pandas dataframe 
    vegnrDF = pd.DataFrame( minListe )
    print( f"Tidsbruk: {datetime.now()-t0}")
    vegnrDF.to_csv( 'vegnummer.csv', sep=';', index=False )
