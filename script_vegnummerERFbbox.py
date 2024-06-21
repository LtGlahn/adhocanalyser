"""
Finner alle vegnummer på ERF-veg (innafor fylke eller kommune). 
Slår sammen geometri og finner BBox 
"""
import STARTHER
import nvdbapiv3 
import pandas as pd
import geopandas as gpd 
from shapely import from_wkt, simplify
from datetime import datetime

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

if __name__ == '__main__': 

    t0 = datetime.now()

    mineVegnummer = { }
    vegsok = nvdbapiv3.nvdbVegnett( filter={'vegsystemreferanse' : 'Ev,Rv,Fv', 'trafikantgruppe' : 'K', 
                                            'sideanlegg' : False, 'detaljniva' : 'VT,VTKB', 'fylke' : 3 })


    myDf = pd.DataFrame( vegsok.to_records() )
    myGdf = gpd.GeoDataFrame( myDf, geometry=myDf['geometri'].apply( from_wkt ), crs=5973) 
    myGdf['vegnr'] = myGdf['vegsystemreferanse'].apply( lambda x : x['kortform'].split()[0] )



    # Forenkler geometri, med ulik toleranse tilpasset forskjellige zoomlevels. 
    # Må bli litt prøving og feiling for å komme i mål her. 
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

    gpkgfil = 'vegnummerdemo.gpkg'
    vegnr_orginal.to_file( gpkgfil, layer='Vegnummer orginal oppløsning', driver='GPKG' )
    vegnr_perfylke_3m.to_file( gpkgfil, layer='Vegnummer 3m toleranse', driver='GPKG' )
    vegnr_perfylke_25m.to_file( gpkgfil, layer='Vegnummer 25m toleranse', driver='GPKG' )



