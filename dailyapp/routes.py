import random, os
from flask import render_template, url_for, redirect, flash, request, session
from dailyapp import app, db, bcrypt, mail
from flask_mail import Message
from dailyapp.forms import PreRegisterForm, RegisterForm, LoginForm
from dailyapp.models import User, Diary
from dailyapp.weather import get_weather
from flask_login import login_user, current_user, logout_user, login_required
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


def get_image():
    if not 'image' in session:
        # Relative path from the templates folder, b.c. background image are rendered in .html files
        session['image'] = '../static/images/wallpapers/' + str(random.randint(1,11)) + '.jpg'
    return session['image']


def send_pre_register_email(email):
    # Serializer (secret_key, expiration_time(seconds))
    s = Serializer(app.config['SECRET_KEY'], 1800)
    token = s.dumps({'email': email}).decode('utf-8')
    msg = Message('Flaskblog Registration Email (valid for 30 minutes)', sender=('George Zuo', 'codergeorge01@gmail.com'), recipients=[email])
    msg.body = f'''To create an account, visit the following link:
{url_for('register', token=token, _external=True)}

If you did not make this request, then simply ignore this email and no changes will be made.
'''
    # _external=True makes url_form return an absolute url (contains full domain) instead of relative one
    mail.send(msg)


@app.route('/')
@app.route('/home')
def home():
	return render_template('home.html', title='Home', background=get_image())

@app.route('/weather')
def weather():
	data = get_weather('02148')
	return render_template('weather.html', title='Weather', background=get_image(), weather=data)


@app.route('/pre_register', methods=['GET', 'POST'])
def pre_register():
    # if current user is registered, redirect him to home
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = PreRegisterForm()
    if form.validate_on_submit():
        send_pre_register_email(form.email.data)
        flash('A confirmation email has been sent to your account, please follow link there to complete registration', 'info')
        return redirect(url_for('pre_register'))
    return render_template('pre_register.html', title='Register', form=form)


@app.route('/register/<token>', methods=['GET', 'POST'])
def register(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    # decode token and try to get email
    s = Serializer(app.config['SECRET_KEY'])
    email = None
    try:
        email = s.loads(token)['email']
    except:
        pass
    if email is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('pre_register'))
    flash(email)
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=email, password=hashed_password)
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