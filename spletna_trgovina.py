# Aplikacija za spletno trgovino

import modeli # delo z bazo
from bottle import *

prijavljen_uporabnik_id = None


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

@get('/contact')
def prikaziMenuKontakt():
    return template('contact.html')

@get('/store')
def prikaziMenuTrgovina():
    """ Prikaže slike z naslovi, cenami in košaricami. """
    return template('store.html', cena_kosarice=modeli.Kosarica.Cena, slike=modeli.slike())

@get('/store/register')
def prikaziMenuRegister():
    return template('register.html')


@post('/store/register_submit')
def registracija():
    """ Vzame podatke vnešene v polja za registracijo in jih shrani v bazo. """
    name = request.forms.name
    surname = request.forms.surname
    email = request.forms.email
    password = request.forms.password

    modeli.dodajUporabnika(name, surname, email, password)
    return template('login.html')

@post('/store/add_to_basket<slika_id>')
def registracija(slika_id):
    """ Doda sliko v košarico prijavljenega uporabnika """
    modeli.dodajSlikoVKosarico(prijavljen_uporabnik_id, slika_id)
    redirect('/store')

@get('/store/login')
def prikaziMenuLogin():
    return template('login.html')

@post('/store/login_submit')
def prikaziMenuLogin():
    email = request.forms.email
    password = request.forms.password
    if modeli.prijavaUporabnika(email, password):
        prijavljen_uporabnik_id = modeli.uporabnikovId(email)
    redirect('/store') # gremo nazaj na trgovino, da lahko kupujemo - sedaj lahko dodajamo v košarico



run(host='localhost', port=8080, reloader=True)

