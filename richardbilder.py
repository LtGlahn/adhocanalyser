"""
Foredler datadump med posisjon på vegnett for vegbilder  
"""

import pandas as pd 


if __name__ == '__main__': 
    mydf = pd.read_csv( 'JK_shortlist.csv')
    mydf.rename( columns={'Unnamed: 0' : 'OrginalIndex'}, inplace=True )    

    # Filterrer ut dem som ikke har gyldige verdier for vref eller veglenkesekvens
    mydf2 = mydf[  ~mydf['veglenkesekvens'].isnull()]
    mydf2 = mydf2[  mydf2['veglenkesekvens'] != '']
    mydf2 = mydf2[ ~mydf2['veglenkesekvens'].isnull()]
    mydf2 = mydf2[  mydf2['veglenkesekvens'] != '']

    # Vi kan ikke modifisere på en "slice" (peker tilbake til orginaldata)
    mydf2 = mydf2.copy()


    mydf2['relativpos']     = mydf2['veglenkesekvens'].apply( lambda x: float( x.split( '@')[0])  )
    mydf2['vlid']           = mydf2['veglenkesekvens'].apply( lambda x: int( x.split( '@')[1])  )

    mydf2['orginal_meter']  = mydf2['vref'].apply( lambda x : int( x.split( 'm')[-1] ) )
    mydf2['vrefstamme']     = mydf2['vref'].apply( lambda x : ' '.join( x.split( )[:-1] ) )

    # Eksempel på funksjoner som sjekker om data er gyldige før vi gjør split-operasjon 
    # mydf['vlid'] = mydf['veglenkesekvens'].apply( lambda x: int( x.split( '@')[1]) if '@' in x else None )
    # mydf['relativpos'] = mydf['veglenkesekvens'].apply( lambda x: float( x.split( '@')[0]) if '@' in x else None )