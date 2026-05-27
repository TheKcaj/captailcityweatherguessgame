import pandas as pd
import random
import requests
import math
import PySimpleGUI as sg
import os
from dotenv import load_dotenv

load_dotenv()

weather_icons = {
    "01d": "☀",
    "01n": "🌙",
    "02d": "⛅",
    "03d": "☁",
    "04d": "☁",
    "09d": "🌧",
    "10d": "🌦",
    "11d": "⛈",
    "13d": "❄",
    "50d": "🌫"
}

# Use Haversine/Azimuth formulas to calulate distance and direction of the correct city from the guesssed city
def calculate_distance_and_bearing(guessed_country_info, correct_city, guessed_city_and_country):
    lat1 = guessed_country_info["Latitude"]
    lon1 = guessed_country_info["Longitude"]
    lat2 = correct_city["Latitude"]
    lon2 = correct_city["Longitude"]
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    R = 6371.0 # Radius in km

    a = math.sin((lat2-lat1)/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2-lon1)/2)**2
    distance = round(2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a)), 2)

    x = math.sin(lon2-lon1) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(lon2-lon1))
    bearing = (math.degrees(math.atan2(x, y)) + 360) % 360
    directions = [
        "north",
        "north east",
        "east",
        "south east",
        "south",
        "south west",
        "west",
        "north west"
    ]
    index = round(bearing / 45) % 8
    compassPoint = directions[index]
    return f"{guessed_city_and_country:<30} {distance}km {compassPoint}"

list_of_countries = pd.read_csv('data_file.csv')

def new_capital():
    apiKey = os.getenv("OPENWEATHER_API_KEY")
    selected_city = random.choice(list_of_countries.to_dict("records"))
    print("selected_city: ", selected_city) # Printing the selected city for devs to see the correct answer
    url = "https://api.openweathermap.org/data/2.5/weather?lat={0}&lon={1}&appid={2}&units=metric".format(selected_city["Latitude"], selected_city["Longitude"], apiKey)
    try:
        response = requests.get(url, timeout=5)
        parsedResponse = response.json()
    except requests.RequestException:
        parsedResponse = None
    if not parsedResponse:
        weather = {
            "temp": "--",
            "humidity": "--",
            "wind": "--",
            "pressure": "--",
            "condition": "Unavailable",
            "icon": "03d"
        }
    else:
        weather = {
            "temp": parsedResponse["main"]["temp"],
            "humidity": parsedResponse["main"]["humidity"],
            "wind": parsedResponse["wind"]["speed"],
            "pressure": parsedResponse["main"]["pressure"],
            "condition": parsedResponse["weather"][0]["main"],
            "icon": parsedResponse["weather"][0]["icon"]
        }
    return selected_city, weather

all_cities = (list_of_countries["Capital City"] + ", " + list_of_countries["Country"]).tolist()
remaining_cities = all_cities.copy()
wrong_guesses = []

def filter_cities(search_text, cities):
    search_text = search_text.lower()
    return [city for city in cities if search_text in city.lower()]

def update_weather_ui(window, weather):
    window["-TEMP-"].update(f"{weather['temp']}°C")
    window["-CONDITION-"].update(weather["condition"])
    window["-HUMIDITY-"].update(f"{weather['humidity']}%")
    window["-WIND-"].update(f"{weather['wind']} km/h")
    window["-PRESSURE-"].update(f"{weather['pressure']} hPa")
    icon = weather_icons.get(weather["icon"], "☁")
    window["-WEATHER-ICON-"].update(icon)
    if weather['temp'] == "--":
        sg.popup("Weather API unavailable.")

sg.theme("DarkBlue3")

weather_frame = [
    [
        sg.Column([
            [
                sg.Text(
                    "☁",
                    key="-WEATHER-ICON-",
                    font=("Helvetica", 42),
                    size=(3, 1),
                    justification="center"
                ),
                sg.Column([
                    [
                        sg.Text(
                            "--°C",
                            key="-TEMP-",
                            font=("Helvetica", 28, "bold")
                        )
                    ],

                    [
                        sg.Text(
                            "Unknown",
                            key="-CONDITION-",
                            font=("Helvetica", 14)
                        )
                    ]

                ], pad=((15, 0), 0))
            ],
            [
                sg.HorizontalSeparator()
            ],
            [
                sg.Text("Humidity:", size=(12, 1), font=("Helvetica", 11, "bold")),
                sg.Text("--%", key="-HUMIDITY-")
            ],
            [
                sg.Text("Wind Speed:", size=(12, 1), font=("Helvetica", 11, "bold")),
                sg.Text("-- km/h", key="-WIND-")
            ],
            [
                sg.Text("Pressure:", size=(12, 1), font=("Helvetica", 11, "bold")),
                sg.Text("-- hPa", key="-PRESSURE-")
            ]
        ],
        expand_x=True,
        pad=(10, 10))
    ]
]

layout = [
    [
        sg.Frame(
            "Weather Data",
            weather_frame,
            expand_x=True
        )
    ],
    [
        sg.Text("Search Cities:"),
        sg.Input(
            "",
            key="-SEARCH-",
            enable_events=True,
            expand_x=True
        )
    ],
    [
        sg.Column([
            [
                sg.Text("Possible Cities")
            ],
            [
                sg.Listbox(
                    values=remaining_cities,
                    size=(45, 18),
                    key="-CITY-LIST-",
                    enable_events=True
                )
            ]
        ]),
        sg.Column([
            [
                sg.Text("Wrong Guesses")
            ],
            [
                sg.Listbox(
                    values=wrong_guesses,
                    size=(45, 18),
                    key="-WRONG-LIST-"
                )
            ]
        ]),
        sg.Column([
            [
                sg.Text("Distance from target city")
            ],
            [
                sg.Multiline(
                    "",
                    size=(35, 18),
                    key="-DISTANCE-",
                    disabled=True,
                    autoscroll=True,
                    no_scrollbar=True
                )
            ]
    ])
    ],
    [
        sg.Button("Guess"),
        sg.Button("Give Up / New Capital"),
        sg.Push(),
        sg.Button("Exit")
    ]
]

window = sg.Window(
    "Capital City Weather Guessing Game",
    layout,
    size=(955, 650),
    resizable=True,
    finalize=True,
    element_justification="center"
)

correct_city, weather = new_capital()
update_weather_ui(window, weather)

while True:
    event, values = window.read()

    if event in (sg.WINDOW_CLOSED, "Exit"):
        break

    if event == "-SEARCH-":
        filtered = filter_cities(values["-SEARCH-"], remaining_cities)
        window["-CITY-LIST-"].update(filtered)
        
    if event == "Guess":

        selected = values["-CITY-LIST-"]

        if selected:
            guessed_city_and_country = selected[0]

            if guessed_city_and_country == correct_city["Capital City"] + ", " + correct_city["Country"]:
                sg.popup(
                    "Correct!",
                    f"{guessed_city_and_country} is the right answer!\n"
                    "Loading a new capital..."
                )
                
                remaining_cities = all_cities.copy()
                correct_city, weather = new_capital()
                wrong_guesses.clear()
                window["-WRONG-LIST-"].update(wrong_guesses)
                window["-SEARCH-"].update("")
                window["-CITY-LIST-"].update(remaining_cities)
                window["-DISTANCE-"].update("")
                update_weather_ui(window, weather)
            else:
                if guessed_city_and_country not in wrong_guesses:
                    guessed_city_and_country_split = guessed_city_and_country.split(", ", 1)
                    guessed_country_info = list_of_countries.loc[list_of_countries["Country"] == guessed_city_and_country_split[1]].iloc[0]
                    distance_from_last_guess = calculate_distance_and_bearing(guessed_country_info, correct_city, guessed_city_and_country)
                    wrong_guesses.append(guessed_city_and_country)
                    
                    if guessed_city_and_country in remaining_cities:
                        remaining_cities.remove(guessed_city_and_country)
                    
                    window["-WRONG-LIST-"].update(wrong_guesses)
                    window["-SEARCH-"].update("")
                    window["-CITY-LIST-"].update(remaining_cities)
                    window["-DISTANCE-"].print(f"{distance_from_last_guess} \n")
        else:
            sg.popup("Please select a city from the possible cities list.")
            
    if event == "Give Up / New Capital":
        confirm = sg.popup_yes_no(
            "Are you sure you want to give up?\n\n"
            "Your current progress will be lost.",
            title="Confirm New Capital"
        )
        if confirm == "Yes":
            correct_city, new_weather = new_capital()
            wrong_guesses.clear()
            remaining_cities = all_cities.copy()
            window["-WRONG-LIST-"].update(wrong_guesses)
            window["-SEARCH-"].update("")
            window["-CITY-LIST-"].update(remaining_cities)
            window["-DISTANCE-"].update("")
            update_weather_ui(window, new_weather)
            sg.popup(
                "New Capital Selected",
                "A new capital city has been chosen."
            )
window.close()