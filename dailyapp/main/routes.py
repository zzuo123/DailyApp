import random
from flask import render_template, session, Blueprint
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
    if session.get('zipcode') is None:
        form = ZipForm()
        if form.validate_on_submit():
            session['zipcode'] = form.zipcode.data
            data = get_weather(session['zipcode'])
            return render_template('weather.html', title='Weather', background=get_image(), weather=data)
        return render_template('get_zip.html', title='Weather', background=get_image(), form=form)
    else:
        data = get_weather(session['zipcode'])
        return render_template('weather.html', title='Weather', background=get_image(), weather=data)