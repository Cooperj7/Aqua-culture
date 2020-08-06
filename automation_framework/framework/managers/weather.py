import requests
import logging as log

import framework.database.database as database
from framework.io.io import IoType, Io





class WeatherManager(Io):

    def __init__(self, name: str, actions, zipcode):

        super().__init__(name, IoType.OUTPUT, actions, [])

        self.api_key = "dc5ae0780270feb4057d1d979bdc7307"
        self.units = "imperial"
        self.country_code = "us"
        self.zipcode = zipcode
        self.request = f"https://api.openweathermap.org/data/2.5/forecast?zip={self.zipcode},{self.country_code}&units={self.units}&appid={self.api_key}"
        self.table_name = "AC_webapp_weatherdata"

        self.init_weather_table()

    def call_api(self) -> dict:
        """
        Uses the python requests library to make a API response and returns a dict representing the data as it is stored
        in a JSON file.

        :return: dict representing the data stored in as JSON
        """

        try:
            api_request = requests.get(self.request)

            if api_request.status_code == 200:

                result = api_request.json()
                for row in result["list"]:
                    database.insert_data(self.table_name, {"date_time": row["dt"], "temperature": row["main"]["temp"],
                                                           "min_temperature": row["main"]["temp_min"], "max_temperature": row["main"]["temp_max"],
                                                           "humidity": row["main"]["humidity"], "weather_label": row["weather"][0]["main"],
                                                           "weather_description": row["weather"][0]["description"],
                                                           "cloudiness_level": row["clouds"]["all"], "wind_speed": row["wind"]["speed"]})

            else:
                warning = "FAILED: API response did not return status code 200"
                log.getLogger().critical(warning)
                print(warning)

        except Exception as ex:

            ex_string = f"CRITICAL: failed to get response for API request: '{self.request}'\nException: {ex}"
            print(ex_string)
            log.getLogger().critical(ex_string)

        return {}

    def store_weather_data(self):
        """ Retrieves the weather data from the openWeather api then stores the desired information in database"""


        weather_data = self.call_api()["list"]
        if weather_data == {}:
            database.clear_data_in_table("weather")
            for entry in weather_data:

                try:
                    data = {"date_time": entry["dt_txt"], "temperature": entry["main"]["temp"], "humidity": entry["main"]["humidity"],
                            "min_temperature": entry["main"]["temp_min"], "max_temperature": entry["main"]["temp_max"],
                            "weather_label": entry["weather"][0]["main"], "weather_description": entry["weather"][0]["description"],
                            "cloudiness_level": entry["clouds"]["all"], "wind_speed": entry["wind"]["speed"]}
                    database.insert_data(self.table_name, data)

                except:

                    ex_string = "FAILED: could not find or store all weather data from the openWeather API call\n"
                    print(ex_string)
                    log.getLogger(ex_string)

    def init_weather_table(self) -> None:
        """ Creates a table in the database to store the weather information """

        column_info = {"date_time": "TEXT", "temperature": "REAL", "min_temperature": "REAL", "max_temperature": "REAL",
                       "humidity": "INTEGER", "weather_label": "TEXT", "weather_description": "TEXT",
                       "cloudiness_level": "INTEGER", "wind_speed": "REAL"}
        database.create_table(self.table_name, column_info, True)

    def update_from_database(self):

        temp_zipcode = database.select_data("Settings", database.ResultCount.ONE, columns=["Value"], where="Setting_name LIKE 'zipcode'")
        if self.zipcode != temp_zipcode:
            self.zipcode = temp_zipcode

