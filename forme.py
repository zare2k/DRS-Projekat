from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from projekat.modeli import Korisnik

class RegisterForm(FlaskForm):
  
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
  email = StringField(label='Email:', validators=[DataRequired()])
  lozinka = PasswordField(label='Lozinka:', validators=[DataRequired()])
  submit = SubmitField(label='Prijavi se')