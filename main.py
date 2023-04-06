import requests

endpoint = "http://api.weatherapi.com/v1/current.json"
params = {"key": '46946f4f0e7d4446b5200724230604', "q": "kelowna,BC"}

response = requests.get(endpoint, params=params)

if response.status_code == 200:
    weather_data = response.json()
    print(weather_data)
    # print("Current Temperature in", weather_data["location"]["name"], "is", weather_data["current"]["temp_c"], "C")
else:
    print("Error:", response.status_code, response.reason)