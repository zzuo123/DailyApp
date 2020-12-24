import random
from flask import render_template, session, Blueprint
from dailyapp.main.weather import get_weather

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

@main.route('/weather')
def weather():
	data = get_weather('02148')
	return render_template('weather.html', title='Weather', background=get_image(), weather=data)