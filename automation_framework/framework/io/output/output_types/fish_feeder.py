from datetime import datetime

from framework.database.database import select_data, ResultCount
from framework.io.output.output_types.clock_output import ClockOutput


class FishFeeder(ClockOutput):

    def __init__(self, name: str, actions: dict, out_pins: list, feeding_time: int, feeding_amount: int):

        super().__init__(name, actions, out_pins, self.populate_weekly_schedule(int(feeding_time)))

        self.feeding_time = feeding_time
        self.feeding_amount = feeding_amount

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

    def populate_weekly_schedule(self, feeding_time):

        weekly_schedule = {}
        days_of_week = self.num_to_string.values()
        for day in days_of_week:
            weekly_schedule[day] = {"on_hour": feeding_time, "off_hour": feeding_time + 1}

        return weekly_schedule

    def update_from_database(self):

        temp_feeding_time = select_data("Settings", ResultCount.ONE, columns=["Value"], where="Setting_name LIKE 'fishfeeder_time'")
        if self.feeding_time != temp_feeding_time:
            self.feeding_time = temp_feeding_time

        temp_feeding_amount = select_data("Settings", ResultCount.ONE, columns=["Value"], where="Setting_name LIKE 'fishfeeder_amount'")
        if self.feeding_amount != temp_feeding_amount:
            self.feeding_amount = temp_feeding_amount