import sqlite3
import datetime
import csv

baza = "spletna_trgovina.db"
conn = sqlite3.connect(baza)
cur = conn.cursor()

class Uporabnik:
    id = None
    hotel_dodati_v_kosarico = False
    prijava_neuspesna = False

##   UPORABNIKI:

def dodajUporabnika(ime, priimek, email, geslo, naslov, mesto, drzava):
    """ Doda uporabnika v bazo uporabnikov, v bistvo je to registracija, tako, da se
     uporabnik lahko z temi podatki potem prijavi. """
    try:
        cur.execute("""
               INSERT INTO UPORABNIK (ime, priimek, email, geslo, naslov, mesto, drzava)
               VALUES (?,?,?,?,?,?,?)
               """, (ime, priimek, email, geslo, naslov, mesto, drzava))
        print("Uspešno dodan uporabnik: " + ime + " " + priimek)

        conn.commit()
    except:
        print("Uporabnik z email naslovom " + email + " je že vnešen.")



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
        SELECT * FROM UPORABNIK
        """)
    return cur.fetchall()

def podatkiUporabnika(uporabnik_id):
    if uporabnik_id is None: return

    cur.execute("""
                   SELECT ime, priimek, naslov, mesto, drzava FROM UPORABNIK
                   WHERE id = (?)
                   """, (uporabnik_id, ))
    return cur.fetchone()


##   SLIKE, KOSARICA, NAKUP:

def slike():
    """ Vrne tabelo vseh slik. """
    cur.execute("""
        SELECT * FROM SLIKA
        """)
    return cur.fetchall()

def dodajSliko(naslov, vrsta, cena):
    """ Doda sliko v tabelo slik. """
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
    cur.execute("""
                   SELECT cena FROM SLIKA
                   WHERE id = (?)
                   """, (slika_id, ))
    return cur.fetchone()[0] # vrednost slike z id = slika_id

def vrednostKosarice(uporabnik_id):
    cur.execute("""
            SELECT slika_id FROM KOSARICA
            WHERE uporabnik_id = (?)
            """, (uporabnik_id, ))
    idji_slik = [tupl[0] for tupl in cur.fetchall()]

    vrednost = 0
    for slika_id in idji_slik:
        cur.execute("""
                SELECT cena FROM SLIKA
                WHERE id = (?)
                """, (slika_id,))
        vrednost +=  cur.fetchone()[0]
    return vrednost

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
           """, (1 if dosegljivost else 0, slika_id))
    conn.commit()

def dodajSlikoVKosarico(uporabnik_id, slika_id):
    """ Doda izbrano sliko v košarico izbranega uporabnika, če je slika še na voljo. """
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
    cur.execute("""
                   INSERT INTO SLIKE_NAKUPA (slika_id, nakup_id)
                   VALUES (?,?)
                   """, (slika_id, nakup_id))
    conn.commit()

def novRacun(vrednost):
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
                        INSERT INTO NAKUP (racun_id)
                        VALUES (?)
                        """, (nov_racun_id,))
    # dodajmo posamezno sliko v tabelo slike_nakupa in jih odstranimo iz kosarice:
    for slika in slike_kosarice:
        dodajSlikoNakupa(nakup_id=nov_racun_id, slika_id=slika[0])
        odstraniSlikoIzKosarice(uporabnik_id, slika[0], nakup=True)

    return nov_racun_id  # isti kot nakup_id

def odstraniSlikoIzKosarice(uporabnik_id, slika_id, nakup):
    try:
        cur.execute("""
               DELETE FROM KOSARICA 
               WHERE uporabnik_id = (?) AND slika_id = (?)
               """, (uporabnik_id, slika_id))
        conn.commit()
        print("Uspešno odstranjena slika " + str(slika_id) + " iz košarice uporabnika " + str(uporabnik_id))

        spremeniDosegljivostSlike(slika_id, True)
    except:
        print("Slike" + str(slika_id) + "sploh ni bilo v kosarici uporabnika " + str(uporabnik_id))

def prikaziKosarico(uporabnik_id=None):
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
    cur.execute("""
            SELECT slika_id FROM KOSARICA
            WHERE uporabnik_id = (?)
            """, (uporabnik_id, ))
    idji_slik = [tupl[0] for tupl in cur.fetchall()]

    relevantni_podatki = []
    for slika_id in idji_slik:
        cur.execute("""
                SELECT naslov, ime_datoteke, cena FROM SLIKA
                WHERE id = (?)
                """, (slika_id,))
        relevantni_podatki.append((slika_id, ) + cur.fetchall()[0]) # tuple (id, naslov, pot, cena)
    return relevantni_podatki

def relevantniPodatkiSlikNakupa(id_nakupa):
    cur.execute("""
                SELECT slika_id FROM SLIKE_NAKUPA
                WHERE nakup_id = (?)
                """, (id_nakupa,))
    idji_slik = [tupl[0] for tupl in cur.fetchall()]

    cur.execute("""
                SELECT datum, vrednost FROM RACUN
                WHERE id = (?)
                """, (id_nakupa, )) # id_nakupa je isti kot id_racuna
    datum, vrednost_nakupa = cur.fetchall()[0]

    podatki_o_slikah = []
    for slika_id in idji_slik:
        cur.execute("""
                SELECT naslov, ime_datoteke, vrsta, cena FROM SLIKA
                WHERE id = (?)
                """, (slika_id,))
        podatki_o_slikah.append(cur.fetchall()[0]) # tuple (naslov, pot, vrsta, cena)

    return datum, vrednost_nakupa, podatki_o_slikah



##       Sporocila

def dodajSporocilo(ime, priimek, email, sporocilo):
    cur.execute("""
                INSERT INTO SPOROCILO (ime, priimek, email, sporocilo)
                VALUES (?, ?, ?, ?)
                """, (ime, priimek, email, sporocilo))
    conn.commit()

def pridobiSporocila():
    cur.execute("""SELECT * FROM SPOROCILO""")
    return cur.fetchall()

def odstraniSporocilo(sporocilo_id):
    cur.execute("""
                   DELETE FROM SPOROCILO 
                   WHERE id = (?)
                   """, (sporocilo_id,))
    conn.commit()

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