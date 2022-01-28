from configparser import ConfigParser
import argparse
import sys
from turtle import clear
from urllib import parse, request, error
import json
from pprint import pp

from pandas import RangeIndex
import style

BASE_WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"
THUNDERSTORM = range(200,300)
DRIZZLE = range(300,400)
RAIN = range(500,600)
SNOW = range(600,700)
ATMOSPHERE = range(700,800)
CLEAR = range(800,801)
CLOUDY = range(801,900) 


def _get_api_key():
    config = ConfigParser()
    config.read("secrets.ini")
    return config["openweather"]["api_key"]

def read_user_cli_args():
    parser = argparse.ArgumentParser(
        description="Reciba la información del tiempo para una ciudad"
    )
    parser.add_argument(
        "city", nargs="+", type=str, help="Entra el nombre de la ciudad"
    )
    parser.add_argument(
        "-i",
        "--imperial",
        action="store_true",
        help="Enseña la temperatura a la inglesa (Fº)"
    )
    return parser.parse_args()

def build_weather_query(city_input, imperial=False):
    api_key=_get_api_key()
    city_name = " ".join(city_input)
    url_encoded_city_name = parse.quote_plus(city_name)
    units = "imperial" if imperial else "metric"
    url = (
        f"{BASE_WEATHER_API_URL}?q={url_encoded_city_name}"
        f"&units={units}&appid={api_key}&lang=es"

    )
    return url 

def get_weather_data(query_url):
    try:
        response = request.urlopen(query_url)        
    except error.HTTPError as http_error:
        if http_error.code == 401:
            sys.exit("Acceso denegado")
        elif http_error.code == 404:
            sys.exit("No se puede encontrar datos sobre esta ciudad")
        else:
            sys.exit(f"Algo fallo: {http_error.code}")

    data = response.read()
    
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        sys.exit("No se puede leer los datos del servidor")

def display_weather_info(weather_data, imperial=False):
    
    city = weather_data['name']
    desc = weather_data['weather'][0]['description'] 
    temperature  = weather_data['main']['temp']
    weather_id = weather_data["weather"][0]["id"]
    
    print( f"{style.REVERSE}{city:^{style.PADDING}}{style.RESET}", end="")
    
    weather_symbol, color = _select_weather_display_params(weather_id)
    style.change_color(color)
    print(f"\t{weather_symbol}", end="")
    print(
        f"{desc.capitalize():^{style.PADDING}}",end=""       
    )
    style.change_color(style.RESET)
    print( f"({temperature}º{'F' if imperial else 'C'})")



def _select_weather_display_params(weather_id):
    if weather_id in THUNDERSTORM:
        display_param = "💥", style.RED
    elif weather_id in DRIZZLE:
        display_param = "💧", style.CYAN
    elif weather_id in RAIN:
        display_param = "⛆", style.BLUE
    elif weather_id in SNOW:
        display_param = "❄️", style.WHITE
    elif weather_id in ATMOSPHERE:
        display_param = "🌀", style.BLUE
    elif weather_id in CLEAR:
        display_param = "☀️", style.YELLOW
    elif weather_id in CLOUDY:
        display_param = "💨", style.WHITE
    else:
        display_param = "🌈", style.RESET
    return display_param
if __name__=="__main__":
    user_args=read_user_cli_args()
    query_url = build_weather_query(user_args.city,user_args.imperial)
    weather_data = get_weather_data(query_url)
    display_weather_info(weather_data, user_args.imperial)
    
    