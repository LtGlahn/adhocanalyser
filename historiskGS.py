"""
Henter historisk gang/sykkelveg data 
"""
from datetime import datetime 
import pandas as pd
import geopandas as gpd 
from shapely import wkt 

import STARTHER
import nvdbapiv3 
import nvdbgeotricks

if __name__ == '__main__': 

    # FGDB = 'historiskGS.gdb'
    # for YY in [ '2020', '2021', '2022', '2023']: 
    #     tidspunkt = YY + '-01-01'
    #     gsveg = pd.DataFrame( nvdbapiv3.nvdbVegnett( filter={'tidspunkt' : tidspunkt, 
    #                                                          'trafikantgruppe' : 'G', 
    #                                                          'veglenketype' : 'hoved,konnektering'
    #                                                          }).to_records() )

    #     gsveg = gpd.GeoDataFrame( gsveg, geometry=gsveg['geometri'].apply( wkt.loads ), crs=5973 )
    #     gsveg.to_file( FGDB, layer='TrafikantgruppeG_' + tidspunkt, driver= 'OpenFileGDB' )
        


    FGDB532 = 'historiskVegreferanse.gdb'
    mittfilter = { 'egenskap' : '4567=12159 OR 4567=12983 OR 4567=12160 OR 4567=12986'  }

    # for YY in range( 2005, 2024):
    #     tidspunkt = str(YY)+'-01-01'
    #     mittfilter['tidspunkt'] = tidspunkt

    #     data = pd.DataFrame( nvdbapiv3.nvdbFagdata( 532, filter=mittfilter ).to_records())
    #     if len( data ) > 0: 
    #         print( f"Fant {len(data)} rader med data for år {YY}")
    #         data = gpd.GeoDataFrame( data, geometry=data['geometri'].apply( wkt.loads ), crs=5973 )
    #         dropcols = ['geometri', 'vegnummer', 'vegkategori', 'fase' ]
    #         for col in dropcols: 
    #             if col in data.columns: 
    #                 data.drop( columns=col, inplace=True )
    #                 # print( f"\tFjerner kolonne {col}")
            
    #         data3D = data[  data['geometry'].has_z ]
    #         data2D = data[ ~data['geometry'].has_z ]
    #         if len( data3D ) > 0: 
    #             data3D.to_file( FGDB532, layer='GSvegfra532objekt_'+tidspunkt, driver='OpenFileGDB' )
    #         if len( data2D ) > 0: 
    #             data2D.to_file( FGDB532, layer='GSvegfra532objekt_2D'+tidspunkt, driver='OpenFileGDB' )
    #             print( f"Fant {len( data2D)} rader med 2D data for år {YY}")
    #     else: 
    #         print( f"Ingen GS-veg funnet for år {YY}")
    
    
    ## Henter dagens sykkelfelt fra NVDB 
    # FGDB_dagens = 'NVDBforGS.gdb'

    # vegsok = nvdbapiv3.nvdbVegnett( filter={ 'veglenketype' : 'hoved' })
    # sykkelfelt = []
    # for v in vegsok: 
    #     finnesSykkelfelt = [ x for x in v['feltoversikt'] if 'S' in x ]
    #     if len( finnesSykkelfelt ) > 0: 
    #         sykkelfelt.append( nvdbapiv3.flatutvegnettsegment( v ) )

    # sykkelfelt = pd.DataFrame(  sykkelfelt ) 
    # sykkelfelt = gpd.GeoDataFrame( sykkelfelt, geometry=sykkelfelt['geometri'].apply( wkt.loads ), crs=5973 )
    # sykkelfelt.to_file( FGDB_dagens, layer='sykkelfelt', driver='OpenFileGDB' )
    # # # Henter dagens GS-veg fra NVDB 
    # gsveg = pd.DataFrame( nvdbapiv3.nvdbVegnett( filter={    'trafikantgruppe' : 'G', 
    #                                                          'veglenketype' : 'hoved,konnektering'
    #                                                          }).to_records() )

    # gsveg = gpd.GeoDataFrame( gsveg, geometry=gsveg['geometri'].apply( wkt.loads ), crs=5973 )
    # gsveg.to_file( FGDB_dagens, layer='TrafikantgruppeG', driver= 'OpenFileGDB' )

    # Henter historisk sykkelfelt fra NVDB 

    t0 = datetime.now()
    # FGDB_sykkelhist = 'sykkelfelthistorisk.gdb'

    # mittfilter = { 'veglenketype' : 'hoved' }
    # # for YY in range( 2005, 2024):
    # for YY in range( 2018, 2024):
    #     tidspunkt = str(YY)+'-01-01'
    #     mittfilter['tidspunkt'] = tidspunkt

    #     print( f"Henter data for {tidspunkt}, medgått tid: {datetime.now()-t0}")

    #     vegsok = nvdbapiv3.nvdbVegnett( filter=mittfilter)
    #     sykkelfelt = []
    #     for v in vegsok: 
    #         finnesSykkelfelt = [ x for x in v['feltoversikt'] if 'S' in x ]
    #         if len( finnesSykkelfelt ) > 0: 
    #             sykkelfelt.append( nvdbapiv3.flatutvegnettsegment( v ) )

    #     if len( sykkelfelt ) > 0: 
    #         sykkelfelt = pd.DataFrame( sykkelfelt )
    #         sykkelfelt = gpd.GeoDataFrame( sykkelfelt, geometry=sykkelfelt['geometri'].apply( wkt.loads ), crs=5973 )
    #         sykkelfelt.to_file( FGDB_sykkelhist, layer='veg_m_sykkefelt_'+tidspunkt, driver='OpenFileGDB')
    #         print( f"Lagret {len(sykkelfelt)} sykkelfelt-rader for tidspunkt {tidspunkt}")
    #     else: 
    #         print( f"Fant ingen sykkelfelt-data for tidspunkt {tidspunkt}")


    # # Henter alt vegnett som ikke er for kjørende
    # FGDB_alt = 'vegnettIkkeBil.gdb'
    # vegsok = nvdbapiv3.nvdbVegnett( filter={'veglenketype' : 'hoved,konnektering'})
    # data = []
    # for v in vegsok: 
    #     v2 = nvdbapiv3.flatutvegnettsegment( v )
    #     if 'trafikantgruppe' in v2 and v2['trafikantgruppe'] == 'K': 
    #         if 'feltoversikt' in v2: 
    #             finnesSykkelfelt = [ x for x in v2['feltoversikt'] if 'S' in x ]
    #             if len( finnesSykkelfelt ) > 1:
    #                 data.append( v2 )
    #     else: 
    #         data.append( v2 )

    # ikkebil = pd.DataFrame( data )
    # ikkebil = gpd.GeoDataFrame( data, geometry=ikkebil['geometri'].apply( wkt.loads ), crs=5973 )
    # ikkebil.to_file( FGDB_alt, layer='Ikkebil', driver='OpenFileGDB' )


    print( f"Ferdig, medgått tid: {datetime.now()-t0}")


