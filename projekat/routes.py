from projekat import app
from projekat.forme import RegisterForm, LoginForm
from projekat.modeli import Korisnik
from flask import render_template, flash, redirect, url_for
from flask_login import login_user, logout_user

@app.route('/')
@app.route('/home')
def pocetna():
    return render_template('base.html')

@app.route('/registracija', methods=['GET', 'POST'])
def registracija():
    forma = RegisterForm()
    if forma.validate_on_submit():
        korisnik = Korisnik(ime=forma.ime,
                              prezime=forma.prezime,
                              adresa=forma.adresa,
                              grad=forma.grad,
                              drzava=forma.drzava,
                              broj_telefona=forma.broj_telefona,
                              email=forma.email,
                              lozinka=forma.lozinka1)
        flash(f"Nalog uspesno kreiran.", category="success")
        return redirect(url_for('pocetna'))
    if forma.errors != {}: 
        for err_msg in forma.errors.values():
            flash(f'There was en error with creating a user: {err_msg}', category='danger')
    return render_template('registracija.html', forma=forma)
    
@app.route('/prijava', methods=['GET', 'POST'])
def prijava():
    forma = LoginForm()
    return render_template('prijava.html', forma=forma)