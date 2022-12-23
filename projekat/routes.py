from projekat import app, db
from projekat.forme import RegisterForm, LoginForm, IzmenaForm, VerifikacijaForm
from projekat.modeli import Korisnik, Kartica
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.sql import text, select

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
            flash("Podaci uspesno izmenjeni.", category='success')
            return redirect(url_for('prikaz_profila'))
        else:
            flash("Izmena podataka neuspesna", category="danger")
    return render_template('izmena.html', form=form, korisnik_izmena=korisnik_izmena)

@app.route('/verifikacija/<int:id>', methods=['GET', 'POST'])
@login_required
def verifikacija(id):
    forma = VerifikacijaForm()
    korisnik_verifikacija = Korisnik.query.get_or_404(id)
    if request.method == "POST":
        if forma.validate_on_submit():
            kartica = Kartica(broj_kartice=forma.broj_kartice.data,
                                datum_isteka_kartice=forma.datum_isteka_kartice.data,
                                sigurnosni_kod=forma.sigurnosni_kod.data,
                                budzet=1000,
                                ime_korisnika=korisnik_verifikacija.id)
            db.session.add(kartica)
            db.session.commit()
            korisnik_verifikacija.verifikovan = True
            kartica.budzet -= 1
            db.session.commit()
            flash("Nalog uspesno verifikovan.", category='success')
            return redirect(url_for('prikaz_profila'))
        else:
            flash("Greska prilikom verifikacije.", category='danger')
    return render_template('verifikacija.html', forma=forma, korisnik_verifikacija = korisnik_verifikacija)