from projekat import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Korisnik.query.get(int(user_id))

class Korisnik(db.Model, UserMixin):
  id = db.Column(db.Integer(), primary_key=True)
  ime = db.Column(db.String(length=30), nullable=False)
  prezime = db.Column(db.String(length=30), nullable=False)
  adresa = db.Column(db.String(length=30), nullable=False)
  grad = db.Column(db.String(length=30), nullable=False)
  drzava = db.Column(db.String(length=30), nullable=False)
  broj_telefona = db.Column(db.Integer(), nullable=False)
  email = db.Column(db.String(length=30), nullable=False, unique=True)
  lozinka = db.Column(db.String(length=30), nullable=False)
  verifikovan = db.Column(db.Boolean(), nullable=False, default=False)
  kartica = db.relationship('Kartica', backref='vlasnik_kartice', lazy=True)
  
  @property
  def je_verifikovan(self):
    return self.verifikovan
  
class Kartica(db.Model, UserMixin):
  id = db.Column(db.Integer(), primary_key=True)
  broj_kartice = db.Column(db.String(), nullable=False, unique = True)
  datum_isteka_kartice = db.Column(db.String(length=30), nullable=False)
  sigurnosni_kod = db.Column(db.String(length=3), nullable=False)
  budzet = db.Column(db.Integer(), nullable=False, default=0)
  ime_korisnika = db.Column(db.Integer(), db.ForeignKey('korisnik.id'))

