# Aplikacija za spletno trgovino

import modeli # delo z bazo
from bottle import *

# Metode za prikazovanje ustreznih strani:

class PoslanoSporocilo:
    stanje = None


@get('/')
def prikaziMenuDomov():
    return template('domov2.html')

@get('/admin')
def prikaziPodatkeZaAdmina():
    return template('admin.html', sporocila=modeli.pridobiSporocila())

@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')

@get('/static/images/<filename:path>')
def static(filename):
    return static_file(filename, root='static/images')

@get('/static/fonts/<filename:path>')
def static(filename):
    return static_file(filename, root='static/fonts')

@get('/aboutme')
def prikaziMenuOpis():
    return template('aboutme.html')

@get('/contact')
def prikaziMenuKontakt():
    smo_poslali = PoslanoSporocilo.stanje
    PoslanoSporocilo.stanje = None
    return template('contact.html', message_sent=smo_poslali)

@get('/store')
def prikaziMenuTrgovina():
    """ Prikaže slike z naslovi, cenami in košaricami. """
    uporabnik = modeli.Uporabnik.id
    prikazi_sporocilo = modeli.Uporabnik.hotel_dodati_v_kosarico
    modeli.Uporabnik.hotel_dodati_v_kosarico = False # da mu ne bo zdaj vsakič pokazalo tega sporocila
    return template('store.html', uporabnik=uporabnik, cena_kosarice=modeli.vrednostKosarice(uporabnik), slike=modeli.slike(), show_alert=prikazi_sporocilo)

@get('/store/register')
def prikaziMenuRegister():
    return template('register.html')


@get('/basket')
def prikaziKosaricoUporabnika():
    uporabnik = modeli.Uporabnik.id
    podatki = modeli.relevantniPodatkiSlikKosarice(uporabnik)
    return template('basket.html', relevantni_podatki_slik_kosarice=podatki, cena_kosarice=modeli.vrednostKosarice(uporabnik))

@get('/basket/invoice')
def prikaziRacun():
    """ Prikaze racun na podlagi košarice prijavljenega uporabnika. """
    uporabnik = modeli.Uporabnik.id
    podatki = modeli.relevantniPodatkiSlikKosarice(uporabnik)
    return template('invoice.html', relevantni_podatki_slik_kosarice=podatki, cena_kosarice=modeli.vrednostKosarice(uporabnik))


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
def dodajVKosarico(slika_id):
    """ Doda sliko v košarico prijavljenega uporabnika """
    if modeli.Uporabnik.id is not None:
        modeli.dodajSlikoVKosarico(modeli.Uporabnik.id, slika_id)
        # to informacijo rabimo, da lahko uporabniku prikazemo sporocilo,
        # da more biti prijavljen za dodajanje v kosarico
    else:
        modeli.Uporabnik.hotel_dodati_v_kosarico = True
    redirect('/store')

@post('/basket/remove_painting<slika_id>')
def odstraniIzKosarice(slika_id):
    """ Doda sliko v košarico prijavljenega uporabnika """
    modeli.odstraniSlikoIzKosarice(modeli.Uporabnik.id, slika_id)
    redirect('/basket')

@get('/store/login')
def prikaziMenuLogin():
    neuspesnost = modeli.Uporabnik.prijava_neuspesna
    modeli.Uporabnik.prijava_neuspesna = False # da se ne bo pri naslednji prijavi spet pokazalo sporocilo o neuspesnosti
    return template('login.html', previous_login_failed=neuspesnost)

@post('/store/login_submit')
def prikaziMenuLogin():
    email = request.forms.email
    password = request.forms.password
    if modeli.prijavaUporabnika(email, password):
        modeli.Uporabnik.id = modeli.uporabnikovId(email)
        redirect('/store')  # gremo nazaj na trgovino, da lahko kupujemo - sedaj lahko dodajamo v košarico
    else: # prijava neuspesna - prikazati se mora sporocilo!
        modeli.Uporabnik.prijava_neuspesna = True
        redirect('/store/login') # prikazimo sporocilo in se naj poskusi prijaviti ponovno


@post('/store/contact_submit')
def dodajSporocilo():
    ime = request.forms.ime
    priimek = request.forms.priimek
    email = request.forms.email
    sporocilo = request.forms.sporocilo
    modeli.dodajSporocilo(ime, priimek, email, sporocilo)
    PoslanoSporocilo.stanje = True
    redirect('/contact')


@post('/basket/remove_message<sporocilo_id>')
def odstraniSporocilo(sporocilo_id):
    """ Doda sliko v košarico prijavljenega uporabnika """
    modeli.odstraniSporocilo(sporocilo_id)
    redirect('/admin')


run(host='localhost', port=8080)

