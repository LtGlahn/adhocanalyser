
import STARTHER
import pandas as pd
import nvdbapiv3
from copy import deepcopy

mittFilter = { 'kontraktsomrade' : '9303 Hardanger og Sogn 2022-2027' } # 4166256.88 m^2

# mittFilter = { 'kontraktsomrade' : '9301 Stavanger 2022-2027 (2023-)' }

# gammeltFilter = deepcopy( mittFilter )
# gammeltFilter['tidspunkt'] = '2022-09-02'
# gammelt = pd.DataFrame( nvdbapiv3.nvdbFagdata( 301, filter=gammeltFilter ).to_records( vegsegmenter=False ) )

oversett = { '1 g. pr år' : 1, '2 g. pr år' : 2, '2.hvert år' : 0.5, '3-5. hvert år' : 0.25 }

# Må skille mellom dem som har areal og dem som ikke har
temp = pd.DataFrame( nvdbapiv3.nvdbFagdata(301, filter=mittFilter ).to_records( vegsegmenter=False ) )
har_areal = temp[ ~temp['Areal'].isnull()].copy()
temp = pd.DataFrame( nvdbapiv3.nvdbFagdata(301, filter=mittFilter ).to_records( vegsegmenter=True ) )
uten_areal = temp[  temp['Areal'].isnull()].copy()
uten_areal['Areal'] = uten_areal['Klippebredde, faktisk'] * uten_areal['segmentlengde']

dagens = pd.concat( [ har_areal, uten_areal ])

dagens['Xfaktor'] = dagens['Kantklipp, anbefalt intervall'].map( oversett ).fillna( 1 )
dagens['Anbefalt årlig klippareal'] = dagens['Areal'] * dagens['Xfaktor']
print( f"\n\nDagens data: {mittFilter['kontraktsomrade']}")
print( dagens.groupby( 'Kantklipp, anbefalt intervall' ).agg( { 'Areal' : 'sum', 'Anbefalt årlig klippareal' : 'sum', 'nvdbId' : 'count'  } ) ) 

print( f"Dagens totalt anbefalt kantklippareal {dagens['Anbefalt årlig klippareal'].sum()} m^2" ) 



# gammelt['Xfaktor'] = gammelt['Kantklipp, anbefalt intervall'].map( oversett ).fillna( 1 )


# gammelt['Anbefalt årlig klippareal'] = gammelt['Areal'] * gammelt['Xfaktor']
# print( f"Data per {gammeltFilter['tidspunkt']}")
# print( gammelt.groupby( 'Kantklipp, anbefalt intervall' ).agg( { 'Areal' : 'sum', 'Anbefalt årlig klippareal' : 'sum', 'nvdbId' : 'count'  } ) )
# print( f"totalt anbefalt kantklippareal  per {gammeltFilter['tidspunkt']} {dagens['Anbefalt årlig klippareal'].sum()} m^2" ) 

# v4 = pd.read_excel( '9303-D2-V4-20220902.xlsx', sheet_name='301 - Kantklippareal', skiprows=6 )
# v4
# v4medAreal = v4[ ~V4['Areal'].isnull() ]
# v4medAreal = v4[ ~v4['Areal'].isnull() ]
# v4medAreal = v4[ ~v4['Areal'].isnull() ].copy()
# v4UtenAreal = v4[ v4['Areal'].isnull() ]
# v4medAreal
# v4UtenAreal
# v4UtenAreal[ ~v4UtenAreal['Klippebredde, faktisk'].isnull() ]
# v4UtenAreal['beregnetAreal'] = v4UtenAreal['Klippebredde, faktisk'] * v4UtenAreal['Lengde vegnett']
# v4UtenAreal = v4[ v4['Areal'].isnull() ].copy()
# v4UtenAreal['beregnetAreal'] = v4UtenAreal['Klippebredde, faktisk'] * v4UtenAreal['Lengde vegnett']
# v4UtenAreal['Xfaktor'] = v4UtenAreal['Kantklipp, anbefalt intervall'].map( oversett ).fillna( 1 )
# v4UtenAreal['Anbefalt årlig klippareal'] = v4UtenAreal['beregnetAreal'] * v4UtenAreal['Xfaktor']
# v4UtenAreal['Anbefalt årlig klippareal'].sum()
# v4medAreal = v4medAreal[ v4medAreal['Første forekomst'] == 1 ]
# v4medAreal
# v4medAreal['Xfaktor'] = v4medAreal['Kantklipp, anbefalt intervall'].map( oversett ).fillna( 1)
# v4medAreal['Anbefalt årlig klippareal'] = v4medAreal['Areal'] * v4medAreal['Xfaktor']
# v4medAreal['Anbefalt årlig klippareal'].sum()
# v4medAreal['Anbefalt årlig klippareal'].sum() + v4UtenAreal['Anbefalt årlig klippareal'].sum()
# v4UtenAreal['beregnetAreal'].sum() + v4medAreal['Areal'].sum()