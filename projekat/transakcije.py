from projekat import app
from time import sleep
from multiprocessing import Lock
from projekat.modeli import Kartica, Korisnik, Transakcije
from projekat import db



def proces_transakcije_racun(lock, korisnik_id, suma, email_primaoca, vreme_string):

    lock.acquire()

    transakcija = Transakcije(suma=suma,
                              email_primaoca=email_primaoca,
                              broj_kartice_primaoca="/",
                              vreme_transakcije=vreme_string,
                              vrsta_uplate="Uplata na racun",
                              stanje_transakcije="U OBRADI",
                              posiljalac_id=korisnik_id)

    app.app_context().push()
    db.session.add(transakcija)
    db.session.commit()
    sleep(20)
    
    kartica_uplatioca = Kartica.query.filter_by(ime_korisnika=korisnik_id).first()
    primalac = Korisnik.query.filter_by(email=transakcija.email_primaoca).first()
    primalac_kartica = Kartica.query.filter_by(ime_korisnika=primalac.id).first()
    
    if (kartica_uplatioca.uplata_online(transakcija.suma)):
      primalac_kartica.budzet += transakcija.suma
      db.session.commit()
      kartica_uplatioca.budzet -= transakcija.suma
      db.session.commit()
      transakcija.stanje_transakcije = "OBRADJENO"
      db.session.commit()
    else:
      transakcija.stanje_transakcije = "ODBIJENO"
      db.session.commit()
        
    lock.release()

def proces_transakcije_kartica(lock, korisnik_id, suma, broj_kartice_primaoca, vreme_string):

    lock.acquire()

    transakcija = Transakcije(suma=suma,
                              broj_kartice_primaoca=broj_kartice_primaoca,
                              email_primaoca = "/",
                              vreme_transakcije=vreme_string,
                              vrsta_uplate="Uplata na karticu",
                              stanje_transakcije="U OBRADI",
                              posiljalac_id=korisnik_id)

    app.app_context().push()
    db.session.add(transakcija)
    db.session.commit()
    sleep(20)

    kartica_uplatioca = Kartica.query.filter_by(ime_korisnika=korisnik_id).first()
    kartica_primaoca = Kartica.query.filter_by(broj_kartice=transakcija.broj_kartice_primaoca).first()
    
    if (kartica_uplatioca.uplata_online(transakcija.suma)):
      kartica_primaoca.budzet += transakcija.suma
      db.session.commit()
      kartica_uplatioca.budzet -= transakcija.suma
      db.session.commit()
      transakcija.stanje_transakcije = "OBRADJENO"
      db.session.commit()
    else:
      transakcija.stanje_transakcije = "ODBIJENO"
      db.session.commit()
    
    lock.release()
