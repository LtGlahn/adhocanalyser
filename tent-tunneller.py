import pandas as pd
import geopandas as gpd
from shapely import wkt 

import STARTHER
import nvdbapiv3
import nvdbgeotricks


if __name__ == '__main__': 

    sok = nvdbapiv3.nvdbFagdata( 581 )
    sok.filter( {'overlapp' : '826'})
    tun = pd.DataFrame( sok.to_records())
    tun['geometry'] = tun['geometri'].apply( wkt.loads )
    tun = gpd.GeoDataFrame( tun, geometry='geometry', crs=5973 )

    sok2 = nvdbapiv3.nvdbFagdata( 67 )
    sok2.filter( {'overlapp' : '826'})
    tunlop = pd.DataFrame( sok2.to_records())
    tunlop['geometry'] = tunlop['geometri'].apply( wkt.loads )
    tunlop = gpd.GeoDataFrame( tunlop, geometry='geometry', crs=5973 )




    tuncol = [ 'objekttype', 'nvdbId',   'Navn', 'Åpningsår',  
       'vref', 'TEN-T', 'Antall parallelle hovedløp', 'kommune', 'fylke', 
       'vegkategori', 'fase', 'vegnummer', 'Lengde, offisiell', 'Eier', 'Vedlikeholdsansvarlig']

    tunlopcol = ['objekttype', 'nvdbId', 'Navn',  'vref',  'Åpningsår',
       'Lengde', 'kommune', 'fylke', 'vegkategori', 'fase',
       'vegnummer' ]

    # Sjekker TEN-T egenskapsverdi opp mot TEN-T overlapp
    sok3 = nvdbapiv3.nvdbFagdata( 581 )
    myDf = pd.DataFrame( sok3.to_records())
    tentEgenskap = myDf[ myDf['TEN-T'] == 'Ja']
    idx = list(  tentEgenskap[  ~tentEgenskap['nvdbId'].isin( list( tun['nvdbId'] ) )   ]['nvdbId'] )

    ikkeTentOverlapp = myDf[ myDf['nvdbId'].isin( idx )].copy() # 
    ikkeTentOverlapp['geometry'] = ikkeTentOverlapp['geometri'].apply( wkt.loads )
    ikkeTentOverlapp = gpd.GeoDataFrame( ikkeTentOverlapp, geometry='geometry', crs=5973)


    nvdbgeotricks.skrivexcel( 'tent-tunneller.xlsx', [ tun[tuncol], tunlop[tunlopcol], ikkeTentOverlapp[tuncol+['trafikantgruppe']] ], 
                            sheet_nameListe=['Tunnellobjekter på TEN-T', 'Tunnelløp på TEN-T', 'Ikke TENT-overlapp'],  )

    tun[ tuncol+['geometry'] ].to_file( 'tent-tunneller.gpkg', layer='tent tunneller', driver='GPKG' )
    tunlop[ tunlopcol+['geometry'] ].to_file( 'tent-tunneller.gpkg', layer='tent tunnelløp', driver='GPKG' )
    ikkeTentOverlapp[ tuncol + ['trafikantgruppe', 'geometry']].to_file( 'tent-tunneller.gpkg', layer='ikke TEN-T overlapp', driver='GPKG')

