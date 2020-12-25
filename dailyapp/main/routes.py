import random
from flask import render_template, session, Blueprint, flash
from flask.helpers import url_for
from werkzeug.utils import redirect
from dailyapp.main.weather import get_weather
from flask_login import current_user
from dailyapp.users.forms import ZipForm

main = Blueprint('main', __name__)


def get_image():
    if not 'image' in session:
        # Relative path from the templates folder, b.c. background image are rendered in .html files
        session['image'] = '../static/images/wallpapers/' + str(random.randint(1,11)) + '.jpg'
    return session['image']


@main.route('/')
@main.route('/home')
def home():
	return render_template('home.html', title='Home', background=get_image())

@main.route('/weather', methods=['GET', 'POST'])
def weather():
    if (current_user.is_authenticated and current_user.zipcode != 'none') or 'zipcode' in session:
        if 'zipcode' not in session:  # user logged in and set zip code, but first visit weather page
            session['zipcode'] = current_user.zipcode
        data = get_weather(session['zipcode'])
        return render_template('weather.html', title='Weather', background=get_image(), weather=data)
    else:
        form = ZipForm()
        if form.validate_on_submit():
            zipcode = form.zipcode.data
            data = get_weather(zipcode)
            if not data:  # owm didn't return data for that zipcode
                flash('That zip code doesn\'t seem to work. Please try again!', 'warning')
                return redirect(url_for('main.home'))
            else:
                session['zipcode'] = form.zipcode.data
                return render_template('weather.html', title='Weather', background=get_image(), weather=data)
        return render_template('get_zip.html', title='Weather', background=get_image(), form=form)