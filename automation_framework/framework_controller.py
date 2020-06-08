"""
Gives something each of the classes to hook onto

1. Initialize the environment
2. Run tests
    If something is wrong send emails/text --> put the system in some sort of standby,
    let the user choose. Make modular, if one service not starting should not keep the rest of the
    system from trying. Some are dependent.
"""
from datetime import datetime
import logging as log

import framework.json_loader as json
from framework.io.gpio import GPIOController
from framework.io.io import IoType


def set_gpio_controller(outputs, gpio_controller: GPIOController) -> None:
    """
    Setter method to link the gpio_controller to each output. This is mostly for convenience when preforming gpio
    actions with an output.
    :param outputs: outputs that need access to gpio actions
    :param gpio_controller: the gpio controller being used
    """

    for output in outputs:

        if output.io_type == IoType.OUTPUT:

            output.set_gpio_controller(gpio_controller)



def main():

    # Create log
    now = datetime.now()
    date_time_formatted = now.strftime("%m_%d_%Y__%H_%M_%S")
    filename = f"logs/automation_log_{date_time_formatted}.log"
    log.basicConfig(filename=filename,
                    format="%(asctime)s %(message)s",
                    filemode='w')
    logger = log.getLogger()
    logger.setLevel(log.WARNING)

    # Create the gpio controller
    gpio_controller = GPIOController()
    log.getLogger().debug("GPIO controller created")

    # logger.debug("Initializing outputs...")

    # Creating sensor related objects to read sensors and control output relays
    multi_sensor = json.create_multi_sensor("multi_sensor.json")
    co2 = json.create_sensor_output("co2.json")
    heater = json.create_sensor_output("heater.json")

    # Creating output objects to control output relays
    big_tent_lights = json.create_clock_output("big_tent_lights.json")
    small_tent_lights = json.create_clock_output("small_tent_lights.json")
    exhaust_fan = json.create_timer_output("exhaust_fan.json")

    # Creating email controller object to sent alert emails
    email_controller = json.create_email_controller("email_info.json")

    # Managers
    database_manager = json.create_database_manager("database_manager.json")

    # Set a blocking output so co2 is not released when blower is on
    co2.set_blocking_output({exhaust_fan: True, big_tent_lights: False})

    outputs = [big_tent_lights, small_tent_lights, exhaust_fan, heater]

    log.getLogger().debug("Done initializing outputs")

    # Set the output pins being used and pass the gpio_controller to each output
    gpio_controller.init_gpio(outputs)
    set_gpio_controller(outputs, gpio_controller)
    multi_sensor.set_email_controller(email_controller)

    outputs.append(multi_sensor)
    outputs.append(database_manager)

    # logger.debug("Starting main loop")
    while True:

        # Go through each of the outputs
        for output in outputs:

            # Check if enough time has passed since the action was last preformed
            timer_results = output.check_time()
            output.perform_actions(timer_results)


if __name__ == "__main__":
    main()
