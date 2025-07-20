import datetime as dt
import requests

API_KEY = '59ae5c0a66d15dbcd1af005b2d622b05'
CITY = "KALYANI"
LAT = 22.99139
LON = 88.4482395

url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}"

response = requests.get(url).json()

print(response)

