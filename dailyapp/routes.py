import random
from flask import render_template, url_for, redirect, flash, request, session
from dailyapp import app, db, bcrypt
from dailyapp.forms import RegistrationForm, LoginForm
from dailyapp.models import User, Diary
from dailyapp.weather import get_weather
from flask_login import login_user, current_user, logout_user, login_required


def get_image():
    if not 'image' in session:
        # Relative path from the templates folder, b.c. background image are rendered in .html files
        session['image'] = '../static/images/wallpapers/' + str(random.randint(1,11)) + '.jpg'
    return session['image']


@app.route('/')
@app.route('/home')
def home():
	return render_template('home.html', title='Home', background=get_image())

@app.route('/weather')
def weather():
	data = get_weather('02148')
	return render_template('weather.html', title='Weather', background=get_image(), weather=data)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)  # remember me is a true/false value
            next_page = request.args.get('next')  # user get('next') instead of ['next'] because it returns none if key does not exist
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/account')
@login_required
def account():
    return render_template('account.html', title='Account')