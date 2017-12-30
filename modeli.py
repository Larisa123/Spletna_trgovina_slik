import sqlite3
import datetime
import csv

baza = "spletna_trgovina.db"
conn = sqlite3.connect(baza)
cur = conn.cursor()

##   UPORABNIKI:

def dodajUporabnika(ime, priimek, email, geslo):
    """ Doda uporabnika v bazo uporabnikov, v bistvo je to registracija, tako, da se
     uporabnik lahko z temi podatki potem prijavi. """
    try:
        cur.execute("""
               INSERT INTO UPORABNIK (ime, priimek, email, geslo)
               VALUES (?,?,?,?)
               """, (ime, priimek, email, geslo))
        print("Uspešno dodan uporabnik: " + ime + " " + priimek)

        conn.commit()
    except:
        print("Uporabnik z email naslovom " + email + " je že vnešen.")



def prijavaUporabnika(email, geslo):
    """ Preveri ali obstaja uporabnik z tem emailom in geslom. """
    try:
        cur.execute("""
               SELECT geslo FROM UPORABNIK
               WHERE email = ?
               """, (email, ))
        pravoGeslo = cur.fetchone()
        print(email)
        if pravoGeslo[0] == geslo:
            print("Prijava uporabnika z naslovom " + email + " uspešna.")
            return True

        conn.commit()

        print("Geslo uporabnika: " + email + " ni pravilno.")
    except:
        print("Uporabnik z email naslovom " + email + " še ni registriran.")


def uporabniki():
    """ Vrne tabelo vseh uporabnikov. """
    cur.execute("""
        SELECT * FROM UPORABNIK
        """)
    return cur.fetchall()


##   SLIKE, KOSARICA, NAKUP:

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
    if not slikaNaVoljo(slika_id):
        print("Slika " + str(slika_id) + " več ni na voljo. ")
        return

    try:
        datum_vstavljanja = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        cur.execute("""
               INSERT INTO KOSARICA (uporabnik_id, slika_id, datum_vstavljanja)
               VALUES (?,?,?)
               """, (uporabnik_id, slika_id, datum_vstavljanja))
        print("Uspešno dodana slika " + str(slika_id) + " v košarico uporabnika " + str(uporabnik_id))
        conn.commit()

        spremeniDosegljivostSlike(slika_id, False)
    except:
        print("Vnos slike v košarico ni bil uspešen.")

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
    return racun[len(racun)-1][0] # id racuna

def pretvoriKosaricoVNakup(uporabnik_id):
    try:
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

    except: print("Kosarica uporabnika " + str(uporabnik_id) + " je prazna." )

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


# VPRASANJA: Pri kosarici imamo zdaj vsak izdelek ostevilcen z ID kosarice:
# id, uporabnik_id, slika_id, datum_vstavljanja, datum_odstranitve,
# ampak ta id v resnici ni potreben, zakaj ga imamo?


# zakaj bi rabili pri slikah nakupa tudi id? vsaka slika je lahko vstavljena samo enkrat,
# tudi nakup_id je shranjen, tako da vemo, z katerim nakupom je posamezna slika povezana,
# zakaj bi imeli še tretjo številko, ki je nikjer ne uporabimo?