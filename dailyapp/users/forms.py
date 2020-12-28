import re
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from dailyapp.models import User
from dailyapp.main.weather import weather_from_api


class ZipForm(FlaskForm):
    zipcode = StringField(validators=[DataRequired()])
    submit = SubmitField('OK')

    def validate_zipcode(self, zipcode):
        valid_zip = re.search(r'^\d{5}$', zipcode.data)
        if not valid_zip or not weather_from_api(zipcode.data, 'imperial'):
            raise ValidationError('That doesn\'t look like a US zip code. Please try a different one.')


class PreRegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Email')
    
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:  # if email exists in the User table
            raise ValidationError('That email is used by another user. Please user a diffferent one.')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:  # if user exists in the User table
            raise ValidationError('That username is taken. Please choose a diffferent one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    zipcode = StringField('Zipcode')
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:  # if user exists in the User table
                raise ValidationError('That username is taken. Please choose a diffferent one.')
    def validate_email(self, email):
        if email.data != current_user.email:
            email = User.query.filter_by(email=email.data).first()
            if email:  # if email exists in the User table
                raise ValidationError('That email is used by another user. Please user a diffferent one.')
    def validate_zipcode(self, zipcode):
        valid_zip = re.search(r'^\d{5}$', zipcode.data)
        if not valid_zip or not weather_from_api(zipcode.data, 'imperial'):
            raise ValidationError('That doesn\'t look like a US zip code. Please try a different one.')