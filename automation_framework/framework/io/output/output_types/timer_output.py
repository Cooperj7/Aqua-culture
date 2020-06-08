"""
This class is to create an output object that is toggled based on time
"""

import logging as log
from collections import OrderedDict

from framework.io.io import IoType
from framework.io.output.output import Output


class TimerOutput(Output):

    def __init__(self,  name: str, actions: OrderedDict, output_pins: list,
                 on_seconds: int, off_seconds: int):
        """
        Represents an output controlled by a timer. You set an on and off interval.

        :param name: name of output ex. "co2-0", "heater-10", "ac-0"
        :param actions: dictionary of methods for the object to execute and how often to do it
            {"method_name": 5, "method_name1": 10} method_name() will be executed every 5 seconds and method_name1()
            will be executed every 10 seconds
        :param output_pins: pins linked to output object
        :param on_seconds: number of seconds to keep the output object on
        :param off_seconds: number of seconds to keep the output object off
        """

        log.getLogger().debug(f"STARTING to create a timer based output named '{name}'...")

        super().__init__(name, actions, output_pins)

        self.state = True
        self.on_seconds = on_seconds
        self.off_seconds = off_seconds
        self.current_timer = on_seconds

        log.getLogger().debug(f"Name: {name} | out_pins: {output_pins} | on_seconds: {on_seconds} off_seconds: {off_seconds}")
        log.getLogger().debug(f"DONE creating a timer based output named '{name}'")
        log.getLogger().debug("")

    def find_state(self) -> None:
        """
        Finds the state of the timer using the number of seconds for each part of the cycle
        """

        self.current_timer -= self.timers["find_state"].interval

        if self.current_timer <= 0:

            if self.get_state():
                self.current_timer = self.off_seconds
                result = False

            else:
                self.current_timer = self.on_seconds
                result = True

        else:
            result = self.state

        if result != self.state:
            self.state = result
            self.gpio_controller.toggle_pins(self.output_pins, self.state)
