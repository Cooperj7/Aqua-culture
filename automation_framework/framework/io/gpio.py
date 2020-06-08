"""
A controller to handle all hardware IO using the raspberrypi GPIO pins
"""

import RPi.GPIO as gpio
import logging as log


class GPIOController:

    valid_output_pins = [7, 11, 12, 13, 15, 16, 18, 22, 29, 31, 32, 33, 36, 37]

    def __init__(self):
        """
        A wrapper class for RPi.GPIO used to handle GPIO functions on the raspberry pi
        """

        log.getLogger().debug("Initializing io controller...")
        gpio.setwarnings(False)
        gpio.setmode(gpio.BOARD)

        log.getLogger().debug("Done setting mode")

    def init_gpio(self, outputs):

        log.getLogger().debug("Done initializing outputs")

        self.validate_pins(outputs)
        self.setup_output_pins(outputs)
        self.setup_input_pin(outputs)
        for output in outputs:
            self.toggle_pins(output.output_pins, output.state)

        log.getLogger().debug("Done initializing gpio")

    def toggle_pins(self, pins: list, state: bool) -> None:
        """
        Switches the pin state to the current state of the object
        :param pins: pin numbers to change state
        :param state: state the pins should be set to
        """

        log.getLogger().debug(f"STARTING toggle_state 'GPIOController'")
        if state:
            self.turn_pins_on(pins)
        else:
            self.turn_pins_off(pins)

        log.getLogger().debug(f"DONE toggle_state 'GPIOController'")

    def toggle_pin(self, pin: int, state: bool) -> None:
        """
        Turns the pin on or off based on the given state
        :param pin: the pin to turn on or off
        :param state: the state ot set the pin to
        """

        if state:
            self.turn_pin_on(pin)
        else:
            self.turn_pin_off(pin)

    @staticmethod
    def setup_output_pins(outputs: list) -> None:
        """
        Used to setup pins for each output in the list to be used as an output
        :param outputs: a list of outputs with pins to setup
        """

        for output in outputs:
            for pin in output.output_pins:
                log.getLogger().debug(f"Setting pin '{pin}' as an output pin for '{output.name}'")
                gpio.setup(pin, gpio.OUT)

    @staticmethod
    def setup_output_pin(pin: int) -> None:
        """
        Used to setup pins for each output in the list to be used as an output
        :param outputs: a list of outputs with pins to setup
        """

        log.getLogger().debug(f"Setting pin '{pin}' as an output")
        gpio.setup(pin, gpio.OUT)

    def setup_input_pin(self, outputs) -> None:
        """
        Checks clock_outputs for a block_button being set. If this is set a digital input pin is setup. If the digital
        input returns True the output will be set to False (off) for the set duration.
        :param outputs: outputs that potentially require input pin to be setup
        """

        for output in outputs:

            if output.__class__.__name__ == "ClockOutput" and output.block_button_pin is not None:
                log.getLogger().debug(f"Block button setup on pin {output.block_button_pin}")
                self.setup_digital_input(output.block_button_pin)

    @staticmethod
    def setup_digital_input(input_pin: int) -> None:
        """
        Sets a pin to be used as a digital input
        :param input_pin: pin to listen on for digital input
        """

        log.getLogger().debug(f"Setting pin '{input_pin}' as a digital input'")
        gpio.setup(input_pin, gpio.IN, pull_up_down=gpio.PUD_UP)

    @staticmethod
    def turn_pin_off(pin: int):
        gpio.output(pin, gpio.LOW)

    @staticmethod
    def turn_pin_on(pin: int):
        gpio.output(pin, gpio.HIGH)

    def turn_pins_on(self, pins: list) -> None:
        """
        Turns pins in the list to the high state
        :param pins: list of pin numbers to turn on
        """

        for pin in pins:
            # When using relays a low signal completes the circuit on the relay board and creates a high signal
            self.turn_pin_on(pin)

    def turn_pins_off(self, pins: list) -> None:
        """
        Turns pins in the list to the low state
        :param pins: list of pin numbers to turn off
        """

        for pin in pins:
            # When using relays a high signal completes the circuit on the relay board and creates a low signal
            self.turn_pin_off(pin)

    def validate_pins(self, outputs: list) -> None:
        """
        A container method to hold all methods to validate io pins
        :param outputs: a list of output objects with pins
        """

        self.verify_no_duplicate_pins(outputs)
        self.verify_output_pins(outputs)

    @staticmethod
    def verify_no_duplicate_pins(outputs: list) -> None:
        """
        Checks to make sure pins are not being assigned twice
        :param outputs: list of outputs with pins
        """

        log.getLogger().debug("Checking pins for duplicate assignments...")

        used_pins = []
        for output in outputs:
            for pin in output.output_pins:

                if pin not in used_pins:
                    used_pins.append(pin)

                else:
                    raise ValueError(f"Pin: {str(pin)} is already assigned")

        log.getLogger().debug("Done checking pins for duplicate assignments")

    def verify_output_pins(self, outputs: list) -> None:
        """
        Only certain pins on the raspberry pi header can be set as outputs. Check to make sure the pins being used as
        outputs are valid output pins.
        :param outputs: list of outputs with pins
        """

        log.getLogger().debug("Making sure outputs are only assigned to output pins...")

        for output in outputs:
            for pin in output.output_pins:

                if pin in self.valid_output_pins:
                    log.getLogger().debug(f"Pin {pin} is a valid output pin")
                else:
                    raise ValueError(f"Pin {pin} cannot be used as an output pin")

        log.getLogger().debug("Done making sure outputs are only assigned to output pins")

    @staticmethod
    def get_pin_state(pin: int) -> bool:
        """
        Gets the current state of the pin
        :param pin: number pin to check
        :return: the state of the pin (True/False)
        """

        return gpio.input(pin)

    def check_pin_voltage(self, pin: int, expected_state: bool) -> bool:
        """
        Validates the current state of the pin by comparing the pin state to the objects state
        :param pin: number pin to check
        :param expected_state: the expected state of the object
        :return: if the pin state matches the object state
        """

        if expected_state == self.get_pin_state(pin):
            return True
        else:
            log.getLogger().critical(f"FALSE pin: {str(pin)} is NOT set to {expected_state}")
            return False

    @staticmethod
    def check_push_button(pin: int) -> bool:
        """
        Checks if a push button has been pushed down or not
        :param pin: pin number to listen for the button on
        :return: if the button was pressed or not
        """

        # Using pull up resistor so low mean button was pressed
        if gpio.input(pin) == gpio.HIGH:
            return False
        else:
            log.getLogger().debug(f"Button pressed for {pin}")
            return True
