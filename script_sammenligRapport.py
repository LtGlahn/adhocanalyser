"""
Sammenligner min rekursive datadump (søk på elektriske anlegg langs Fv130 på kontraktsomrdet 30-103 Østfold Sør 2022-2028 )
med relasjonstrerapport for samme søkefiltre 
"""

import pandas as pd 

if __name__ == '__main__': 

    mittfilter = {'kontraktsomrade' : '30-103 Østfold Sør 2022-2028', 'vegsystemreferanse' : 'FV130' }

    rapportfil = 'relasjonseksempel_rapportgenerator.xlsx'
    minFil = 'relasjonseksempelQA.xlsx'

    qadata = pd.read_excel( minFil )

    ff = pd.ExcelFile( rapportfil )
    tempDf = []
    for ark in ff.sheet_names: 
        if ark != 'Oversikt': 
            mydf = pd.read_excel( rapportfil, sheet_name=ark, skiprows=6 )
            mydf['relasjonstype'] = ark
            tempDf.append( mydf[['Objekt Id', 'relasjonstype', 'Vegsystemreferanse'] ] )

    rapportDf = pd.concat( tempDf, ignore_index=True )


    
    # Tar det (nesten) for gitt at rapporten inneholder alt som mitt QA datasett 
    junk = rapportDf[ ~rapportDf['Objekt Id'].isin( qadata['nvdbId'] ) ]
    if len( junk ) > 0:
        print( f"ALARM - har vi rett datasett?? Fant {len(junk)} objekter i rapportgenerator som IKKE finnes i mitt kontrolldatasett! ")

    ekstra = qadata[ ~qadata['nvdbId'].isin( rapportDf['Objekt Id'] ) ]

    print( f"Totalt {len(ekstra)} objekt som ideelt sett skulle vært med i rapportgenerator, sjekker nå hvor mange som er utafor filteret mitt: {mittfilter}")

    # sjekk_kontraktsområde 
    ekstra_komr = ekstra[ ekstra['kontraktsomrader'].str.contains( mittfilter['kontraktsomrade'] ) ]
    print( f"{len(ekstra)-len(ekstra_komr)} objekt faller vekk når vi kun tar med dem som har kontraktområde {mittfilter['kontraktsomrade']}")

    # sjekk vegsystereferanse 
    ekstra_vref = ekstra[ ekstra['vref'].str.contains( mittfilter['vegsystemreferanse'] ) ]
    print( f"{len(ekstra)-len(ekstra_vref)} objekt faller vekk når vi kun tar med dem som har vegsystemreferanse {mittfilter['vegsystemreferanse']}")

    # Sjekker begge deler 
    ekstra_filtrert = ekstra_komr[ ekstra_komr['vref'].str.contains( mittfilter['vegsystemreferanse'] )]

    print( f"Står igjen med {len(ekstra_filtrert)} objekter som ikke er med i relasjonstrerapporten og som matcher søkefilter {mittfilter}")
