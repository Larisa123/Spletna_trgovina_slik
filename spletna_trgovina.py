# Aplikacija za spletno trgovino

import modeli # delo z bazo
from bottle import *


# Metode za prikazovanje ustreznih strani:


@get('/')
def prikaziMenuDomov():
    return template('domov2.html')

@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')

@get('/static/images/<filename:path>')
def static(filename):
    return static_file(filename, root='static/images')

@get('/aboutme')
def prikaziMenuOpis():
    return template('aboutme.html')

@get('/store')
def prikaziMenuTrgovina():
    #mail = None
    #passw = None
    #return template('store.html', email=mail, password=passw)
    return template('store.html')


def prikaziKosarico():
    """ Uporabnika napoti na novo stran, na kateri mu prikaže košarico v obliki seznama, tako da
     vidi, katere slike ima zaenkrat v njej, koliko posamezna slika stane in kakšna je vrednost
     celotnega nakupa. V kolikor se odloči za nakup, ima tukaj možnost zaključiti nakup, sicer 
     lahko nadaljuje z nakupom ali odstrani posamezne izdelke iz košarice. """
    pass

def prikaziRacun():
    pass

# Pomožne metode:

def izpisiVsePodatkeTabele(tabela):
    print()
    for vrstica in tabela:
        print(vrstica)


run(host='localhost', port=8080, reloader=True)

