"""
Tests to validate the output configuration data in the JSON files
"""

import os
import logging as log

import framework.json_loader as json

log.basicConfig(filename="automation_framework_system_test.log",
                format="%(asctime)s %(message)s",
                filemode='w')
logger = log.getLogger()
logger.setLevel(log.DEBUG)

def check_clock_outputs() -> None:
    """
    Displays the state of the clock output for a 24 hour period
    """

    print("Testing clock based outputs\n")

    # Create the output objects using the JSON files
    clock_output_names = os.listdir(json.path_to_clock_outputs)
    clock_outputs = []
    for output_name in clock_output_names:
        clock_outputs.append(json.create_clock_output(output_name))

    # Show the on/off times for a 24 hours period
    for clock_output in clock_outputs:
        print(f"    {clock_output.name}")

        for day in range(8):
            print(f"    {clock_output.num_to_string[day]}")
            for hour in range(24):
                print(f"        {hour}: {clock_output._test_find_state(hour, day)}")

            print()

    print("Done testing clock based outputs\n\n")


def check_timer_outputs() -> None:
    """
    Validates the time object by running for a full on/off cycle while counting states
    """
    print("Testing timer based outputs\n")

    timer_output_names = os.listdir(json.path_to_timer_outputs)

    # Create outputs
    timer_outputs = []
    for output_name in timer_output_names:
        timer_outputs.append(json.create_timer_output(output_name))

    # Run the timer for 1 on/off cycle
    for timer_output in timer_outputs:

        print(f"    {timer_output.name}")

        on_max = timer_output.on_seconds
        off_max = timer_output.off_seconds
        total_count = on_max + off_max
        on_count = 0
        off_count = 0

        for i in range(total_count):
            timer_output.find_state()


        # Next the timer output should complete the off cycle
        # for i in range(off_max):
        #
        #     timer_output.find_state()
        #
        #     if timer_output.state:
        #         raise ValueError(
        #             f"Failure on number: {i} The timer has completed the on cycle so the off cycle should have run uninterrupted.")
        #     else:
        #         off_count += 1
        #
        # # If the timer output start on the whole on cycle should be completed at first
        # for i in range(on_max):
        #
        #     timer_output.find_state()
        #
        #     if timer_output.state:
        #         on_count += 1
        #     else:
        #         raise ValueError(f"Failure on number: {i} If the timer is starting in the on state it should not return false until the whole" +
        #                          " on cycle has been completed")

        if total_count != on_count + off_count:
            raise ValueError("Number of on + off count does not equal the total cycle")

        print(f"        Total count: {total_count} | On counts: {on_count} | Off counts: {off_count}")

    print("\nDone Testing timer based outputs\n")


def check_sensor_outputs():
    pass

def check_system():
    """
    Checks the system as a whole
    """

    # Validate config data in JSON files
    check_clock_outputs()
    #check_timer_outputs()

check_system()
