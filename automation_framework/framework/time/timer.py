"""
The purpose of this class is to avoid calling the sleep methods. When you call the sleep
method the instructions make the program wait. This also makes it easier to set different
intervals for different outputs. Each input and output group gets a timer. In most cases
the interval of the sensor should match the output but it does not have to.
"""

import time


class Timer:

    def __init__(self, name: str, interval: int):

        self.interval = interval
        self.name = name
        self.previous_seconds = 0
        self.current_seconds = 0

    def check_time(self) -> bool:
        """
        Simulates a timer using the current time from epoch and the previous time from epoch when this timer last went
        off.

        :return: if the output should check its state
        """

        # Set the current time
        self.current_seconds = time.time()

        # This hopefully prevents potential overflow problems
        if self.previous_seconds < 0:
            self.previous_seconds = 0

        # If the current time from epoch minus the time from epoch in the previous check is greater
        # then the interval then you know it has been at least as many seconds as the interval
        if self.current_seconds - self.previous_seconds > self.interval:

            # Now that the interval has been reached set the previous time from epoch to the current time. This is the
            # same as resetting the timer
            self.previous_seconds = self.current_seconds
            return True

        else:
            return False
