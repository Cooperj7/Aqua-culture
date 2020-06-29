import requests
import logging as log

import framework.database.database as database
from framework.io.io import IoType, Io

api_key = "dc5ae0780270feb4057d1d979bdc7307"
units = "imperial"
zip_code = "01564"
country_code = "us"

table_name = "weather"


class WeatherManager(Io):

    def __init__(self, name: str, actions):

        super().__init__(name, IoType.OUTPUT, actions, [])

        self.init_weather_table()

    @staticmethod
    def call_api(request: str) -> dict:
        """
        Uses the python requests library to make a API response and returns a dict representing the data as it is stored
        in a JSON file.

        :param request: request to make to the API
        :return: dict representing the data stored in as JSON
        """

        try:
            api_request = requests.get(request)

            if api_request.status_code == 200:

                return api_request.json()

            else:
                warning = "FAILED: API response did not return status code 200"
                log.getLogger().critical(warning)
                print(warning)

        except Exception as ex:

            ex_string = f"CRITICAL: failed to get response for API request: '{request}'\nException: {ex}"
            print(ex_string)
            log.getLogger().critical(ex_string)

        return {}

    def store_weather_data(self):
        """ Retrieves the weather data from the openWeather api then stores the desired information in database"""

        request = f"https://api.openweathermap.org/data/2.5/forecast?zip={zip_code},{country_code}&units={units}&appid={api_key}"
        weather_data = self.call_api(request)["list"]
        if weather_data == {}:
            database.clear_data_in_table("weather")
            for entry in weather_data:

                try:
                    data = {"date_time": entry["dt_txt"], "temperature": entry["main"]["temp"], "humidity": entry["main"]["humidity"],
                            "min_temperature": entry["main"]["temp_min"], "max_temperature": entry["main"]["temp_max"],
                            "weather_label": entry["weather"][0]["main"], "weather_description": entry["weather"][0]["description"],
                            "cloudiness_level": entry["clouds"]["all"], "wind_speed": entry["wind"]["speed"]}
                    database.insert_data(table_name, data)

                except:

                    ex_string = "FAILED: could not find or store all weather data from the openWeather API call\n"
                    print(ex_string)
                    log.getLogger(ex_string)

    @staticmethod
    def init_weather_table() -> None:
        """ Creates a table in the database to store the weather information """

        column_info = {"date_time": "TEXT", "temperature": "REAL", "min_temperature": "REAL", "max_temperature": "REAL",
                       "humidity": "INTEGER", "weather_label": "TEXT", "weather_description": "TEXT",
                       "cloudiness_level": "INTEGER", "wind_speed": "REAL"}
        database.create_table(table_name, column_info, True)

manager = WeatherManager("test", {})

manager.store_weather_data()