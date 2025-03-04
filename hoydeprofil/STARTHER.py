# -*- coding: utf-8 -*-
"""
Setter opp søkestien slik at du finner NVDB-api funksjonene 
Last ned dette reposet
https://github.com/LtGlahn/nvdbapi-V3 
og hardkod inn plasseringen 

"""

import sys
import os 

if not [ k for k in sys.path if 'nvdbapi' in k]: 
    print( "Legger NVDB api til søkestien")
    sys.path.append( '/mnt/c/data/leveranser/nvdbapi-V3' )
    print( "Legger ruteplan api til søkestien")
    sys.path.append( '/mnt/c/data/leveranser/ruteplan' )


