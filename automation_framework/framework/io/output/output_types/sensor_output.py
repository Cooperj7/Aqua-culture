from collections import OrderedDict
from typing import Union
import logging as log

from framework.database import database
from framework.io.io import IoType
from framework.io.output.output import Output

from datetime import datetime


class SensorOutput(Output):

    def __init__(self, name: str, actions: OrderedDict, output_pins: list, database_name: str, table_name: str,
                 columns: [], value_shift: chr, target_value: Union[int, float], target_range: Union[int, float],
                 good_reading_interval: int, max_value: Union[float, int] = None, min_value: Union[float, int] = None):
        """
        Represents an output controlled by the readings from a sensor such as co2 or temperature sensor. Currently this
        only supports sensors that output a numerical value ie. '900' '10.2'.

        :param name: name of output ex. "co2-0", "heater-10", "ac-0"
        :param actions: dictionary of methods for the object to execute and how often to do it
            {"method_name": 5, "method_name1": 10} method_name() will be executed every 5 seconds and method_name1()
            will be executed every 10 seconds
        :param output_pins: pins linked to output object
        :param database_name: name of the database to get sensor data from
        :param table_name: name of the table in the database to get sensor data from
        :param columns: columns in database table to get data from
        :param value_shift: physical output will cause the value to increase or decrease, actual value = '+' or '-'.
            EX. heater causes temperature to increase so value_shift = "+"
        :param target_value: the target value to aim for; the mid point
        :param target_range: the accepted range target_value +/- target_range
        :param good_reading_interval: oldest a sensor reading can be for it to be valid
        :param max_value: max value to turn off relay at
        :param min_value: min value to turn off relay at
        """

        log.getLogger().debug(f"STARTING to create a sensor output named '{name}'...")

        super().__init__(name, actions, output_pins)

        self.value = 0
        self.modulation_point = -1
        self.sensor_values = None
        self.gpio_controller = None

        self.database_name = database_name
        self.table_name = table_name
        self.columns = columns

        self.value_shift = value_shift
        self.target_value = target_value
        self.target_range = target_range

        self.good_reading_interval = good_reading_interval

        self.max_value = max_value
        self.min_value = min_value

        self.blocking_outputs = {}

        log.getLogger().debug(f"DONE to creating a sensor output named '{name}'")
        log.getLogger().debug("")

    def find_state(self) -> None:
        """ Finds if the output associated with this sensor should be on or off based on the following """

        log.getLogger().debug(f"STARTING find_state '{self.name}'")

        result = False
        # Check if this output should be off based on the state of a different output.
        # Ex. When the lights are off no co2 is needed so if lights are on the co2 output should be blocked from
        #   turning on.
        if not self.check_blocking_output():

            # Make sure the make sure the sensor readings are current enough to be considered valid
            if self.validate_sensor_reading():

                # Format will be ["date_and_time", sensor_value]
                self.value = self.sensor_values[1]

                # This block is for outputs that decrease the value related to this sensor such as
                # ac, dehumidifier, water chiller...
                if self.value_shift == '-':

                    if self.modulation_point == -1:

                        range_min = self.target_value - self.target_range
                        if self.value <= range_min:
                            self.modulation_point = 1
                            result = False
                        elif self.value >= range_min:
                            result = True

                    elif self.modulation_point == 1:

                        range_max = self.target_value + self.target_range
                        if self.value >= range_max:
                            self.modulation_point = -1
                            result = True
                        elif self.value <= range_max:
                            result = False

                # This block is for outputs that increase the value related to this sensor such as
                # heaters
                elif self.value_shift == '+':

                    if self.modulation_point == -1:

                        range_min = self.target_value - self.target_range
                        if self.value <= range_min:
                            self.modulation_point = 1
                            result = True

                        elif self.value <= range_min:
                            result = False

                        else:
                            result = self.state

                    elif self.modulation_point == 1:

                        range_max = self.target_value + self.target_range
                        if self.value < range_max:
                            result = True

                        elif self.value >= range_max:
                            self.modulation_point = -1
                            result = False

                        else:
                            result = self.state

                else:
                    raise ValueError(f"The variable 'value_shift' should be set to '-' or '+' for {self.name}")

            else:

                # Senor reading is invalid so keep the output off
                result = False
                print(f"Value is not valid for {self.name}. Turning output off.")
                log.getLogger().debug(f"Value is not valid. Turning output off.")

        else:

            # This output is being block because of the state of a different output
            result = False
            log.getLogger().debug(f"BLOCKED by an output. Turning output off.")

        if self.state != result:
            self.state = result
            self.toggle_state()

        else:

            if self.gpio_controller.get_pin_state(self.output_pins[0]) != self.state:

                log.getLogger().critical(f"!SenorOutput: {self.name} was not in the correct state!")
                self.toggle_state()

        log.getLogger().debug(f"DONE find_state '{self.name}'")

    def validate_sensor_reading(self) -> bool:
        """
        Checks to see if the sensor value is valid or not. A reading is invalid if it is 'None' or if the number of
        seconds since the reading is greater than the set interval.

        :return: if the sensor reading is valid or not
        """

        log.getLogger().debug(f"STARTING validate_sensor_reading '{self.name}'")

        if self.sensor_values is None:

            return False

        reading_timestamp = datetime.strptime(self.sensor_values[0], "%m/%d/%Y %H:%M:%S")
        now = datetime.now()

        sensor_value = self.sensor_values[1]

        time_since_last_reading = now - reading_timestamp
        if sensor_value is not None and time_since_last_reading.days == 0 and \
                time_since_last_reading.seconds <= self.good_reading_interval:

            log.getLogger().debug(f"Sensor reading is valid.")
            result = True

        else:

            log.getLogger().debug(f"The sensor reading not valid. It is older than set duration.")
            result = False

        log.getLogger().debug(f"DONE validate_sensor_reading '{self.name}'")

        return result

    def get_sensor_values(self):

        log.getLogger().debug(f"STARTING get_sensor_value '{self.name}'")

        self.sensor_values = database.get_sensor_reading(self.database_name, self.table_name, self.columns)

        log.getLogger().debug(f"DONE get_sensor_value '{self.name}'")

    def set_blocking_output(self, output: dict):

        log.getLogger().debug(f"STARTING set_blocking_output '{self.name}'")

        self.blocking_outputs = output

        log.getLogger().debug(f"DONE set_blocking_output '{self.name}'")

    def check_blocking_output(self) -> bool:

        log.getLogger().debug(f"STARTING check_blocking_output '{self.name}'")

        result = False
        if len(self.blocking_outputs) > 0:

            for blocking_output in self.blocking_outputs.keys():

                # If the state of the blocking output is on or True then turn off this sensor output.
                blocking_state = self.blocking_outputs[blocking_output]
                if blocking_output.state == blocking_state:

                    log.getLogger().debug(f"Blocked by {blocking_output.name}")
                    result = True
                    break

        log.getLogger().debug(f"DONE find_state '{self.name}'")

        return result

    def toggle_state(self):

        log.getLogger().debug(f"STARTING toggle_state '{self.name}'")

        self.gpio_controller.toggle_pins(self.output_pins, self.state)

        log.getLogger().debug(f"DONE toggle_state '{self.name}'")

    def print_state(self):

        pin_states = {}
        for pin in self.output_pins:
            pin_states[pin] = self.gpio_controller.get_pin_state(pin)

        print(f"{self.name} state:{self.state} | values:{self.sensor_values} | modulation point:{self.modulation_point},"
              f" {pin_states}")

# def safety_check(self):
#
#     if self.value > self.max_value or self.value < self.min_value:
#
#         if self.value_shift == '+':
#
#             log.getLogger().critical(f"Sensor value for {self.name} is to high. Max value is {self.max_value} and "
#                                      f"the current value is {self.value}. Turning relay off.")
#
#         if self.value > self.min_value:
#
#             if self.value_shift == '-':
#
#                 log.getLogger().critical(
#                     f"Sensor value for {self.name} is to low. Low value is {self.min_value} and "
#                     f"the current value is {self.value}. Turning relay off.")
