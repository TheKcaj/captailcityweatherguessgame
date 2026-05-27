The inspiration for this project is the website https://countryle.com where the user has to guess a country based on some data given, but instead of guessing a country based on average weather and population size I have used the openweathermap API that can be found here (https://openweathermap.org) to get live weather data of capital cities around the world.

The data file used for all capital cities in the world is from this github: https://gist.github.com/ofou/df09a6834a8421b4f376c875194915c9

List of packages requied to be installed to run this script:
	pandas
	random
	requests
	math
	PySimpleGUI
  	os
	dotenv

A .env file is also needed for the API key, for example: OPENWEATHER_API_KEY=your_actual_api_key_here
