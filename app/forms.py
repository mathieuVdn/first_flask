from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_wtf.file import FileField, FileRequired, FileAllowed
import sqlalchemy as sa
from app import db
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Sign in")


class RegistrationForm(FlaskForm):
    lastname = StringField('Lastname', validators=[DataRequired()])
    firstname = StringField("Firstname", validators=[DataRequired()])
    gender = SelectField("Gender", choices=[(0, "male"), (1, 'female')], validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo('password')]
    )
    profile_picture = FileField("Profile Picture", validators=[FileAllowed(['jpg', 'jpeg', 'png']), FileRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        print(username.data)
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        print(user)
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        print(email.data)
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        print(user)
        if user is not None:
            raise ValidationError('Please use a different email address.')


class MarketSearchForm(FlaskForm):
    symbol = StringField('Symbol', validators=[DataRequired()])
    submit = SubmitField('Search')
