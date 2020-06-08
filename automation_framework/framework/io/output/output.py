"""
This is the parent class to all outputs. This contains common variables and methods
across all outputs.
"""
from collections import OrderedDict

from framework.database.database import ResultCount, path_to_databases, update_output_state, select_data
from framework.io.gpio import GPIOController
from framework.io.io import Io, IoType
import logging as log


class Output(Io):

    def __init__(self, name: str, actions: OrderedDict, out_pins: list):
        """
        Base class of all outputs

        :param name: name of output ex. "co2-0", "heater-10", "ac-0"
        :param actions: dictionary of methods for the object to execute and how often to do it
            {"method_name": 5, "method_name1": 10} method_name() will be executed every 5 seconds and method_name1()
            will be executed every 10 seconds
        :param out_pins: pins linked to output object
        """

        super().__init__(name, IoType.OUTPUT, actions, out_pins)
        self.gpio_controller = None
        self.state = False

    def get_state(self) -> bool:
        """
        Getter for the state of the output object
        :return: if the output is on or off
        """

        return self.state

    def confirm_state(self) -> None:
        """
        Checks the state of each output pin against the variable stored in the object then logs the result
        """

        for pin in self.output_pins:

            # If the current voltage of the pin does not match the expected voltage then change the pin to that state
            if self.gpio_controller.check_pin_voltage(pin, self.state):
                log.getLogger().debug(f"{self.name} pin: {pin} is correctly set to {self.state}")

            else:
                log.getLogger().error(f"{self.name} pin: {pin} should be {self.state} but is {not self.state}")

    def set_gpio_controller(self, gpio_controller: GPIOController) -> None:
        """
        Setter for gpio_controller. There should only be one gpio object per raspberry pi so pass each output object a
        reference to same object.
        :param gpio_controller: the gpio object to preform gpio actions
        """

        self.gpio_controller = gpio_controller

    def print_state(self):
        print(f"{self.name}: {self.state}")

    def log_state(self):

        update_output_state("sensors.db", self.name, self.state)

    def print_log_state(self):
        print(select_data(path_to_databases + "sensors.db", "output_states", ResultCount.ALL))
