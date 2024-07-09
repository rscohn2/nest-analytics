import os

import requests


def get_current_weather(api_key, lat, lon):
    url = (
        "http://api.openweathermap.org/data/2.5/weather?"
        f"lat={lat}&lon={lon}&appid={api_key}&units=imperial"
    )
    response = requests.get(url)
    weather_data = response.json()
    print(f"Response: {weather_data}")
    temperature = weather_data["main"]["temp"]
    humidity = weather_data["main"]["humidity"]
    return temperature, humidity


# Example usage
api_key = os.getenv(
    "OPENWEATHERMAP_API_KEY"
)  # Replace with your actual OpenWeatherMap API key
print(f"API Key: {api_key}")
lat = "42.76950214174165"
lon = "-71.27612488426918"

temperature, humidity = get_current_weather(api_key, lat, lon)
print(f"Current Temperature: {temperature}°F, Humidity: {humidity}%")
