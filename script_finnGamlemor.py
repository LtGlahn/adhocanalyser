"""
Finner historiske mødre

Steg 1: Finn objekter som har to (evt flere) mødre 
Steg 2A): Sjekk om noen av disse mødrene har sluttdato 
Steg 2B): Hvis mor-objektet ikke er historisk: Sjekk at relasjonen finnes på den versjonen som er aktiv i dag
"""

import STARTHER
import nvdbapiv3

sok = nvdbapiv3.nvdbFagdata( 14)

data = []
for t in sok:
    if 'relasjoner' in t and 'foreldre' in t['relasjoner']:
        if len( t['relasjoner']['foreldre'][0]['vegobjekter'] ) > 1:
            vref = t['vegsegmenter'][0]['vegsystemreferanse']['kortform']
            for mamma in t['relasjoner']['foreldre'][0]['vegobjekter']: 
                a = nvdbapiv3.finnid( mamma, kunfagdata=True )
                retval = { 'nvdbId' : t['id'], 'morId' : a['id'], 'morType' : a['metadata']['type']['navn'], 'vref' : vref  }
                if 'sluttdato' in a['metadata']:
                    retval['info'] = 'Mor-objekt historisk'
                    data.append(  retval  )
                elif not 'barn' in a['relasjoner'] or t['id'] not in [y  for x in a['relasjoner']['barn'] for y in x['vegobjekter'] ]: 
                    # https://stackoverflow.com/questions/952914/how-do-i-make-a-flat-list-out-of-a-list-of-lists
                    retval['info'] = 'Mor-objekt gyldig, men har IKKE mor->datter relasjon til vårt objekt'
                    data.append( retval )

