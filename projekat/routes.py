from datetime import datetime
from projekat import app, db
from projekat.forme import RegisterForm, LoginForm, IzmenaForm, VerifikacijaForm, OnlineUplataForm, KonvertovanjeForm, TransakcijeKarticaForm, TransakcijeRacunForm
from projekat.modeli import Korisnik, Kartica, RealTimeCurrencyConverter, Stanja, Transakcije
from projekat.transakcije import proces_transakcije_racun, proces_transakcije_kartica
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.sql import text, select
from multiprocessing import Process, Lock

lock = Lock()

@app.route('/')
@app.route('/pocetna')
def pocetna():
    return render_template('base.html')

@app.route('/registracija', methods=['GET', 'POST'])
def registracija():
    forma = RegisterForm()
    if forma.validate_on_submit():
        korisnik = Korisnik(ime=forma.ime.data,
                              prezime=forma.prezime.data,
                              adresa=forma.adresa.data,
                              grad=forma.grad.data,
                              drzava=forma.drzava.data,
                              broj_telefona=forma.broj_telefona.data,
                              email=forma.email.data,
                              lozinka=forma.lozinka1.data)
        db.session.add(korisnik)
        db.session.commit()
        flash(f"Nalog uspesno kreiran.", category="success")
        return redirect(url_for('pocetna'))
    if forma.errors != {}: 
        for err_msg in forma.errors.values():
            flash(f'Desila se greška prilikom registracije: {err_msg}', category='danger')
    return render_template('registracija.html', forma=forma)
    
@app.route('/prijava', methods=['GET', 'POST'])
def prijava():
    forma = LoginForm()
    if forma.validate_on_submit():
        korisnik = Korisnik.query.filter_by(email=forma.email.data).first()
        if korisnik and Korisnik.query.filter_by(lozinka=forma.lozinka.data).first():
            login_user(korisnik)
            flash(f'Uspešno ste se prijavili.', category='success')
            return redirect(url_for('prikaz_profila'))
        else:
            flash('Email i lozinka se ne poklapaju. Pokušajte ponovo.', category='danger')
    return render_template('prijava.html', forma=forma)

@app.route('/odjava')
def odjava():
    logout_user()
    flash("Uspešno ste se odjavili.", category='info')
    return redirect(url_for('pocetna'))

@app.route('/profil', methods=['GET', 'POST'])
@login_required
def prikaz_profila():
    return render_template('profil.html')

@app.route('/izmena/<int:id>', methods=['GET', 'POST'])
@login_required
def izmena_podataka(id):
    form = IzmenaForm()
    korisnik_izmena = Korisnik.query.get_or_404(id)
    if request.method == "POST":
        korisnik_izmena.ime = request.form['ime']
        korisnik_izmena.prezime = request.form['prezime']
        korisnik_izmena.adresa = request.form['adresa']
        korisnik_izmena.grad = request.form['grad']
        korisnik_izmena.drzava = request.form['drzava']
        korisnik_izmena.broj_telefona = request.form['broj_telefona']
        korisnik_izmena.email = request.form['email']
        if form.validate_on_submit():
            db.session.commit()
            flash("Podaci uspešno izmenjeni.", category='success')
            return redirect(url_for('prikaz_profila'))
        else:
            flash("Izmena podataka neuspešna.", category="danger")
    return render_template('izmena.html', form=form, korisnik_izmena=korisnik_izmena)

@app.route('/verifikacija/<int:id>', methods=['GET', 'POST'])
@login_required
def verifikacija(id):
    forma = VerifikacijaForm()
    korisnik_verifikacija = Korisnik.query.get_or_404(id)
    if request.method == "POST":
        if forma.validate_on_submit():
            if(forma.broj_kartice.data.isnumeric() and forma.sigurnosni_kod.data.isnumeric() and korisnik_verifikacija.provera_datuma(forma.datum_isteka_kartice.data)):
                kartica = Kartica(broj_kartice=forma.broj_kartice.data,
                                    datum_isteka_kartice=forma.datum_isteka_kartice.data,
                                    sigurnosni_kod=forma.sigurnosni_kod.data,
                                    budzet=1000,
                                    ime_korisnika=korisnik_verifikacija.id)
                db.session.add(kartica)
                db.session.commit()
                url = 'https://api.exchangerate-api.com/v4/latest/RSD'
                converter = RealTimeCurrencyConverter(url)
                dolar_u_dinarima = converter.convert('USD', 'RSD', 1)
                korisnik_verifikacija.verifikovan = True
                kartica.budzet -= dolar_u_dinarima
                db.session.commit()
                flash("Nalog uspešno verifikovan.", category='success')
                return redirect(url_for('prikaz_profila'))
            else:
                flash('Unesite validne parametre za verifikaciju.', category='danger')
        else:
            flash("Greška prilikom verifikacije.", category='danger')
    return render_template('verifikacija.html', forma=forma, korisnik_verifikacija = korisnik_verifikacija)

@app.route('/pregled/<int:id>', methods=["GET", "POST"], defaults={'valuta1' : None, 'valuta2' : None, 'iznos' : None })
@app.route('/pregled/<int:id>/<valuta1>/<valuta2>/<float:iznos>', methods=["GET", "POST"])
@login_required
def pregled_stanja(id, valuta1, valuta2, iznos):
    korisnik = Korisnik.query.get_or_404(id)
    if valuta1 != None:
        stanje_za_konverziju = Stanja.query.filter_by(ime_korisnika=korisnik.id, valuta=valuta2).first()
        if stanje_za_konverziju == None:
                stanje_za_konverziju = Stanja(valuta=valuta2,
                                    vrednost=0,
                                    ime_korisnika=korisnik.id)
                db.session.add(stanje_za_konverziju)
                db.session.commit()      
        staro_stanje = Stanja.query.filter_by(ime_korisnika=korisnik.id, valuta=valuta1).first()
        url = 'https://api.exchangerate-api.com/v4/latest/' + valuta1
        converter = RealTimeCurrencyConverter(url)
        nova_vrednost = converter.convert(valuta1, valuta2, iznos)
        stanje_za_konverziju.vrednost += nova_vrednost
        staro_stanje.vrednost -= iznos
        db.session.commit()
    stanje = Stanja.query.filter_by(ime_korisnika=korisnik.id).all()
    return render_template('pregled.html', stanja=stanje, korisnik=korisnik)

@app.route('/konverzija/<int:id>/<valuta>', methods=["GET", "POST"])
@login_required
def konverzija(id, valuta):
    korisnik = Korisnik.query.get_or_404(id)
    #stanje = Stanja.query.filter_by(ime_korisnika=korisnik.id).first()
    url = 'https://api.exchangerate-api.com/v4/latest/' + valuta
    converter = RealTimeCurrencyConverter(url)
    valute = converter.get_valute()
    return render_template('konverzija.html', korisnik=korisnik, valute=valute, valuta=valuta)

@app.route('/konvertovanje/<int:id>/<valuta>/<valuta2>', methods=["GET", "POST"])
@login_required
def konvertovanje(id, valuta, valuta2):
    forma = KonvertovanjeForm()
    korisnik = Korisnik.query.get_or_404(id)
    stanje = Stanja.query.filter_by(ime_korisnika=korisnik.id, valuta=valuta).first()
    if request.method == "POST":
        if forma.validate_on_submit():
            iznos=forma.iznos.data
            if iznos < 0:
                flash(f'Unesite ispravan iznos.', category='danger')
                return render_template('konvertovanje.html', forma=forma, korisnik=korisnik)
            if stanje.vrednost >= iznos:
                return redirect(url_for('pregled_stanja', id=korisnik.id, valuta1=valuta, valuta2=valuta2, iznos=iznos))
            else:
                flash(f'Nemate dovoljno sredstava u {stanje.valuta}', category='danger')
        else:
            flash(f'Unesite iznos za konverziju', category='danger')
    return render_template('konvertovanje.html', forma=forma, korisnik=korisnik)
    
@app.route('/online_uplata/<int:id>', methods=["GET", "POST"])
@login_required
def online_uplata(id):
    forma = OnlineUplataForm()
    korisnik = Korisnik.query.get_or_404(id)
    kartica = Kartica.query.filter_by(ime_korisnika=korisnik.id).first()
    if request.method == "POST":
        if forma.validate_on_submit():
            stanje_dinari = Stanja.query.filter_by(ime_korisnika=korisnik.id, valuta='RSD').first()
            if stanje_dinari == None:
                stanje_dinari = Stanja(valuta='RSD',
                                vrednost=0,
                                ime_korisnika=korisnik.id)
                db.session.add(stanje_dinari)
                db.session.commit()
            if kartica.uplata_online(forma.iznos.data):
                stanje_dinari.vrednost += forma.iznos.data
                db.session.commit()
                kartica.budzet -= forma.iznos.data
                db.session.commit()
                return redirect(url_for('prikaz_profila'))
            else:
                flash('Nemoguća transakcija. Nemate dovoljno sredstava na računu.', category='danger')        
        else:
            flash('Unesite pravilan iznos.', category='danger')
    return render_template('online_uplata.html', forma=forma, korisnik=korisnik)

@app.route('/transakcije', methods=["GET", "POST"])
@login_required
def transakcije():
    korisnik = current_user

    return render_template('transakcije.html', korisnik=korisnik)

@app.route('/transakcije_kartica', methods=["GET", "POST"])
@login_required
def transakcije_kartica():
    korisnik = current_user
    kartica_uplatioca = Kartica.query.filter_by(ime_korisnika=korisnik.id).first()
    forma = TransakcijeKarticaForm()
    if request.method == "POST":
        if forma.validate_on_submit():
            if forma.suma.data < 0:
                flash(f'Unesite ispravan iznos.', category='danger')
                return redirect(url_for('transakcije_kartica'))
            if forma.broj_kartice_primaoca.data == kartica_uplatioca.broj_kartice:
                flash(f'Ne možete samome sebi uplatiti novac.', category='danger')
                return redirect(url_for('transakcije_kartica')) 
            kartica_primaoca = Kartica.query.filter_by(broj_kartice=forma.broj_kartice_primaoca.data).first()
            if kartica_primaoca == None:
                flash(f'Ne postoji kartica sa unesenim brojem kartice', category='danger')
                return redirect(url_for('transakcije_kartica'))                 

            vreme = datetime.now()
            vreme_string = vreme.strftime("%H:%M:%S")
            process = Process(target=proces_transakcije_kartica, args=[lock, korisnik.id, forma.suma.data, forma.broj_kartice_primaoca.data, vreme_string])
            process.start()
            return redirect(url_for('transakcije'))
        else:
            flash('Unesite pravilan iznos i broj kartice.', category='danger')

    return render_template('transakcije_kartica.html', forma=forma)

@app.route('/transakcije_racun', methods=["GET", "POST"])
@login_required
def transakcije_racun():
    korisnik = current_user
    forma = TransakcijeRacunForm()
    if request.method == "POST":
        if forma.validate_on_submit():
            if forma.suma.data < 0:
                flash(f'Unesite ispravan iznos.', category='danger')
                return redirect(url_for('transakcije_racun'))
            if forma.email_primaoca.data == korisnik.email:
                flash(f'Ne možete samome sebi uplatiti novac.', category='danger')
                return redirect(url_for('transakcije_racun'))
            primalac = Korisnik.query.filter_by(email=forma.email_primaoca.data).first()
            if primalac == None:
                flash(f'Ne postoji korisnik sa tom e-mail adresom.', category='danger')
                return redirect(url_for('transakcije_racun'))                   

            vreme = datetime.now()
            vreme_string = vreme.strftime("%H:%M:%S")
            process = Process(target=proces_transakcije_racun, args=[lock, korisnik.id, forma.suma.data, forma.email_primaoca.data, vreme_string])
            process.start()
            return redirect(url_for('transakcije'))
        else:
            flash('Unesite pravilan iznos i e-mail primaoca.', category='danger')

    return render_template('transakcije_racun.html', forma=forma)
