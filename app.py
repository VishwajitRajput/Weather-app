import datetime
from flask import Flask, jsonify, render_template, request
from flask_pymongo import PyMongo
from pymongo import MongoClient
import requests

app = Flask(__name__)

# Database configuration
client = MongoClient('mongodb://localhost:27017/')
db = client['Weather_db_asg']
collection = db['assignment']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city_name = request.form['name']
        url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&APPID=ce86d5e03fcf845e371a31f462deb074'
        response = requests.get(url.format(city_name)).json()

        temp = response['main']['temp']
        weather = response['weather'][0]['description']
        min_temp = response['main']['temp_min']
        max_temp = response['main']['temp_max']
        icon = response['weather'][0]['icon']

        data = {
            'city_name': city_name,
            'temp': temp,
            'weather': weather,
            'min_temp': min_temp,
            'max_temp': max_temp,
            'icon': icon,
            'timestamp': datetime.datetime.now()
        }
        collection.insert_one(data)

        return render_template('index.html', temp=temp, weather=weather, min_temp=min_temp, max_temp=max_temp, icon=icon, city_name=city_name)
    else:
        return render_template('index.html')

@app.route('/weather_data', methods=['GET'])
def get_weather_data():
    location = request.args.get('location')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    min_temp = request.args.get('min_temp')
    max_temp = request.args.get('max_temp')

    query = {}

    if location:
        query['city_name'] = location
    
    if start_date and end_date:
        query['timestamp'] = {
            '$gte': datetime.datetime.strptime(start_date, '%Y-%m-%d'),
            '$lte': datetime.datetime.strptime(end_date, '%Y-%m-%d') + datetime.timedelta(days=1)
        }
    
    if min_temp:
        query['temp'] = {'$gte': float(min_temp)}
    
    if max_temp:
        query['temp'] = {'$lte': float(max_temp)}

    weather_data = collection.find(query, {'_id': 0})
    weather_data_list = list(weather_data)

    statistics = calculate_statistics(weather_data_list)

    response = {
        'weather_data': weather_data_list,
        'statistics': statistics
    }

    return jsonify(response)

def calculate_statistics(weather_data):
    temperatures = [data['temp'] for data in weather_data]

    if temperatures:
        average_temp = sum(temperatures) / len(temperatures)
        max_temp = max(temperatures)
        min_temp = min(temperatures)
    else:
        average_temp = None
        max_temp = None
        min_temp = None

    statistics = {
        'average_temp': average_temp,
        'max_temp': max_temp,
        'min_temp': min_temp
    }

    return statistics

if __name__ == '__main__':
    app.run(debug=True)
