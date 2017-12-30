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
    niz = 'store.html'
    slike = modeli.slike()
    niz += "number_of_images={}".format(len(slike))
    #mail = None
    #passw = None
    #return template('store.html', email=mail, password=passw)


    return template('store.html', number_of_images=3, image_name="krave_haloze", image_title="Haloze", image_price=30)

@get('/contact')
def prikaziMenuKontakt():
    return template('contact.html')

@get('/store/register')
def prikaziMenuRegister():
    return template('register.html')


@post('/store/register_submit')
def formhandler():
    """ Vzame podatke vnešene v polja za registracijo in jih shrani v bazo. """
    name = request.forms.name
    surname = request.forms.surname
    email = request.forms.email
    password = request.forms.password

    modeli.dodajUporabnika(name, surname, email, password)
    return template('login.html')

@get('/store/login')
def prikaziMenuLogin():
    return template('login.html')

@post('/store/login_submit')
def prikaziMenuLogin():
    email = request.forms.email
    password = request.forms.password
    modeli.prijavaUporabnika(email, password)
    redirect('/store') # gremo nazaj na trgovino, da lahko kupujemo - sedaj lahko dodajamo v košarico


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

