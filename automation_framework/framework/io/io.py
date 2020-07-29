"""
This the parent class to input and output objects
"""
import inspect
import time
from enum import Enum

from framework.managers.email import EmailController
from framework.time.timer import Timer

from datetime import datetime


class IoType(Enum):

    OUTPUT = "OUTPUT"
    INPUT = "INPUT"
    MANGER = "MANAGER"


class Io:

    def __init__(self, name: str, io_type: IoType, actions: dict, output_pins: list):
        """
        Init Io object

        :param name: name of the output
        :param actions: method name/how often to call method key/value pair
        :param output_pins: output pins being used by the output
        """

        self.gpio_controller = None
        self.timers = {}
        self.name = name
        self.io_type = io_type
        self.output_pins = output_pins
        self.actions = self.build_actions_dict(list(actions.keys()))

        self.email_controller = None

        self.start_time = 0
        self.timer_name = ""

        # Instead of storing a timer object in the json just store the name and interval. That is all you need to create
        # a timer. To link timers to a method use the timer name as a key and the class method as a value to add to the
        # dictionary named actions in perform_actions() method for that class.
        self.timers = {}
        for key in actions.keys():
            self.timers[key] = Timer(name, actions[key])

    def check_time(self) -> dict:
        """
        Checks each of the timers owned by the output. The name of the timer is used as a key in the result dictionary
        and the value is if the output should be on or off.

        :return: if it is time for the output object to check and update it's state
        """

        results = {}
        for key in self.timers.keys():

            results[key] = self.timers[key].check_time()

        return results

    def build_actions_dict(self, actions_input: list) -> dict:
        """
        The purpose of this method is the preserve the order the actions in the json file. The actions or methods will
        be called in the order as they appear in the json file for the object in the 'actions' field. This is so the
        methods can later be called by perform_actions.

        :param actions_input: a list of methods that the input will call when running
        :return: method name (action name)/point to the method
        """

        # This is a map of of the method name (a string) to the method itself.
        actions = {}
        object_members = inspect.getmembers(self)
        for action in actions_input:

            action_found = False
            for member in object_members:

                if member[0] == action:

                    actions[action] = member[1]
                    action_found = True
                    break

            if not action_found:
                raise ValueError(f"'{action}' is not a method name found in '{self.name}' object type '{self.__class__}'")

        return actions

    def perform_actions(self, timer_results: dict) -> None:
        """
        This method is used to execute each of the actions this output should perform. Each action can have its own
        interval. self.actions is a python dictionary where the keys are method names and the value is the method
        itself. This ensures the name in the json matches to an actual method belonging to that class. This also makes
        it easy to setup the order and interval of actions in the json file.

        :param timer_results: results for each of the timers stored in the output
        :return: None
        """

        # Check each of the time_results. Each key is a function name from the given class.
        for key in timer_results.keys():

            # If the value is True call the method from the given class
            if timer_results[key]:
                self.actions[key]()

    def set_email_controller(self, email_controller: EmailController) -> None:

        pass

    def start_timer(self, timer_name):
        """
        Basic timer method for debugging. Call this method to store the timer name and start time.

        **Note: Only call this method one time before calling end_timer(). If called multiple times before calling end 

        :param timer_name:
        :return:
        """

        self.timer_name = timer_name
        self.start_time = time.time()

    def end_timer(self):

        print(f"{self.timer_name} took: {time.time() - self.start_time}")

    def test_execution_interval(self) -> None:
        """ Used for debugging. Shows the interval a method is being executed. """
        print(f"{self.name}: {datetime.now().strftime('%m/%d/%Y %H:%M:%S')}")