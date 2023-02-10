"""
Splitter uhåndterlige multippel-stedfesting objekt i mer håndterbare biter 
 
Tar (liste med) objektID og lager endringssett der spagettimonster-objekt får en mer fornuftig oppdeling, f.eks samme vegnummer
"""
from copy import deepcopy 

import pandas as pd
import geopandas as gpd 
from shapely import wkt 

import STARTHER 
import nvdbapiv3
import skrivnvdb

import pdb 
def df2veglenkepos( mindf, col_vlenk='veglenkesekvensid', col_start='startposisjon', col_slutt='sluttposisjon' ): 
    """
    Lager stedfestingselement for skriving til NVDB ut fra DataFrame 
    """

    assert isinstance( mindf,  gpd.geodataframe.GeoDataFrame ) or isinstance( mindf, pd.core.frame.DataFrame ), "Input data må være en dataframe"
    assert col_vlenk in mindf and col_start in mindf and col_slutt in mindf, f"Finner ikke standardkolonner {[col_vlenk,col_start,col_slutt]} i dataframe, angi eksplisitt navn for kolonner med veglenkesekvensid, start- og sluttposisjno"
    mal = { 'linje' : [ ] }

    for vlenk in mindf[col_vlenk].unique(): 
        A = mindf[ mindf[col_vlenk] == vlenk ].sort_values( by=col_start ) 

        tempStart = A.iloc[0][col_start]
        tempSlutt = A.iloc[0][col_slutt]
        for junk, row in A.iterrows(): 
            if row[col_start] > tempSlutt: 
                mal['linje'].append(  { 'veglenkesekvensNvdbId' : int( vlenk), 'fra' : tempStart, 'til' : tempSlutt } )
                tempStart = row[col_start]
                tempSlutt = row[col_slutt]

            elif row[col_slutt] > tempSlutt: 
                tempSlutt = row[col_slutt]

        mal['linje'].append(  { 'veglenkesekvensNvdbId' : int( vlenk ), 'fra' : tempStart, 'til' : tempSlutt } )


    return mal 

# Sjekk veglenkesekvens 121755 

if __name__ == '__main__': 
    endreDisse = [ 1016497070,     # Normaltransport 
                1016495424,  # Tømmertransport 
                1016496222,  # Spesialtransport 
                779619604,   # Normal uoff
                1015223762,  # Tømmer uoff
                779578871  ]  # Spesial uoff 


    skrivemal = None 

    forb = nvdbapiv3.apiforbindelse()
    # if not forb.+
    forb.login( miljo='prodles')
    count = -100
    for minId in endreDisse: 
        obj = forb.finnid( minId, kunfagdata=True )
        data = pd.DataFrame( nvdbapiv3.nvdbfagdata2records( obj ))

        data['vegnummer'] = data['vref'].apply( lambda x : x.split()[0] )
        data['strekningsnummer'] = data['vref'].apply( lambda x : int( x.split()[1].split('D')[0][1:] ) )
        data['delstrekningsnummer'] = data['vref'].apply( lambda x : int( x.split()[1].split('D')[1] ))
        data['vegnr-strekning'] =  data['vref'].apply( lambda x : x.split()[0] +  ' ' + str( x.split()[1].split('D')[0].lower()  ) )

        # lokasjon = skrivnvdb.lokasjon2skriv( [x for x in obj['egenskaper'] if x['navn'] == 'Liste av lokasjonsattributt' ][0] )

        denneObjType = skrivnvdb.fagdata2skrivemal( obj , operasjon='registrer'  )


        for strnr in data['vegnr-strekning'].unique(): 
            count = count -1 
            egensk =  deepcopy( denneObjType['registrer']['vegobjekter'][0])
            egensk['stedfesting']  = df2veglenkepos( data[ data['vegnr-strekning'] == strnr ])
            egensk['tempId'] = count

            if isinstance  (skrivemal, dict ):
                skrivemal['registrer']['vegobjekter'].append( egensk )
            else:
                skrivemal = denneObjType
                skrivemal['registrer']['vegobjekter'] = [ egensk ]
            # endringssett.append( egensk )
