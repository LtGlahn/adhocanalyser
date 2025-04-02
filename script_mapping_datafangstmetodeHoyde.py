"""
Beskriver mapping mellom målemetode og datafangstmetode  
"""
import pandas as pd 


mapping_dict = { 10: "lan", 11: "lan", 12: "lan",     13: "lan",     14: "lan",   15: "lan", 
    17: "byg",  18: "pla",   19: "ukj",  20: "fot",   21: "fot",     22: "fot",     23: "fot",     24: "fot", 
    30: "dig",     31: "dig",     32: "dig",     33: "dig",     34: "dig",     35: "dig",
    36: "gen",  37: "gen",     38: "gen",     40: "dig",  41: "dig",  42: "dig",     43: "dig",  44: "dig",     45: "dig", 
    46: "dig",  47: "dig",  48: "dig",  49: "gen",  50: "dig",  51: "dig",  52: "dig",  53: "dig",  54: "dig",  55: "dig", 
    56: "dig", 60: "gen",  61: "gen",  62: "gen",  63: "gen",  64: "gen",  65: "gen",  66: "gen",  67: "ukj",  68: "ukj", 
    69: "gen",  70: "ukj",  71: "ukj", 72: "ukj", 73: "ukj", 74: "ukj", 77: "ukj", 78: "ukj", 79: "ukj", 80: "ukj", 
    81: "ukj", 82: "ukj",  90: "lan", 91: "sat", 92: "sat", 93: "sat", 94: "sat", 95: "sat", 96: "sat", 97: "sat",  99: "ukj"  }


if __name__  == '__main__': 
    maal = pd.read_csv( 'malemetodehoyde-kode.csv' ,sep=';')
    fangst = pd.read_csv( 'datafangstmetode.csv', sep=';')

    # GJør om til liste med dictionares 
    listeMaal = maal.to_dict( orient='records')
    listefangst = fangst.to_dict( orient='records')


    resultat = []
    for myKey in mapping_dict.keys():
        res = { 'Målemetode kodeverdi' : myKey }  
        mm = [ x for x in listeMaal if x['Kodeverdi'] == myKey ]
        if len( mm ) == 1: 
            res['Målemetode Navn'] = mm[0]['Navn']
            res['Målemetode Beskrivelse'] = mm[0]['Beskrivelse']
        else: 
            print( f"SOSI målemetode kodeverdi {myKey} finnes ikke! Mappes til {mapping_dict[myKey]}")

        res['Datafangstmetode kode'] = mapping_dict[myKey]

        dfm = [ x for x in listefangst if x['Kodeverdi'] == mapping_dict[myKey]]
        res['Datafangstmetode navn'] = dfm[0]['Navn']
        res['Datafangstmetode Beskrivelse'] = dfm[0]['Beskrivelse']
        resultat.append( res )

    
    resultatDF = pd.DataFrame( resultat )

