from flask import render_template, redirect, url_for, flash, request, Blueprint, current_app, session
from flask_login import current_user, login_user, logout_user, login_required
from dailyapp import db, bcrypt
from dailyapp.models import User
from dailyapp.users.forms import PreRegisterForm, RegisterForm, LoginForm, RequestResetForm, UpdateAccountForm, ResetPasswordForm
from dailyapp.users.utils import send_pre_register_email, Serializer, send_reset_email

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
            if user.zipcode == 'none':
                # None needs to be added to avoid keyerror
                session.pop('zipcode', None)
            else:
                session['zipcode'] = user.zipcode
            login_user(user, remember=form.remember.data)  # remember me is a true/false value
            next_page = request.args.get('next')  # user get('next') instead of ['next'] because it returns none if key does not exist
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route('/logout')
def logout():
    logout_user()
    session.pop('zipcode', None)
    return redirect(url_for('main.home'))


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.zipcode = form.zipcode.data
        db.session.commit()
        # have to update zipcode in session (because it is stored in cookie)
        session['zipcode'] = form.zipcode.data
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.zipcode.data = current_user.zipcode
    return render_template('account.html', title='Account', form=form)


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('users.account'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset the password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)  # method returns a user if token is correct
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.add(user)
        db.session.commit()
        flash('Your password has been updated! You are now able to login.', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)