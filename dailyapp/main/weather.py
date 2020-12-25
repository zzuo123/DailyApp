import json, urllib.request, os
from datetime import datetime


def weather_from_api(zip, units, API_key=os.environ.get('owm_api_key')):
	url = f"https://api.openweathermap.org/data/2.5/weather?zip={zip},us&units={units}&appid={API_key}"
	try:
		response = urllib.request.urlopen(url)
		data = json.loads(response.read())
	except urllib.error.HTTPError:
		data = None
	return data


def get_icon(sunrise, sunset, id):
	sunrise_hour = int(datetime.utcfromtimestamp(sunrise).strftime('%H'))
	sunset_hour = int(datetime.utcfromtimestamp(sunset).strftime('%H'))
	with open('dailyapp/static/icons.json') as f:
		icon = json.load(f)[str(id)]['icon']
	hour = datetime.now().hour
	if not (id > 699 and id < 800) and not (id > 899 and id < 1000):
		if hour > sunrise_hour and hour < sunset_hour:
			icon = "day-"+icon
		else:
			icon ="night-"+icon
	return 'wi-'+icon+'.svg'


def parse_weather(data, units):
	# we want [0]city, [1]weather, [2]icon, [3]temp, [4]feel, [5]min, [6]max, [7]pressure, [8]humidity, [9]visibility, [10]wind speed, [11]wind degree, [12]cloudiness, [13]sunrise, [14]sunset, [15]update_time
	weather = [data['name'], data['weather'][0]['description']]
	icon = get_icon(data['sys']['sunrise'], data['sys']['sunset'], data['weather'][0]['id'])
	weather.append(icon)
	if units == 'metric':
		weather.append(str(data['main']['temp'])+'°C')
		weather.append(str(data['main']['feels_like'])+'°C')
		weather.append(str(data['main']['temp_min'])+'°C')
		weather.append(str(data['main']['temp_max'])+'°C')
	else:  # imperial
		weather.append(str(data['main']['temp'])+'°F')
		weather.append(str(data['main']['feels_like'])+'°F')
		weather.append(str(data['main']['temp_min'])+'°F')
		weather.append(str(data['main']['temp_max'])+'°F')
	weather.append(str(data['main']['pressure'])+'hPa')
	weather.append(str(data['main']['humidity'])+'%')
	weather.append(str(data['main']['humidity'])+'%')
	weather.append(str(data['wind']['speed'])+'m/s')
	weather.append(str(data['wind']['deg'])+'°')
	weather.append(str(data['clouds']['all'])+'%')
	weather.append(datetime.utcfromtimestamp(data['sys']['sunrise'] + data['timezone']).strftime('%H:%M:%S'))
	weather.append(datetime.utcfromtimestamp(data['sys']['sunset'] + data['timezone']).strftime('%H:%M:%S'))
	weather.append(datetime.utcfromtimestamp(data['dt'] + data['timezone']).strftime('%Y-%m-%d %H:%M:%S'))
	return weather
	

example_response = {'coord': {'lon': -71.06, 'lat': 42.43}, 'weather': [{'id': 500, 'main': 'Rain', 'description': 'light rain', 'icon': '10d'}, {'id': 701, 'main': 'Mist', 'description': 'mist', 'icon': '50d'}], 'base': 'stations', 'main': {'temp': 34.57, 'feels_like': 26.92, 'temp_min': 33.01, 'temp_max': 36, 'pressure': 1008, 'humidity': 86}, 'visibility': 6437, 'wind': {'speed': 6.93, 'deg': 360}, 'rain': {'1h': 0.44}, 'clouds': {'all': 90}, 'dt': 1608575189, 'sys': {'type': 1, 'id': 3486, 'country': 'US', 'sunrise': 1608552639, 'sunset': 1608585269}, 'timezone': -18000, 'id': 0, 'name': 'Malden', 'cod': 200}

def get_weather(zip, units='imperial'):
	data = weather_from_api(zip, units)
	if data:
		return parse_weather(data, units)
	else:
		return None