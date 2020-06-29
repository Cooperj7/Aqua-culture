from datetime import datetime

from framework.io.output.output_types.clock_output import ClockOutput


class FishFeeder(ClockOutput):

    def __init__(self, name: str, actions: dict, out_pins: list, feeding_time: int, feed_weight: int):

        super().__init__(name, actions, out_pins, self.populate_weekly_schedule())

        self.feeding_time = feeding_time
        self.feed_weight = feed_weight

        now = datetime.now()
        self.saved_day = now.day
        self.already_fed = False

    def find_state(self) -> None:

        # This class was made for with lights in mind. It will return true starting at the supplied
        # feeding time until an hour later. Have to make sure fish are only fed one time per day.
        state = super().find_state()

        # Check if it is time for feeding
        if state:

            # If the fish should be fed check the last time they were fed. If it is a new day then
            # feed the fish if not do nothing because it is the same day still.
            current_day = datetime.now().day
            if self.saved_day != current_day:

                self.saved_day = current_day
                self.feed_fish()

    def feed_fish(self):

        # TODO: Need to print fish feeder parts before this can be fully implemented
        pass

    def populate_weekly_schedule(self):

        weekly_schedule = {}
        days_of_week = self.num_to_string.values()
        for day in days_of_week:
            weekly_schedule[day] = {"on_hour": self.feeding_time, "off_hour": self.feeding_time + 1}

        return weekly_schedule