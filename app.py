from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

WEATHER_API_KEY = 'api_key'  # Replace with your OpenWeatherMap API key
IPINFO_API_KEY = 'api_key'

# Route to serve the index.html
@app.route('/')
def index():
    return render_template('index.html')

# Fetch user's location based on IP
def get_location_from_ip(ip):
    ipinfo_url = f"https://ipinfo.io/{ip}?token={IPINFO_API_KEY}"
    response = requests.get(ipinfo_url)
    
    if response.status_code != 200:
        print(f"Error: Unable to fetch location for IP {ip}, status code: {response.status_code}")
        return None, None, None

    data = response.json()

    if 'loc' in data:
        lat, lon = data['loc'].split(',')
        return lat, lon, data.get('city')
    
    print(f"Error: Location not found in the response for IP {ip}")
    return None, None, None

# API to fetch weather details (by city or lat/lon)
@app.route('/api/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city')
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    if city:
        # Fetch weather by city name
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={WEATHER_API_KEY}"
    elif lat and lon:
        # Fetch weather by latitude and longitude
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={WEATHER_API_KEY}"
    else:
        return jsonify({'error': 'City or coordinates not provided'}), 400

    response = requests.get(weather_url)
    data = response.json()

    if data.get('cod') != 200:
        return jsonify({'error': 'City or location not found'}), 404

    weather_data = {
        'city': data['name'],
        'temperature': data['main']['temp'],
        'description': data['weather'][0]['description'],
        'conditionCode': data['weather'][0]['id'],  # Include the condition code
        'humidity': data['main']['humidity'],
        'wind_speed': data['wind']['speed'],
    }
    
    return jsonify(weather_data)

if __name__ == '__main__':
    app.run(debug=True)