# Aplikacija za spletno trgovino

import modeli # delo z bazo
from bottle import *


class StanjeAplikacije:
    """ Se obnaša podobno kot enum v drugih jezikih - z pomočjo tega razreda nastavimo 
    stanje na eno izmed možnih vrednosti, brez da bi si morali zapomniti, katere nize
    smo uporabili za katero stanje. Po potrebi lahko stanja dodajama. """

    Domov = 1 # gumb Home - to bo privzeta vrednost
    Opis = 2 # gumb About me
    Trgovina = 3 # gumb Store
    Kosarica = 4 # gumb Basket - do tega lahko dostopamo samo v trgovini
    Racun = 5 # ko zaključimo nakup, se nam prikaže nova stran, na kateri je račun nakupa


stanjeAp = StanjeAplikacije.Domov

# Metode za prikazovanje ustreznih strani:

@get('/')
def prikaziMenuDomov():
    """ Morema napisati html """
    return template('domov.html')

def prikaziMenuOpis():
    """ Morema napisati html """
    pass

def prikaziMenuTrgovina():
    """ Morema napisati html """
    pass

def prikaziKosarico():
    """ Uporabnika napoti na novo stran, na kateri mu prikaže košarico v obliki seznama, tako da
     vidi, katere slike ima zaenkrat v njej, koliko posamezna slika stane in kakšna je vrednost
     celotnega nakupa. V kolikor se odloči za nakup, ima tukaj možnost zaključiti nakup, sicer 
     lahko nadaljuje z nakupom ali odstrani posamezne izdelke iz košarice. """
    pass

def prikaziRacun():
    pass


def nalozi():
    """ Nalozi ustrezno stran. """
    if stanjeAp == StanjeAplikacije.Domov:
        prikaziMenuDomov()
    elif stanjeAp == StanjeAplikacije.Opis:
        prikaziMenuOpis()
    elif stanjeAp == StanjeAplikacije.Trgovina:
        prikaziMenuTrgovina()
    elif stanjeAp == StanjeAplikacije.Kosarica:
        prikaziKosarico()
    elif stanjeAp == StanjeAplikacije.Racun:
        prikaziRacun()

# Pomožne metode:

def izpisiVsePodatkeTabele(tabela):
    print()
    for vrstica in tabela:
        print(vrstica)


run(host='localhost', port=8080, reloader=True)

nalozi()