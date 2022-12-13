from flask_login import UserMixin

class Korisnik(UserMixin):
  def __init__(self, ime, prezime, adresa, grad, drzava, broj_telefona, email, lozinka):
    self.ime = ime
    self.prezime = prezime
    self.adresa = adresa
    self.grad = grad
    self.drzava = drzava
    self.broj_telefona = broj_telefona
    self.email = email
    self.lozinka = lozinka