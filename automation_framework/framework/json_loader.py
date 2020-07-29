"""
Utilizes the data in the JSON files located in the resources folder. Mainly used
to create the output objects.
"""
import collections
import json

from framework.database.database_manager import DatabaseManager
from framework.io.output.output_types.fish_feeder import FishFeeder
from framework.managers.email import EmailController
from framework.io.input.sensors.multi_sensor import MultiSensor
from framework.io.output.output_types.clock_output import ClockOutput
from framework.io.output.output_types.sensor_output import SensorOutput
from framework.io.output.output_types.timer_output import TimerOutput
from framework.managers.plant_buddy import PlantBuddy
from framework.managers.weather import WeatherManager

path_to_clock_outputs = "./resources/json_files/outputs/clock_outputs/"
path_to_timer_outputs = "./resources/json_files/outputs/timer_outputs/"
path_to_sensor_outputs = "./resources/json_files/outputs/sensor_outputs/"

path_to_sensor_inputs = "./resources/json_files/inputs/sensors/"
path_to_email_info = "./resources/json_files/emails/"
path_to_managers = "./resources/json_files/managers/"
path_to_misc = "./resources/json_files/outputs/misc/"




def create_clock_output(file_name: str, block_button_pin: int = None, block_duration: int = None) -> ClockOutput:
    """
    Creates a clock output based on the given file name. This function looks in the
    resources folder a matching JSON file and creates an object.

    :param file_name: name of the JSON in resources/json_files/outputs/clock_outputs
    :param block_button_pin: pin to listen on for button input
    :param block_duration: how long to block the output for after the button is pressed
    :return: ClockOutput
    """

    path = path_to_clock_outputs + file_name
    with open(path, 'r') as json_file:
        data = json.load(json_file)

    return ClockOutput(data["name"], data["actions"], data["out_pins"], data["week_schedule"],
                       block_button_pin=block_button_pin, block_duration=block_duration)


def create_timer_output(file_name: str) -> TimerOutput:
    """
    Creates a timer output based on the given file name. This function looks in the
    resources folder a matching JSON file and creates an object.

    :param file_name: name of the JSON in resources/json_files/outputs/timer_outputs
    :return: TimerOutput
    """

    path = path_to_timer_outputs + file_name
    with open(path, 'r') as json_file:
        data = json.load(json_file, object_pairs_hook=collections.OrderedDict)

    return TimerOutput(data["name"], data["actions"], data["out_pins"], data["on_seconds"],
                       data["off_seconds"])


def create_multi_sensor(file_name: str) -> MultiSensor:
    """
    Creates a multi-sensor output based on the given file name. This function looks in the
    resources folder a matching JSON file and creates an object.

    :param file_name: name of the JSON in resources/json_files/inputs/sensors
    :return: MultiSensor
    """

    path = path_to_sensor_inputs + file_name
    with open(path, 'r') as json_file:
        data = json.load(json_file)

    return MultiSensor(data["name"], data["actions"],
                       data["database_table_name"], data["database_column_info"], data["serial_connection_string"],
                       data["alarm_values"], data["mac_address"], data["buadrate"], data["timeout"],
                       data["no_readings_limit"])


def create_sensor_output(file_name: str) -> SensorOutput:
    """
    Creates a sensor output based on the given file name. This function looks in the
    resources folder a matching JSON file and creates an object.

    :param file_name: name of the JSON in resources/json_files/outputs/sensor_outputs
    :return: SensorOutput
    """

    path = path_to_sensor_outputs + file_name
    with open(path, 'r') as json_file:
        data = json.load(json_file)

    return SensorOutput(data["name"], data["actions"], data["out_pins"],
                        data["table_name"], data["columns"], data["value_shift"], data["target_value"],
                        data["target_range"], data["good_reading_interval"], data["max_value"], data["min_value"])


def create_email_controller(file_name: str):
    """
    Creates a email controller object based on the given file name. A multi-sensor requires a email controller to send
     text alert when different alarms are tripped. This function looks in the
    resources folder a matching JSON file and creates an object.

    :param file_name: name of the JSON in resources/json_files/email
    :return: EmailController
    """

    path = path_to_email_info + file_name
    with open(path, 'r') as json_file:
        data = json.load(json_file)

        return EmailController(data["sender_email"], data["sender_password"], data["receiving_emails"])


def create_database_manager(file_name: str):
    """
    Creates a database manager object based on the given file name. Used to purge old data to keep system running fast.
    This function looks in the resources folder a matching JSON file and creates an object.

    :param file_name: name of the JSON in resources/json_files/managers
    :return: DatabaseManager
    """

    path = path_to_managers + file_name
    with open(path, 'r') as json_file:
        data = json.load(json_file)

        return DatabaseManager(data["name"], data["actions"], data["database_name"], data["max_data_age"])

def create_weather_manager(file_name: str):

    path = path_to_managers + file_name
    with open(path, 'r') as json_file:
        data = json.load(json_file)

        return WeatherManager(data["name"], data["actions"], data["zipcode"])

def create_fish_feeder(file_name: str):

    path = path_to_misc + file_name
    with open(path, 'r') as json_file:
        data = json.load(json_file)

        return FishFeeder(data["name"], data["actions"], data["out_pins"], data["feeding_time"], data["feeding_amount"])


def create_plant_buddy(file_name: str):

    path = path_to_managers + file_name
    with open(path, 'r') as json_file:
        data = json.load(json_file)

        return PlantBuddy(data["name"], data["actions"], data["sender_email"], data["sender_password"],
                          data["receiving_emails"], data["zipcode"], data["phone_num"])