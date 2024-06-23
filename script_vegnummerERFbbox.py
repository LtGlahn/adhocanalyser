"""
Finner alle vegnummer på ERF-veg (innafor fylke eller kommune). 
Slår sammen geometri og finner BBox 
"""
from pathlib import Path
import pandas as pd
from copy import deepcopy 

import geopandas as gpd 
from shapely import from_wkt, simplify
from datetime import datetime

import STARTHER
import nvdbapiv3 

def datamassasje( minGDF:gpd.GeoDataFrame ): 
    """
    Legger på boundinbBox og et par andre egenskaper og endrer koordinatsystem til WGS84 
    """
    minGDF['vegkategori'] = minGDF['vegnr'].apply( lambda x : x[0])
    minGDF['Antall siffer'] = minGDF['vegnr'].apply( lambda x : len(x) - 2)
    minGDF = minGDF.to_crs( 4623 )
    minGDF['bbox'] = minGDF['geometry'].apply( lambda x: x.bounds )
    # Runder av til grei presisjon, ref https://xkcd.com/2170/
    minGDF['bbox'] =minGDF['bbox'].apply( lambda x: ','.join( [ str( round( y, 4)) for y in x ] ) )

    return minGDF

def lagre2geojson( mydata:gpd.GeoDataFrame, mappenavn:str ): 
    """
    lagrer som en individuell geojson fil per fylke og vegnummer 
    """
    t0 = datetime.now()
    # sikrer at endringene på geodataframe ikke påvirker orginaldataene 
    minGDF = deepcopy( mydata )
    print( f"Lagrer data til mappe {mappenavn}")

    if not 'fylke' in minGDF.columns: 
        minGDF['fylke'] = 'heleNorge'
    for fylke in minGDF['fylke'].unique(): 
        fylkeGDF = minGDF[ minGDF['fylke'] == fylke ]
        for vegnr in fylkeGDF['vegnr'].unique(): 
            outdir =  mappenavn + '/' + str( fylke ) 
            Path( outdir ).mkdir( parents=True, exist_ok=True ) 
            etVegnr = fylkeGDF[ fylkeGDF['vegnr'] == vegnr ] 
            etVegnr.to_file( outdir + '/fylke' + str(fylke) + vegnr + '.geojson',  driver="GeoJSON" )


    print( f"Tidsbruk lagring {mappenavn}: {datetime.now()-t0}")


    # from IPython import embed; embed()

if __name__ == '__main__': 

    t00 = datetime.now()

    mineVegnummer = { }
    vegsok = nvdbapiv3.nvdbVegnett( filter={'vegsystemreferanse' : 'Ev,Rv,Fv', 'trafikantgruppe' : 'K', 
                                            'sideanlegg' : False, 'detaljniva' : 'VT,VTKB' }) #, 'fylke' : 3 })


    myDf = pd.DataFrame( vegsok.to_records() )
    t1 = datetime.now(); print( f"Tid for datanedlasting: {t1-t00}")
    myGdf = gpd.GeoDataFrame( myDf, geometry=myDf['geometri'].apply( from_wkt ), crs=5973) 
    myGdf['vegnr'] = myGdf['vegsystemreferanse'].apply( lambda x : x['kortform'].split()[0] )

    # Forenkler geometri, med ulik toleranse tilpasset forskjellige zoomlevels. 
    # Må bli litt prøving og feiling for å finne riktig kompromiss mellom dataminimering og pen opptegning 
    myGdf_3m = myGdf.copy()
    myGdf_25m = myGdf.copy()
    myGdf_3m['geometry']  = myGdf_3m['geometry'].apply(  lambda x: simplify( x, tolerance=3))
    myGdf_25m['geometry'] = myGdf_25m['geometry'].apply( lambda x: simplify( x, tolerance=25))

    vegnr_perfylke_25m   = datamassasje( myGdf_25m[['vegnr', 'fylke', 'geometry']].dissolve( by=['fylke', 'vegnr']).reset_index() ) 
    vegnr_helelandet_25m = datamassasje( myGdf_25m[['vegnr',          'geometry']].dissolve( by=['vegnr']).reset_index() )

    vegnr_perfylke_3m   = datamassasje( myGdf_3m[['vegnr', 'fylke', 'geometry']].dissolve( by=['fylke', 'vegnr']).reset_index() )
    vegnr_helelandet_3m = datamassasje( myGdf_3m[['vegnr',          'geometry']].dissolve( by=['vegnr']).reset_index() )

    # Orginaloppløsning for å ha et sammenligningsgrunnlag
    vegnr_orginal        = datamassasje( myGdf[['vegnr',          'geometry']].dissolve( by=['vegnr']).reset_index() )

    # Lagrer CSV 
    cols = list( vegnr_perfylke_25m.columns)
    cols.remove( 'geometry')
    vegnr_perfylke_25m[cols].to_csv( 'vegnummerdemo_perfylke.csv', sep=';' )
    cols.remove( 'fylke')
    vegnr_helelandet_25m[cols].to_csv( 'vegnummerdemo_helelandet.csv', sep=';' )

    t2 = datetime.now(); print( f"Tid for data bearbeiding: {t2-t1}")

    gpkgfil = 'vegnummerdemo.gpkg'
    vegnr_orginal.to_file( gpkgfil, layer='Vegnummer orginal oppløsning', driver='GPKG' )
    vegnr_perfylke_3m.to_file( gpkgfil, layer='Vegnummer 3m toleranse', driver='GPKG' )
    vegnr_perfylke_25m.to_file( gpkgfil, layer='Vegnummer 25m toleranse', driver='GPKG' )

    t3 = datetime.now(); print( f"Tid for lagring til geopackage: {t3-t2}")


    lagre2geojson( vegnr_orginal, 'geojson_orginalOppløsning' )
    lagre2geojson( vegnr_perfylke_3m, 'geojson_3m' )
    lagre2geojson( vegnr_helelandet_3m, 'geojson_3m' )
    lagre2geojson( vegnr_perfylke_25m, 'geojson_25m' )
    lagre2geojson( vegnr_helelandet_25m, 'geojson_25m' )

    t4 = datetime.now(); print( f"Tid for lagring til geojson: {t4-t3}")
    print( f"Kjøretid totalt: {datetime.now()-t00}")
