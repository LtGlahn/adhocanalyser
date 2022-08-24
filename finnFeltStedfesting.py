from itertools import count
import STARTHER
import nvdbapiv3 
import requests 
import pandas as pd 
import geopandas as gpd 
from shapely import wkt 

if __name__ == '__main__': 


    data = []

    sok = nvdbapiv3.nvdbFagdata(105)
    countTotal = 0
    countFound = 0 
    for obj in sok: 

        countTotal += 1 
        if countTotal % 1000 == 0: 
            print( f"Objekt nr {countTotal} ")

        # Picking out all instances where the nitty-gritty road network location details has detailed lane description in the "kjørefelt" attribute
        # obj.stedfestinger: [
        # {
        #    type: "Linje",
        #    veglenkesekvensid: 1060130,
        #    startposisjon: 0,
        #    sluttposisjon: 0.05053654,
        #    kortform: "0.0-0.05053654@1060130",
        #    kjørefelt: ["2"],
        #    retning: "MED"
        #    }
        # ],
        # https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekter/105/90832925/1.json
        # 
        # Example of where this "kjørefelt" - attribute does not contain these details: 
        # https://nvdbapiles-v3.atlas.vegvesen.no/vegobjekter/105/761141392/1.json 

        lane_specification = [ x['kjørefelt'] for x in obj['lokasjon']['stedfestinger'] if 'kjørefelt' in x and isinstance( x['kjørefelt'], list) and len( x['kjørefelt']) > 0 ]
        if len( lane_specification ) > 0 and 'geometri' in obj: 
            countFound += 1 

            if countFound == 1 or countFound % 10 == 0: 
                print( f"Fant objekt nr {countFound} med kjørefelt-spesifikk stedfesting")

            # our variable `lane_specification` is a list of lists, something like [ ['2'] ] or [ ['2'],  ['2', '4K'] ]
            # Transforming into a comma separated text string and appending to the properties of the feature
            temp_lanespeclist = ['#'.join( x ) for x in lane_specification ] # Now it's a list of strings, like ['2'] or [ '2', '2#4K']
            newProperty = { 'id'        : -99, 
                            'navn'      : 'Lane codes',
                            'datatype'  : 'Tekst', 
                            'egenskapstype' : 'tekst',
                            'verdi'     : ','.join( temp_lanespeclist )  # Something like [ '2,2#4K']. 
                          }
            obj['egenskaper'].append( newProperty )

            data.append( obj )
    print( f"Ferdig med for-løkke, fant {countFound} av {countTotal} med kjørefelt-spesifikk stedfesting")
    mydf = pd.DataFrame( nvdbapiv3.nvdbfagdata2records( data   ))
    mydf['geometry'] = mydf['geometri'].apply( wkt.loads )
    myGdf = gpd.GeoDataFrame( mydf, geometry='geometry', crs=5973)
    myGdf.to_file( 'fartsgrensedebug.gpkg', layer='feltstedfesting', driver='GPKG')


    