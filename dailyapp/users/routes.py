from flask import render_template, redirect, url_for, flash, request, Blueprint, current_app
from flask_login import current_user, login_user, logout_user, login_required
from dailyapp import db, bcrypt
from dailyapp.models import User
from dailyapp.users.forms import PreRegisterForm, RegisterForm, LoginForm
from dailyapp.users.utils import send_pre_register_email, Serializer

users = Blueprint('users', __name__)


@users.route('/pre_register', methods=['GET', 'POST'])
def pre_register():
    # if current user is registered, redirect him to home
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = PreRegisterForm()
    if form.validate_on_submit():
        send_pre_register_email(form.email.data)
        flash('A confirmation email has been sent to your account, please follow link there to complete registration', 'info')
        return redirect(url_for('users.pre_register'))
    return render_template('pre_register.html', title='Register', form=form)


@users.route('/register/<token>', methods=['GET', 'POST'])
def register(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    # decode token and try to get email
    s = Serializer(current_app.config['SECRET_KEY'])
    email = None
    try:
        email = s.loads(token)['email']
    except:
        pass
    if email is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.pre_register'))
    flash(email)
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to login.', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)  # remember me is a true/false value
            next_page = request.args.get('next')  # user get('next') instead of ['next'] because it returns none if key does not exist
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/account')
@login_required
def account():
    return render_template('account.html', title='Account')