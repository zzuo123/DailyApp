from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from dailyapp import app, mail
from flask_mail import Message
from flask import url_for

def serialize(content, valid_time=1800):
    s = Serializer(app.config['SECRET_KEY'], valid_time)
    return s.dumps(content).decode('utf-8')


def send_pre_register_email(email):
    # Serializer (secret_key, expiration_time(seconds))
    msg = Message('DailyApp Registration Email (valid for 30 minutes)', sender=('George Zuo', 'codergeorge01@gmail.com'), recipients=[email])
    msg.body = f'''To create an account, visit the following link:
{url_for('users.register', token=serialize({'email': email}), _external=True)}

If you did not make this request, then simply ignore this email and no changes will be made.
'''
    # _external=True makes url_form return an absolute url (contains full domain) instead of relative one
    mail.send(msg)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Dailyapp Password Reset Request', sender=('George Zuo', 'codergeorge01@gmail.com'), recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request, then simply ignore this email and no changes will be made.
'''
    # _external=True makes url_form return an absolute url (contains full domain) instead of relative one
    mail.send(msg)