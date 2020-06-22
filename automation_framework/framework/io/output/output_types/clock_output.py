from collections import OrderedDict
from datetime import datetime
import logging as log

from framework.io.output.output import Output


class ClockOutput(Output):

    num_to_string = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Wednesday", 4: "Thursday", 5: "Friday",
                     6: "Saturday", 7: "Sunday"}

    def __init__(self, name: str, actions: OrderedDict, out_pins: list, week_schedule: OrderedDict,
                 block_button_pin: int = None, block_duration: int = None):
        """
        Represents an output switched based on the the time of day. An example is lights they turn on at a certain time
        of the day and they turn off at a certain time of day. Each day of the week can be set differently.

        :param name: name of output ex. "co2", "heater-10", "ac-0"
        :param actions: dictionary of methods for the object to execute and how often to do it
            {"method_name": 5, "method_name1": 10} method_name() will be executed every 5 seconds and method_name1()
            will be executed every 10 seconds
        :param out_pins: pins linked to output object
        :param week_schedule: on and off times for each day of the week. EX:
              "week_schedule": {"Monday": {"on_hour": 12, "off_hour":  0},
                    "Tuesday": {"on_hour": 12, "off_hour":  0},
                    "Wednesday": {"on_hour": 12, "off_hour":  0},
                    "Thursday": {"on_hour": 12, "off_hour":  0},
                    "Friday": {"on_hour": 12, "off_hour":  0},
                    "Saturday": {"on_hour": 12, "off_hour":  0},
                    "Sunday": {"on_hour": 12, "off_hour":  0}
        :param block_button_pin: (optional) listen to this pin for a button to be pressed
        :param block_duration: (optional) if the above button is pressed keep the output object off for this duration
        """

        log.getLogger().debug(f"STARTING to create a clock based output named '{name}'...")

        super().__init__(name, actions, out_pins)

        self.day_of_week = None
        self.on_hour = None
        self.off_hour = None

        self.week_schedule = week_schedule

        self.block_button_pin = block_button_pin
        self.block_duration = block_duration
        self.block_timer = 0

        self._validate_hour()
        self._log_on_off_hour()
        self.day_of_week = self.get_current_day()
        self.set_on_off_time()

        log.getLogger().debug(f"Name: {name} | out_pins: {out_pins}")
        log.getLogger().debug(f"DONE creating a clock based output named '{name}'")
        log.getLogger().debug("")

    @staticmethod
    def get_current_day() -> int:
        """
        Getter for the current day of the week. Used to set the on/off hour for the output.
        :return: The current day of the week represented as an int (Monday=0,...,Sunday=6)
        """

        return datetime.now().weekday()

    def set_on_off_time(self) -> None:
        """ Sets the on and off hour for a clock output based on the day of the week """

        self.on_hour = self.week_schedule[self.num_to_string[self.day_of_week]]["on_hour"]
        self.off_hour = self.week_schedule[self.num_to_string[self.day_of_week]]["off_hour"]

    def find_state(self) -> None:
        """ Using the current time and the on/off hours find the current state of the output """

        now = datetime.now()

        # Before checking the state make sure the right on/off hours are set by checking if the day has changed
        current_day = now.weekday()
        if self.day_of_week != current_day:
            self.day_of_week = current_day
            self.set_on_off_time()

        current_hour = now.hour
        if self.on_hour == self.off_hour:
            result = True

        elif self.off_hour < self.on_hour:
            if current_hour >= self.on_hour:
                result = True
            elif current_hour >= self.off_hour:
                result = False
            else:
                result = True

        else:
            if current_hour >= self.on_hour and current_hour < self.off_hour:
                result = True
            else:
                result = False

        # If the block_timer is None that means there is no block button set so it will never by blocked. If the
        # block_timer is not None then the gpio should only be allowed to update if the output is not being blocked.
        if result != self.state and self.block_timer <= 0:

            self.state = result
            self.gpio_controller.toggle_pins(self.output_pins, self.state)

    def check_block_button(self) -> None:
        """
        Checks the button used to block the output. If the output is blocked it will be set to false for the duration
        set in block_duration
        """

        if self.block_button_pin is None:
            raise ValueError("'block_button_pin' must be set in order to turn off lights with a button")

        if self.block_duration is None or self.block_duration == 0:
            raise ValueError("'block_duration' must be greater than 0 in order to block output")

        # If the button is being pressed then the block timer should be started
        if self.gpio_controller.check_push_button(self.block_button_pin):

            log.getLogger().debug(f"Block button for '{self.name}' was pressed")
            # If the timer is 0 or less reset the block_timer
            if self.block_timer <= 0:
                self.block_timer = self.block_duration

            # If timer is already counting down do nothing

        else:

            # If the button is not being pressed subtract the interval that the button is checked
            if self.block_timer > 0:
                self.block_timer -= self.actions["check_block_button"].interval

        # If the block_timer is active set the state to False
        if self.block_timer > 0:

            self.state = False
            self.gpio_controller.toggle_pins(self.output_pins, self.state)
            log.getLogger().debug(f"Blocking {self.name} duration left: {self.block_timer}")


    def _test_find_state(self, hour: int, day: int) -> bool:
        """
        A method made for testing purposes. Instead of waiting 24 hours to see one cycle take in the hour as an input.
        :param hour: hour of the day to test
        :return: if the output should be on or off at that hour
        """

        self.day_of_week = day
        self.set_on_off_time()

        current_hour = hour
        if self.on_hour == self.off_hour:
            return True

        elif self.off_hour < self.on_hour:
            if current_hour >= self.on_hour:
                return True
            elif current_hour >= self.off_hour:
                return False
            else:
                return True

        else:
            if current_hour >= self.on_hour and current_hour < self.off_hour:
                return True
            else:
                return False

    def _log_on_off_hour(self) -> None:
        """ Logs if the clock output should be on or off for each hour of the day for each day of the week """

        log.getLogger().debug(f"Logging on/off hours for {self.name}")
        for day in range(8):

            log.getLogger().debug("")
            log.getLogger().debug(f"    {self.num_to_string[day]}")
            for hour in range(24):

                log.getLogger().debug(f"        {hour}: {self._test_find_state(hour, day)}")

        log.getLogger().debug("")

    def _validate_hour(self) -> None:
        """
        Makes sure the set hours in the weekly schedule are valid. It also checks the format of the schedule itself.
        The weekly schedule format should match the example below. The on/off times should use military time valid
        hours are 0-23.

        Weekly schedule example:

            "week_schedule": {"Monday": {"on_hour": 1, "off_hour":  10},
                              "Tuesday": {"on_hour": 1, "off_hour":  10},
                              "Wednesday": {"on_hour": 1, "off_hour":  10},
                              "Thursday": {"on_hour": 1, "off_hour":  10},
                              "Friday": {"on_hour": 1, "off_hour":  10},
                              "Saturday": {"on_hour": 1, "off_hour":  10},
                              "Sunday": {"on_hour": 1, "off_hour":  10}
            }
        """

        # Check there are 7 days for the whole week
        if not len(self.week_schedule) == 7:
            raise ValueError(f"The weekly schedule for {self.name} should contain 7 days or dictionaries "
                             f"(1 dictionary for each day) but {len(self.week_schedule)} were found")

        # Check the 7 dictionaries are valid days of the week
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for key in self.week_schedule:

            if key not in days_of_week:
                raise ValueError(f"{key} is not a valid day of the week")

            else:
                days_of_week.remove(key)

        # If there are any days left in the list those days did not have a matching key in the schedule
        if len(days_of_week) > 0:
            raise ValueError(f"The supplied schedule does not contain all 7 days of the week. Could not find times for"
                             f" {days_of_week}")

        # Check that all of the hours are between 0 and 23
        for day in self.week_schedule:

            if len(self.week_schedule[day]) != 2:
                raise ValueError(f"Found more than 2 entries for {day}. There should only be an on and off hour "
                                 f"for each day.")

            for setting in self.week_schedule[day]:

                if not (self.week_schedule[day][setting] >= 0 or self.week_schedule[day][setting] <= 23):
                    raise ValueError(f"The {setting} setting for {day} is invalid. Valid hours are 0-23.")
