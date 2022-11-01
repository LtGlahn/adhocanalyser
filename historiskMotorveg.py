from re import sub
import pandas as pd
import geopandas as gpd
from shapely import wkt

import STARTHER 
import nvdbapiv3
# import skrivdataframe 
import nvdbgeotricks 

if __name__ == '__main__': 

    gpkgfil = 'historisk-Motorveg.gpkg'


    data = { }
    resultat = []
    # for tidspunkt in [ '2014-12-31', '2020-12-31' ]:
    for tidspunkt in [ '2014-12-31', '2015-12-31', '2016-12-31', '2017-12-31', '2018-12-31', '2019-12-31', '2020-12-31', '2021-12-31', '2022-09-23'  ]:

        print( f"Analyserer {tidspunkt} ")
        # Henter motorveg 
        mittfilter = { 'tidspunkt' : tidspunkt }
        sok = nvdbapiv3.nvdbFagdata( 595 )
        sok.filter( mittfilter )
        motor = pd.DataFrame( sok.to_records( vegsegmenter=True))

        # Fjerner konnekteringslenker 
        motor = motor[motor['veglenkeType'] == 'HOVED' ].copy()
        data[tidspunkt] = motor 

        mittResultat = { 'tidspunkt' : tidspunkt, 
                        'Lengde Motorveg+Motortrafikkveg'   : round(motor['segmentlengde'].sum() / 1000),
                        'Lengde Motorveg'                   : round(motor[ motor['Motorvegtype'] == 'Motortrafikkveg' ]['segmentlengde'].sum() / 1000), 
                        'Lengde Motortrafikkveg'            : round(motor[ motor['Motorvegtype'] == 'Motorveg' ]['segmentlengde'].sum() / 1000) }



        motor['geometry'] = motor['geometri'].apply( wkt.loads )
        motor = gpd.GeoDataFrame( motor, geometry='geometry', crs=5973 )
        motor.to_file( gpkgfil, layer='motorveg'+tidspunkt, driver='GPKG')

        if 'adskilte_lop' in motor.columns: 

            motor = motor[ motor['adskilte_lop'] != 'Mot'  ]

            # Ett objekt (14 segmenter) mangler vegreferansedata 2019-data
            feilvegref = motor[ motor['vref'].isnull()]
            if len( feilvegref) > 0: 
                print( f"FEILER {tidspunkt}- mangler vegreferanseverdi for {round(feilvegref['segmentlengde'].sum())} meter motorveg")
                feilvegref.to_file( gpkgfil, layer='manglerVREF'+tidspunkt, driver='GPKG')
            motor = motor[ ~motor['vref'].isnull()]

            # Filtrerer sideanlegg
            motor = motor[ ~motor['vref'].str.contains('SD')]

            # Filtrerer vekk kryssdeler som ikke er rundkjøringer
            motor = motor[ ( ~motor['vref'].str.contains('KD')) | (motor['typeVeg'] == 'Rundkjøring' ) ]

            mittResultat['Lengde m filter MT+MTV']  = round(motor['segmentlengde'].sum() / 1000)
            mittResultat['Lengde m filter MT']      = round(motor[ motor['Motorvegtype'] == 'Motorveg' ]['segmentlengde'].sum() / 1000)
            mittResultat['Lengde m filter MTV']     = round(motor[ motor['Motorvegtype'] == 'Motortrafikkveg' ]['segmentlengde'].sum() / 1000)

            if len( motor) > 0: 
                motor.to_file( gpkgfil, layer='motorvegFILTRERT'+tidspunkt, driver='GPKG')

        resultat.append( mittResultat )

    res = pd.DataFrame( resultat )
    # skrivdataframe.skrivdf2xlsx( res, 'historiskMotorveg.xlsx' )
    nvdbgeotricks.skrivexcel( 'historiskMotorveg.xlsx', res  )