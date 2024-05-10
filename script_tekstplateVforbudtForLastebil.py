"""

"""
import pandas as pd
import sqlite3


import STARTHER
import nvdbapiv3 
import nvdbgeotricks


if __name__ == '__main__': 
    sok = nvdbapiv3.nvdbFagdata(96)
    sok.filter( {'egenskap' : '(5530=7654)' })
    # sok.filter( { 'kommune' : 5047 })
    data = []
    for skilt in sok: 
        skiltdata = nvdbapiv3.nvdbfagdata2records( skilt, relasjoner=False )[0]
        if 'relasjoner' in skilt and 'foreldre' in skilt['relasjoner']: 
            morobjektID = skilt['relasjoner']['foreldre'][0]['vegobjekter'][0]
            mor = nvdbapiv3.finnid(  morobjektID, kunfagdata=True )
            if 'relasjoner' in mor and 'barn' in mor['relasjoner']: 
                for relasjon in mor['relasjoner']['barn']: 
                    if relasjon['id'] == 200004: 
                        count = 0
                        for barnId in relasjon['vegobjekter']: 
                            if barnId == skilt['id']: 
                                pass 
                            else: 
                                barn = nvdbapiv3.finnid( barnId, kunfagdata=True )
                                barneliste = nvdbapiv3.nvdbfagdata2records( barn, relasjoner=False )
                                if len( barneliste ) > 0: 
                                    barn = barneliste[0]
                                count += 1

                                if 'Skiltnummer' in barn: 
                                    skiltdata['skiltnummer_underskilt' + str( count+1 )] = barn['Skiltnummer']

                                else: 
                                    skiltdata['skiltnummer_underskilt' + str( count+1 )] = 'Mangler skiltnummer'
        data.append( skiltdata)

    mydf = pd.DataFrame( data )

    # Henter bruksklasse-data som overlapper med skiltpunktene våre
    bkDF = pd.DataFrame( nvdbapiv3.nvdbFagdata( 904, filter={'overlapp' : '96(egenskap(5530)=7654)' } ).to_records() )
    bkDF = bkDF[['Bruksklasse', 'veglenkesekvensid', 'startposisjon', 'sluttposisjon' ]]
    # Merger basert på veglenkeposisjon 
    qry = ( f"SELECT * from skilt\n" 
            f"LEFT JOIN B on skilt.veglenkesekvensid = B.veglenkesekvensid\n"
            f"AND skilt.relativPosisjon >= B.startposisjon\n"
            f"AND skilt.relativPosisjon < B.sluttposisjon"
            )
    # TODO: Masser litt på egenskapsnavn slik at veglenkesekvensid ikke kommer som to identiske kolonner   

    conn = sqlite3.connect( ':memory' )
    mydf.to_sql( 'skilt', conn, index=False )
    bkDF.to_sql( 'B', conn, index=False )
    leftjoin = pd.read_sql_query( qry, conn )

    cols = ['nvdbId', 'Skiltnummer',
        'veglenkesekvensid', 'relativPosisjon',
       'kommune', 'fylke', 'vref', 'vegkategori',  'trafikantgruppe',
        'geometri',
        'Bruksklasse',
       'skiltnummer_underskilt2',
       'skiltnummer_underskilt3', 'skiltnummer_underskilt4',
       'skiltnummer_underskilt5', 
       'skiltnummer_underskilt6', 'vegkart' ] 
    
    # TODO: Må knote litt med veglenkesekvensid, som kommer TO ganger
    # TODO: Dynamisk håndtering av skiltnummer_underskilt<løpenummer>  