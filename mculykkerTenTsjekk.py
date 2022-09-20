# Sjekker datasett med MC-ulykker i tunnell på TEN-T vegnettet for 2020 og 2021 (regneark fra Thea)

import pandas as pd

import STARTHER
import nvdbapiv3
import nvdbgeotricks


def fiksdato( x ):
    """
    Omarbeider datoer på formatet '13.07.2020' => ISO format '2020-07-13' 
    """
    tmp = x.split( '.')
    tmp.reverse()
    return '-'.join( tmp )


if __name__ == '__main__': 

    # Henter trafikkulykker innafor tunnelløp 
    sok = nvdbapiv3.nvdbFagdata( 570 )
    sok.filter( {'vegsystemreferanse' : 'Ev,Rv' })
    sok.filter( {'overlapp' : '67'  } )
    mydf = pd.DataFrame( sok.to_records() )

    # Filtrerer, kun ulykker fra 2020 og 2021 
    mydf['UdatoTall'] = mydf['Ulykkesdato'].apply( lambda x : int(  x.replace( '-', '' )  ) )

    alleTunnellUlykker = mydf[ mydf['UdatoTall'] > 20191231 ]

    # Henter ulykker på TEN-T vegnettet
    sok = nvdbapiv3.nvdbFagdata( 570 )
    sok.filter( {'overlapp' : '826'  } )
    alleTenT = pd.DataFrame( sok.to_records())

    # Kombinerer slik at vi får ulykker innafor tunnelløp på TEN-T vegnettet 
    tenTNvdbId = alleTenT[['nvdbId']]
    joined = pd.merge( tenTNvdbId, alleTunnellUlykker, how='inner', on='nvdbId')
    joined['Veg'] = joined['vref'].apply( lambda x : x.split()[0] )

    # Leser Thea sine data
    thea = pd.read_excel( 'Personskadeulykker i tunnel TENT 20202021_291376582.xlsx' )
    # Knar om datoformat 
    thea['Ulykkesdato'] = thea['Dato'].apply( fiksdato )

    joined2 = pd.merge( thea, joined, on=['Veg', 'Ulykkesdato'], how='inner' )

    # Liste med dem som er i Thea sitt datasett, men ikke i mitt
    thea[ ~thea['UID'].isin( list( joined2['UID'] ))]

    # Skriver excel-rapport 
    nvdbgeotricks.skrivexcel( 'MCulykkersjekk.xlsx',  thea[ ~thea['UID'].isin( list( joined2['UID'] ))] )