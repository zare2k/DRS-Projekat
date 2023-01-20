from projekat import db, login_manager
from flask_login import UserMixin
import datetime
import requests

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
  stanje = db.relationship('Stanja', backref='vlasnik_stanja', lazy=True)
  
  @property
  def je_verifikovan(self):
    return self.verifikovan
  
  def prikaz_stanja(self, kartica):
    self.id = kartica.ime_korisnika
    
  def provera_datuma(self, datum):
    try:
      datetime.datetime.strptime(datum, '%m/%Y')
      return True
    except ValueError:
      return False  

  
class Kartica(db.Model, UserMixin):
  id = db.Column(db.Integer(), primary_key=True)
  broj_kartice = db.Column(db.String(), nullable=False, unique = True)
  datum_isteka_kartice = db.Column(db.String(length=30), nullable=False)
  sigurnosni_kod = db.Column(db.String(length=3), nullable=False)
  budzet = db.Column(db.Float(), nullable=False, default=0)
  #online_budzet = db.Column(db.Float(), nullable=False, default=0)
  #valuta = db.Column(db.String(length=3), nullable=False, default='RSD')
  ime_korisnika = db.Column(db.Integer(), db.ForeignKey('korisnik.id'))
  
  def uplata_online(self, iznos):
    return self.budzet >= iznos and iznos > 0
    
class Stanja(db.Model, UserMixin):
  id = db.Column(db.Integer(), primary_key=True)
  valuta = db.Column(db.String(length=3), nullable=False)
  vrednost = db.Column(db.Integer(), nullable=False)
  ime_korisnika = db.Column(db.Integer(), db.ForeignKey('korisnik.id'))

class RealTimeCurrencyConverter():
    def __init__(self,url):
            self.data = requests.get(url).json()
            self.currencies = self.data['rates']

    def convert(self, from_currency, to_currency, amount): 
        if from_currency != 'RSD' : 
            amount = amount / self.currencies[from_currency] 
  
        # limiting the precision to 4 decimal places 
        amount = round(amount * self.currencies[to_currency], 2) 
        return amount
      
    def get_valute(self):
      return self.currencies
    
class Transakcije(db.Model, UserMixin):
  id = db.Column(db.Integer(), primary_key=True)
  suma = db.Column(db.Integer(), nullable=False)
  stanje_transakcije = db.Column(db.String(length=30), nullable=True)
  vreme_transakcije = db.Column(db.String(length=30), nullable=False)
  vrsta_uplate = db.Column(db.String(length=30), nullable=False)
  email_primaoca = db.Column(db.String(length=30))
  broj_kartice_primaoca = db.Column(db.String(length=30))
