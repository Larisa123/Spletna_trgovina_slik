import sqlite3
import datetime
import csv

baza = "spletna_trgovina.db"
conn = sqlite3.connect(baza)
cur = conn.cursor()

##  Hranitev informacij trenutnega uporabnika:

class Uporabnik:
    """ Če te informacije shranjujemo samo kot globalno spremenljivko, se sproti brišejo.
        Tako se pa ne. """
    id = None
    hotel_dodati_v_kosarico = False # če je uporabnik hotel dodati sliko v košarico, pa še ni bil registiran, bo to True
    registracija_uspesna = None # če nismo ravno po registraciji (na login strani), naj bo ta spremenljivka None
    prijava_neuspesna = False # če se je poskusil prijaviti in prijava ni bila uspešna

##   UPORABNIKI:

def dodajUporabnika(ime, priimek, email, geslo, naslov, mesto, drzava):
    """ Doda uporabnika v bazo uporabnikov. V bistvo je to registracija, tako, da se
     uporabnik lahko z temi podatki potem prijavi. 
     Nastavi Uporabnik.registracija_uspesna na True ali False, da lahko uporabniku sporočimo, 
     če je registracija bila uspešna ali ne. """
    try:
        cur.execute("""
               INSERT INTO UPORABNIK (ime, priimek, email, geslo, naslov, mesto, drzava)
               VALUES (?,?,?,?,?,?,?)
               """, (ime, priimek, email, geslo, naslov, mesto, drzava))
        print("Uspešno dodan uporabnik: " + ime + " " + priimek)

        conn.commit()
        Uporabnik.registracija_uspesna = True
    except:
        Uporabnik.registracija_uspesna = False



def prijavaUporabnika(email, geslo):
    """ Preveri ali obstaja uporabnik z tem emailom in geslom in vrne ustrezno logično vrednost. """
    try:
        cur.execute("""
               SELECT geslo FROM UPORABNIK
               WHERE email = ?
               """, (email, ))
        pravoGeslo = cur.fetchone()
        if pravoGeslo[0] == geslo:
            print("Prijava uporabnika z naslovom " + email + " uspešna.")
            return True

        conn.commit()

        print("Geslo uporabnika: " + email + " ni pravilno.")
        return False
    except:
        print("Uporabnik z email naslovom " + email + " še ni registriran.")
        return False

def uporabnikovId(email):
    cur.execute("""
                   SELECT id FROM UPORABNIK
                   WHERE email = ?
                   """, (email,))
    return cur.fetchone()[0]


def uporabniki():
    """ Vrne tabelo vseh uporabnikov. """
    cur.execute("""
        SELECT id, ime, priimek, naslov, mesto, drzava FROM UPORABNIK
        """)
    return cur.fetchall()

def podatkiUporabnika(uporabnik_id):
    """ Vrne podatke uporabnika z id = uporabnik_id. """
    if uporabnik_id is None: return

    cur.execute("""
                   SELECT ime, priimek, naslov, mesto, drzava FROM UPORABNIK
                   WHERE id = (?)
                   """, (uporabnik_id, ))
    return cur.fetchone()


##   SLIKE, KOSARICA, NAKUP:

def slike():
    """ Vrne tabelo vseh slik in njihovih podatkov. """
    cur.execute("""
        SELECT * FROM SLIKA
        """)
    return cur.fetchall()

def dodajSliko(naslov, vrsta, cena):
    """ Doda sliko v tabelo slik. Funkcije v spletni trgovini ne uporabljamo,
        slike so vnešene že v bazi, to smo delali v konzolni spletni trgovini. """
    try:
        dosegljivost = True # če jo vnesemo, je dosegljiva
        cur.execute("""
               INSERT INTO SLIKA (dosegljivost, naslov, vrsta, cena)
               VALUES (?,?,?,?)
               """, (dosegljivost, naslov, vrsta, cena))
        print("Uspešno dodana slika: " + naslov)

        conn.commit()
    except:
        print("Slika z naslovom " + naslov + " je že vnešena.")

def vrednostSlike(slika_id):
    """ Vrne vrednost oz. ceno slike z id = slika_id. """
    cur.execute("""
                   SELECT cena FROM SLIKA
                   WHERE id = (?)
                   """, (slika_id, ))
    return cur.fetchone()[0] # vrednost slike z id = slika_id

def vrednostKosarice(uporabnik_id):
    """ Vrne trenutno vrednost košarice uporabnika z id = uporabnik_id. """

    # INNER JOIN rabimo, ker želimo samo cene od slik, ki so dejansko v košarici uporabnika, z navadnim JOIN-om bi dobili vse
    cur.execute("""
                    SELECT cena FROM KOSARICA
                    INNER JOIN SLIKA ON KOSARICA.slika_id=SLIKA.id
                    WHERE KOSARICA.uporabnik_id = (?)
                    """, (uporabnik_id, ))
    # dobimo rezultat [(72.0,), (135.0,),...], rezultat je vsota prvih vrednosti:
    vsota = sum([dvojica[0] for dvojica in cur.fetchall()])

    return vsota

def slikaNaVoljo(slika_id):
    """ Vrne logično vrednost, ki nam pove, ali je slika z id = slika_id še na voljo. """
    cur.execute("""
                   SELECT dosegljivost FROM SLIKA
                   WHERE id = (?)
                   """, (slika_id, ))
    return cur.fetchone()[0] # dosegljivost slike z id = slika_id

def spremeniDosegljivostSlike(slika_id, dosegljivost):
    cur.execute("""
           UPDATE SLIKA
           SET dosegljivost = (?)
           WHERE id =  (?)
           """, (1 if dosegljivost else 0, slika_id)) # z true/false so bli neki problemi, z 0/1 pa dela, zato sma pustile tak
    conn.commit()

def dodajSlikoVKosarico(uporabnik_id, slika_id):
    """ Doda izbrano sliko v košarico izbranega uporabnika, če je slika še na voljo. 
        print stavka sta bila samo v pomoč preden smo imeli spletno trgovino, sedaj do napake niti
        ne bi smelo priti, razen če je problem z brskalnikom ali kaj takega, nad čem nimama nadzora. """
    try:
        datum_vstavljanja = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        cur.execute("""
               INSERT INTO KOSARICA (uporabnik_id, slika_id, datum_vstavljanja)
               VALUES (?,?,?)
               """, (uporabnik_id, slika_id, datum_vstavljanja))
        conn.commit()

        spremeniDosegljivostSlike(slika_id, False)
        print("Uspešno dodana slika " + str(slika_id) + " v košarico uporabnika " + str(uporabnik_id))
    except:
        print("Vnos slike " + str(slika_id) + " v košarico uporabnika " + str(uporabnik_id) + " ni bil uspešen.")

def dodajSlikoNakupa(nakup_id, slika_id):
    """ Ko imamo nakup, hranimo tam id uporabnika in id računa, slik, ki smo jih kupili, pa ne hranimo ne v računu, ne v nakupu.
        Te hranimo v posebni tabeli SLIKE_NAKUPA, do katere lahko dostopamo preko id-ja nakupa.
        Ta funkcija za id = nakup_id doda sliko, ki smo jo kupili pri tem nakupu v tabelo SLIKE_NAKUPA. """
    cur.execute("""
                   INSERT INTO SLIKE_NAKUPA (slika_id, nakup_id)
                   VALUES (?,?)
                   """, (slika_id, nakup_id))
    conn.commit()

def novRacun(vrednost):
    """ Ustvarimo nov račun vrednosti vrednost in vrnemo njegov id. """
    placan = False
    datum = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    cur.execute("""
                INSERT INTO RACUN (placan, datum, vrednost)
                VALUES (?,?,?)
                """, (placan, datum, vrednost))
    cur.execute("""
                SELECT id FROM RACUN 
                """)
    racun = cur.fetchall()
    return racun[len(racun)-1][0] # zadnji id racuna - to je id tega racuna

def pretvoriKosaricoVNakup(uporabnik_id):
    """ Pretvori košarico prijavljenega uporabnika v nakup. To pomeni, da ustvari nov nakup, shrani slike kot slike nakupa
        in jih odstrani iz košarice. Če ni prijavljenega uporabnika, ne naredi nič. """

    if uporabnik_id is None:
        return
    # POVEZAVA JE TAKA: nakup -> (racun, slike_nakupa -> slike)
    # zato moramo najprej narediti racun, nakup, potem pa slike nakupa, ker ta rabi id od nakupa,
    #
    # najprej poglej katere slike so v kosarici tega uporabnika:
    cur.execute("""
                        SELECT slika_id FROM KOSARICA
                        WHERE uporabnik_id = (?)
                        """, (uporabnik_id,))

    slike_kosarice = cur.fetchall()  # slike imamo
    vrednosti = [vrednostSlike(slika[0]) for slika in slike_kosarice]

    # ustvarimo nov racun in nakup (racun prej, ker rabi nakup tudi id od racuna):
    nov_racun_id = novRacun(vrednost=sum(vrednosti))
    cur.execute("""
                        INSERT INTO NAKUP (racun_id, uporabnik_id)
                        VALUES (?, ?)
                        """, (nov_racun_id, uporabnik_id))
    # dodajmo posamezno sliko v tabelo slike_nakupa in jih odstranimo iz kosarice:
    for slika in slike_kosarice:
        dodajSlikoNakupa(nakup_id=nov_racun_id, slika_id=slika[0])
        odstraniSlikoIzKosarice(uporabnik_id, slika[0], nakup=True)

    return nov_racun_id  # isti kot nakup_id

def odstraniSlikoIzKosarice(uporabnik_id, slika_id, nakup):
    """ Odstrani sliko iz košarice uporabnika. """
    try:
        cur.execute("""
               DELETE FROM KOSARICA 
               WHERE uporabnik_id = (?) AND slika_id = (?)
               """, (uporabnik_id, slika_id))
        conn.commit()
        print("Uspešno odstranjena slika " + str(slika_id) + " iz košarice uporabnika " + str(uporabnik_id))

        spremeniDosegljivostSlike(slika_id, not nakup) # dosegljivost je true, če ne kupujemo, false, če smo kupili
    except:
        print("Slike" + str(slika_id) + "sploh ni bilo v kosarici uporabnika " + str(uporabnik_id))

def prikaziKosarico(uporabnik_id=None):
    """ Funkcija za v pomoč pri iskanju napak - izpiše košarico izbranega uporabnika, če uporabnika ne izberemo,
        pa kar od vseh uporabnikov. """
    if uporabnik_id:
        cur.execute("""
            SELECT * FROM KOSARICA
            WHERE uporabnik_id = (?)
            """, (uporabnik_id, ))
    else:
        cur.execute("""
            SELECT * FROM KOSARICA
            """)
    return cur.fetchall()

def relevantniPodatkiSlikKosarice(uporabnik_id):
    """ Vrne relevantne podatke slik za prikaz v spletni trgovini. Ti so: id, naslov, pot, cena. """

    cur.execute("""
                SELECT SLIKA.id, naslov, ime_datoteke, cena FROM KOSARICA
                INNER JOIN SLIKA ON KOSARICA.slika_id=SLIKA.id
                WHERE KOSARICA.uporabnik_id = (?)
                """, (uporabnik_id,))
    # vrne [(7, 'Flowers', 'rozice', 72.0), ...]
    return cur.fetchall()

def relevantniPodatkiSlikNakupa(id_nakupa):
    """ Vrne relevantne podatke slik za prikaz na računu. 
    Ti so: datum, vrednost_nakupa in za vse slike: id, naslov, pot, vrsta, cena."""


    # najprej pridobimo datum in vrednost nakupa iz računa:
    cur.execute("""
                    SELECT datum, vrednost FROM RACUN
                    WHERE id = (?)
                    """, (id_nakupa,))  # id_nakupa je isti kot id_racuna
    datum, vrednost_nakupa = cur.fetchall()[0]

    # podatki o slikah nakupa:
    cur.execute("""
                SELECT SLIKA.id, naslov, ime_datoteke, vrsta, cena FROM SLIKE_NAKUPA
                INNER JOIN SLIKA ON SLIKA.id=SLIKE_NAKUPA.slika_id
                WHERE SLIKE_NAKUPA.nakup_id = (?)
                """, (id_nakupa,))

    # na koncu vrnemo v naslednji obliki:
    # ('2018-01-14 22:04', 207.0, [(14, 'Cows, Haloze', 'krave3', 72.0), ...])
    return datum, vrednost_nakupa, cur.fetchall()

def pretekliNakupi():
    """ Vrne vse relevantne podatke vseh opravljenih nakupov. To gledamo na /admin strani. """
    cur.execute("""
                SELECT racun_id, datum, ime, priimek, vrednost FROM NAKUP
                JOIN RACUN ON NAKUP.racun_id=RACUN.id
                JOIN UPORABNIK ON NAKUP.uporabnik_id=UPORABNIK.id
                """) # id_nakupa je isti kot id_racuna
    return cur.fetchall()


##       Sporocila

def dodajSporocilo(ime, priimek, email, sporocilo):
    """ Dodamo sporočilo v bazo, po tem ko uporabim izpolni obrazec na /contactme. """
    cur.execute("""
                INSERT INTO SPOROCILO (ime, priimek, email, sporocilo)
                VALUES (?, ?, ?, ?)
                """, (ime, priimek, email, sporocilo))
    conn.commit()

def pridobiSporocila():
    """ Vrne vsa sporočila. Za izpis na /admin strani. """
    cur.execute("""SELECT * FROM SPOROCILO""")
    return cur.fetchall()

def odstraniSporocilo(sporocilo_id):
    """ Odstrani izbrano sporočilo. Do tega imamo dostop na /admin strani (z klikom na gumb z slikico koša). """
    cur.execute("""
                   DELETE FROM SPOROCILO 
                   WHERE id = (?)
                   """, (sporocilo_id,))
    conn.commit()

""" Izpisovanje, brisanje """

def izpisiVsePodatkeTabele(tabela):
    print()
    for vrstica in tabela:
        print(vrstica)

def izbrisiVsePodatke(imeTabele):
    cur.execute("""
                DELETE * FROM (?)
                """, (imeTabele,))
    conn.commit()

# VPRASANJA: Pri kosarici imamo zdaj vsak izdelek ostevilcen z ID kosarice:
# id, uporabnik_id, slika_id, datum_vstavljanja, datum_odstranitve,
# ampak ta id v resnici ni potreben, zakaj ga imamo?


# zakaj bi rabili pri slikah nakupa tudi id? vsaka slika je lahko vstavljena samo enkrat,
# tudi nakup_id je shranjen, tako da vemo, z katerim nakupom je posamezna slika povezana,
# zakaj bi imeli še tretjo številko, ki je nikjer ne uporabimo?