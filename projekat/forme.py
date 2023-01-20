from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, FloatField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from projekat.modeli import Korisnik, Kartica

class RegisterForm(FlaskForm):
  
  def validate_email(self, email_provera):
    korisnik = Korisnik.query.filter_by(email=email_provera.data).first()
    if korisnik:
      raise ValidationError('Korisnik sa unetom email adresom već postoji. Unesite drugu email adresu.')
  
  ime = StringField(label='Ime:', validators=[Length(min=3, max=30), DataRequired()])
  prezime = StringField(label='Prezime:', validators=[Length(min=3, max=30), DataRequired()])
  adresa = StringField(label='Adresa:', validators=[Length(min=3, max=30), DataRequired()])
  grad = StringField(label='Grad:', validators=[Length(min=3, max=30), DataRequired()])
  drzava = StringField(label='Drzava:', validators=[Length(min=3, max=30), DataRequired()])
  broj_telefona = StringField(label='Broj telefona:', validators=[Length(min=3, max=30), DataRequired()])
  email = StringField(label='Email:', validators=[Email(), DataRequired()])
  lozinka1 = PasswordField(label='Lozinka:', validators=[Length(min=5), DataRequired()])
  lozinka2 = PasswordField(label='Potvrdi lozinku:', validators=[EqualTo('lozinka1'), DataRequired()])
  submit = SubmitField(label='Kreiraj nalog')
    
class LoginForm(FlaskForm):
  email = StringField(label='Email:', validators=[Email(), DataRequired()])
  lozinka = PasswordField(label='Lozinka:', validators=[Length(min=5), DataRequired()])
  submit = SubmitField(label='Prijavi se')
  
class IzmenaForm(FlaskForm):
  ime = StringField(label='Ime:', validators=[Length(min=3, max=30), DataRequired()])
  prezime = StringField(label='Prezime:', validators=[Length(min=3, max=30), DataRequired()])
  adresa = StringField(label='Adresa:', validators=[Length(min=3, max=30), DataRequired()])
  grad = StringField(label='Grad:', validators=[Length(min=3, max=30), DataRequired()])
  drzava = StringField(label='Drzava:', validators=[Length(min=3, max=30), DataRequired()])
  broj_telefona = StringField(label='Broj telefona:', validators=[Length(min=3, max=30), DataRequired()])
  email = StringField(label='Email:', validators=[Email(), DataRequired()])
  submit = SubmitField(label='Sacuvaj izmene')
  
class VerifikacijaForm(FlaskForm):
  broj_kartice = StringField(label='Broj kartice:', validators=[Length(min=16, max=16), DataRequired()])
  datum_isteka_kartice = StringField(label='Datum isteka kartice(format MM/YYYY): ', validators=[DataRequired()])
  sigurnosni_kod = StringField(label='Sigurnosni kod: ', validators=[Length(min=3, max=3), DataRequired()])
  submit = SubmitField(label='Verifikuj nalog')
  
class OnlineUplataForm(FlaskForm):
  iznos = FloatField(label='Iznos: ', validators=[DataRequired()])
  submit = SubmitField(label='Uplati na račun')
  
class KonvertovanjeForm(FlaskForm):
  iznos = FloatField(label='Iznos: ', validators=[DataRequired()])
  submit = SubmitField(label='Konvertuj')

class TransakcijeKarticaForm(FlaskForm):
  suma = FloatField(label='Iznos: ', validators=[DataRequired()])
  broj_kartice_primaoca = StringField(label='Broj kartice:', validators=[Length(min=16, max=16), DataRequired()])
  submit = SubmitField(label='Uplati')
  
class TransakcijeRacunForm(FlaskForm):
  suma = FloatField(label='Iznos: ', validators=[DataRequired()])
  email_primaoca = StringField(label='Email:', validators=[Email(), DataRequired()])
  submit = SubmitField(label='Uplati')
