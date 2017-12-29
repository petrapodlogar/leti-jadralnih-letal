import csv
import json
import os
import re
import requests
import string


letalisca = [
    'LESCE1', 'PTUJM1', 'CELJE1', 'NOVOM1',
    'POSTO1', 'MARIB1', 'SLOVE1', 'MURSK1',
    'BOVEC1', 'AJDOV1', 'VELEN1', 'CERKL1'
    ]



re_bloka_leta = re.compile(
    r'<tr class="(odd|even)">.*?<\/tr>', flags=re.DOTALL
    )

re_podatkov_leta = re.compile(
    # datum
    r'<td class="ttop">'
    r'(?P<leto>\d{4})-(?P<mesec>\d{2})-(?P<dan>\d{2})'
    r'.*?'
    # tocke
    r'<td>.*?'
    r'(?P<tocke>\d+,\d+)'
    r'.*?'
    # ime
    r'<a.*?href="flightbook\.html\?sp=2017&amp;st=olcp&amp;rt=olc&amp;pi=\d+">.*?'
    r'(?P<ime>\w.*?)'
    r'\('
    # drzava
    r'(?P<drzava>.*?)'
    r'\)'
    r'.*?'
    # dolzina
    r'<td>.*?'
    r'(?P<dolzina>[0-9]+,[0-9]+)'
    r'.*?'
    # hitrost
    r'<td>.*?'
    r'(?P<hitrost>[0-9]+,[0-9]+)'
    r'.*?'
    # klub
    r'<td class="ttop">'
    r'(?P<klub>.*?)'
    r'<.*?'
    # letalo
    r'<td class="ttop">'
    r'(?P<letalo>.*?)'
    r'<.*?'
    # vzlet
    r'<td class="ttop">.*?'
    r'(?P<vzlet>\d+:\d+)'
    r'.*?'
    # pristanek
    r'<td class="ttop">.*?'
    r'(?P<pristanek>\d+:\d+)'
    r'.*?',
    flags=re.DOTALL
    )



#stevilo_najdenih = 0
#for ujemanje in re_podatkov_leta.finditer(vsebina_strani):
#    print(ujemanje.groupdict())
#    stevilo_najdenih += 1
#print(stevilo_najdenih)



def v_float(n):
    nov_n = ''
    for i in range(len(n)):
        if n[i] == ',':
            nov_n += '.'
        else:
            nov_n += n[i]
    return float(nov_n)

def v_datum(dan, mesec, leto):
    return str(dan) + '.' + str(mesec) + '.' + str(leto)

def velike_zacetnice(niz):
    return string.capwords(niz)

def spremeni_ime_letalisca(letalisce):
    ime = letalisce[10:16]
    dobra_imena = ['Lesce Bled', 'Ptuj Moškanjci', 'Celje', 'Novo Mesto',
                   'Postojna', 'Maribor', 'Slovenj Gradec', 'Murska Sobota',
                   'Bovec', 'Ajdovščina', 'Velenje Lajše', 'Cerklje']
    i = letalisca.index(ime)
    return dobra_imena[i]



def podatki_leta(blok_leta, ime_letalisca):
    ujemanje = re_podatkov_leta.search(blok_leta)
    if ujemanje:
        let = ujemanje.groupdict()
        let['tocke'] = v_float(let['tocke'])
        let['dolzina'] = v_float(let['dolzina'])
        let['hitrost'] = v_float(let['hitrost'])
        let['ime'] = velike_zacetnice(let['ime'])
        let['letalisce'] = spremeni_ime_letalisca(ime_letalisca)
        let['datum'] = v_datum(let['dan'], let['mesec'], let['leto'])
        return let
    else:
        print('ENEGA LETA PA NE ZNAM PREBRATI')
        print(blok_leta)
    


def shrani_lete_v_imenik(imenik):
    os.makedirs(imenik, exist_ok=True)
    for letalisce in letalisca:
        naslov_strani = (
            'https://www.onlinecontest.org/olc-2.0/gliding/flightsOfAirfield.html'
            '?sc=&aa={}&st=olcp&rt=olc&c=SI&olcdecorate=plain&olcdecorate=plain'
            '&olcdecorate=plain&olcdecorate=plain&d-2348235-p=&sp=2017&paging=100000'
        ).format(letalisce)
        stran = requests.get(naslov_strani)
        ime_datoteke = 'letalisce-{}.html'.format(letalisce)
        polna_pot_datoteke = os.path.join(imenik, ime_datoteke)
        with open(polna_pot_datoteke, 'w', encoding='utf-8') as datoteka:
            datoteka.write(stran.text)



def preberi_lete_v_imeniku(imenik):
    leti = []
    for ime_datoteke in os.listdir(imenik):
        ime_letalisca = ime_datoteke
        polna_pot_datoteke = os.path.join(imenik, ime_datoteke)
        with open(polna_pot_datoteke) as datoteka:
            vsebina_datoteke = datoteka.read()
            for blok_leta in re_bloka_leta.finditer(vsebina_datoteke):
                leti.append(podatki_leta(blok_leta.group(0), ime_letalisca))
    return leti



def zapisi_json(podatki, ime_datoteke):
    with open(ime_datoteke, 'w') as datoteka:
        json.dump(podatki, datoteka, indent=2)



def zapisi_csv(podatki, polja, ime_datoteke):
    with open(ime_datoteke, 'w') as datoteka:
        pisalec = csv.DictWriter(datoteka, polja, extrasaction='ignore')
        pisalec.writeheader()
        for podatek in podatki:
            pisalec.writerow(podatek)



#  shrani_lete_v_imenik('leti_2017')

leti = preberi_lete_v_imeniku('leti_2017')


zapisi_json(leti, 'leti_2017.json')
polja = [
    'datum', 'tocke', 'ime', 'drzava', 'dolzina', 'hitrost',
    'klub', 'letalo', 'vzlet', 'pristanek', 'letalisce'
]

zapisi_csv(leti, polja, 'leti_2017.csv')


            

