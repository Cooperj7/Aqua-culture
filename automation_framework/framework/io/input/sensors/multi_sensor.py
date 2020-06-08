from datetime import datetime
from collections import OrderedDict
import time
from subprocess import Popen, PIPE

import logging as log
from serial import Serial

from framework.email import EmailReasons, EmailController
from framework.io.io import Io, IoType
from framework.database import database


class MultiSensor(Io):

    def __init__(self, name: str, actions: OrderedDict, database_name: str, database_table_name: str,
                 database_column_info: dict, serial_connection_name: str, alarm_values: dict,
                 sensor_mac_address: str = None, baudrate: int = 9600, timeout: int = 30, no_readings_limit: int = 5):
        """
        Used to represent a sensor that provides multiple values such as temperature, humidity, light level and or co2
        level. All data is sent over a serial connection.

        * If the connection to the sensor is lost 0 bytes will constantly be returned. If this value is reached the
            connection is assumed to be lost so try to restart it.

        :param name: name of the sensor
        :param io_type: type of object ex input, output or manager
        :param actions: the method names and the intervals to execute them ex. {"find_state": 5}
        :param database_name: name of the database to store values in
        :param database_table_name: name of the table in the database to store sensor values in
        :param database_column_info: column name and data type for each column
            ex. {"date_time": "TEXT", "temperature": "REAL"}
        :param serial_connection_name: name or path of the connection to use
        :param alarm_values: max and min values to send alert notifications at
        :param sensor_mac_address: MAC address of the bluetooth module on the sensor
        :param baudrate: communication rate for the serial connection
        :param timeout:
        :param no_readings_limit: max number of times to not get any data from the sensor *
        """

        log.getLogger().debug(f"STARTING to create a multi-sensor named {name}")

        super().__init__(name, IoType.INPUT, actions, [])
        self.sensor_values = None

        # Info for serial connection to arduino
        self.serial_connection_name = serial_connection_name
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None
        self.sensor_mac_address = sensor_mac_address
        self.serial_port_process = None

        self.bytes_in_waiting = 0
        self.no_bytes_count = 0
        self.no_readings_limit = no_readings_limit

        self.database_name = database_name
        self.table_name = database_table_name
        self.database_column_info = database_column_info
        database.init_database(database_name, database_table_name, database_column_info, True)

        # Create the serial connection
        self.start_serial_connection()

        self.sensor_reading_is_valid = None
        self.alarm_values = alarm_values

        self.serial_connection_restart_count = 0

        log.getLogger().debug(f"DONE creating a multi-sensor named {self.name}")

    # Methods for handling the serial connection
    def start_serial_connection(self) -> None:
        """
        Starts a serial connection to a multi-sensor.

        :return: None
        """

        log.getLogger().warning(f"STARTING start_serial_connection {self.name}")

        if self.sensor_mac_address is not None:

            connect_to_bluetooth = ['sudo', 'rfcomm', 'connect', 'hci0', self.sensor_mac_address]
            self.serial_port_process = Popen(connect_to_bluetooth, stdout=PIPE, stdin=PIPE, stderr=PIPE)

        else:
            self.serial_port_process = None

        try:

            self.serial_connection = Serial(self.serial_connection_name, baudrate=self.baudrate, timeout=self.timeout)
            self.serial_connection.read()
            self.timers["check_serial_connection"].interval = 5
            time.sleep(1)

            self.serial_connection_restart_count += 1
            if self.serial_connection_restart_count > 1:
                log.getLogger().warning(f"Serial connection restarted count = {self.serial_connection_restart_count}")

        except:

            self.serial_connection = None
            self.timers["check_serial_connection"].interval = 3
            log.getLogger().warning(f"{self.name} failed to connect to {self.serial_connection_name}")

        log.getLogger().warning(f"DONE start_serial_connection {self.name}")

    def close_serial_connection(self) -> None:
        """
        Closes the serial connection.

        :return: None
        """

        if self.serial_connection is not None:
            self.serial_connection.close()
            self.serial_connection = None

    def restart_connection(self):
        """
        Closes then re-opens the serial connection.

        :return: None
        """

        self.close_serial_connection()
        self.start_serial_connection()

    def get_sensor_values(self):
        """
        Gets the sensor values over the serial connection.

        :return: None
        """

        log.getLogger().debug(f"STARTING get_sensor_values {self.name}")
        try:
            # Make sure the connection object has been created
            if self.serial_connection is not None:

                # Check to see if there are bytes in waiting
                self.bytes_in_waiting = self.serial_connection.in_waiting
                if self.bytes_in_waiting > 0:

                    # Read the bytes from the serial connection, decode them to utf-8 and lastly remove
                    # the trailing values (the new line termination) for formatting purposes.
                    line = self.serial_connection.readline().decode("utf-8").rstrip()
                    self.serial_connection.flush()

                    # Sometimes some random characters get received on the first read so ignore them
                    self.sensor_values = self.validate_sensor_data(line)
                    if len(self.sensor_values) > 0:

                        # Data comes in as a string containing key/value pairs with spaces separating each value.
                        # Convert this to a dictionary to be inserted into the database.
                        # EX: "lights:304 co2:1000"
                        self.sensor_values['date_time'] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                        print(self.sensor_values)

                        # Add the date and time to the columns
                        # print(f"sensor values: {self.sensor_values}")
                        database.insert_data(self.database_name, self.table_name, self.sensor_values)

                else:

                    # There were not bytes in waiting
                    # Reset the timer
                    print("No bytes found. Setting previous seconds back.")
                    self.timers["get_sensor_value"].previous_seconds -= self.timers["get_sensor_value"] + 2
                    pass

        except:
            print("Exception thrown when getting values")
            log.getLogger().critical(f"FAILED multi-sensor '{self.name}' encountered an"
                                     f" error when executing 'get_sensor_values()'")

        log.getLogger().debug(f"DONE get_sensor_values {self.name}")

    def validate_sensor_data(self, sensor_readings: str):
        """
        Check that the bytes received over the serial connection are valid. Sometimes some bytes are lost or mangled.
        If the sensor name from the string is only 1 letter off use the correct string in the return dict.

        :param sensor_readings: the string sent from the multi sensor ("sensor_name:value sensor2_nameLvalue")
        :return: a dict with the validate labels and values {"sensor_name": value}
        """

        log.getLogger().debug(f"STARTING validate_sensor_reading {self.name}")

        sensor_data = {}
        reading_pairs = sensor_readings.split(" ")

        for reading_pair in reading_pairs:

            key_value = reading_pair.split(":")
            if len(key_value) != 2:
                print("failed because pair did not have colon")
                continue

            sensor_name = key_value[0]
            data = key_value[1]
            for column_name in self.database_column_info.keys():

                edit_distance = self.check_edit_distance(sensor_name, column_name)
                if edit_distance <= 1 and data != "":

                    try:

                        if self.database_column_info[column_name] == "REAL":
                            float(data)

                        elif self.database_column_info[column_name] == "INTEGER":
                            int(data)

                        else:
                            raise ValueError("Datatype should be 'REAL' for floats and 'INTEGERS' for integers")

                        sensor_data[column_name] = data

                    except ValueError:
                        # Data must be bad since it cannot be converted to the correct datatype
                        pass

        log.getLogger().debug(f"DONE validate_sensor_reading {self.name}")

        return sensor_data

    @staticmethod
    def check_edit_distance(string1, string2) -> int:
        """
        Taken from www.tutorialspoint.com. Also known as the levinsthein distance. Counts the number
         of difference between string1 and string2.

        ex.

        wake
        wakes
        Distance is 1. Add 1 letter 's' to the end of the word.


        dog
        cat
        Distance is 3. Change 3 letters of dog to 'c', 'a' and 't'

        :param string1:
        :param string2:
        :return: the difference or distance between the two strings
        """

        # Find lengths of given strings
        m = len(string1)
        n = len(string2)

        count = 0  # Count of isEditDistanceOne

        i = 0
        j = 0
        while i < m and j < n:
            # If current characters dont match
            if string1[i] != string2[j]:

                # If length of one string is
                # more, then only possible edit
                # is to remove a character
                if m > n:
                    i += 1
                elif m < n:
                    j += 1
                else:  # If lengths of both strings is same
                    i += 1
                    j += 1

                # Increment count of edits
                count += 1

            else:  # if current characters match
                i += 1
                j += 1

        # if last character is extra in any string
        if i < m or j < n:
            count += 1

        return count

    def check_serial_connection(self):
        """
        This method uses the number of bytes in waiting figure out if the connection is still active/healthy.

        :return: None
        """

        log.getLogger().debug(f"STARTING check_serial_connection {self.name}")

        # If no bytes are waiting there might be something wrong with the connection
        if self.bytes_in_waiting == 0:

            # Increment the counter
            self.no_bytes_count += 1

            # If the no bytes count reaches max no bytes count then restart the connection
            if self.no_bytes_count >= self.no_readings_limit:

                log.getLogger().warning(f"MultiSensor {self.name} did not find new readings after "
                                         f"{self.no_readings_limit} cycles. Attempting to restart connection.")
                print(f"MultiSensor {self.name} did not find new readings after "
                      f"{self.no_readings_limit} cycles. Attempting to restart connection.")
                self.restart_connection()

        else:
            self.no_bytes_count = 0

        log.getLogger().debug(f"DONE get_sensor_values {self.name}")

    @staticmethod
    def string_to_dict(string: str) -> dict:
        """
        Takes a string and converts it to a dictionary. Each key/value must be separated by a ':' and key/value pairs
        must be separated by a ' ' (space).

        Example string: "light:900 co2:654"
        Example result: {"light": 900, "co2": 654}

        :param string: a string with key
        :return: a dictionary built from the given string
        """

        result = {}
        string_array = string.split(" ")
        for key_value_pair in string_array:

            key_value = key_value_pair.split(":")
            result[key_value[0]] = key_value[1]

        return result

    @staticmethod
    def build_column_info_dict(sensor_info: dict) -> dict:
        """
        Creates a dictionary with the column info used to store values to be inserted into the database. Key is the name
        of the column. The value is an initialisation value based on the type ie TEXT = "" (a empty string).

        Example: {"column_name": "TEXT", column1_name: "REAL"}

        :param sensor_info: dictionary containing column name(key) and column datatype (value)
        :return: dictionary used to hold sensor values as they are received
        """

        sensor_values = {}
        for sensor in sensor_info:

            if sensor_info[sensor] == "TEXT":
                sensor_values[sensor] = ""

            elif sensor_info[sensor] == "INTEGER":
                sensor_values[sensor] = 0

            elif sensor_info[sensor] == "REAL":
                sensor_values[sensor] = 0.0

        return sensor_values

    def alarm_check(self):
        """
        Check to see if any notifications should be sent because of high or low values.

        :return: None
        """

        log.getLogger().debug(f"STARTING alarm_check '{self.name}'")

        self.check_for_high_values()
        self.check_for_low_values()

        log.getLogger().debug(f"DONE alarm_check '{self.name}'")

    def check_for_high_values(self):
        """
        Using the high values set in the json file under "alarm_values" check
        to see if a notification should be sent.

        :return: None
        """

        log.getLogger().debug(f"STARTING check_for_high_values '{self.name}'")

        for key in self.alarm_values:

            sensor_values = database.get_sensor_reading(self.database_name, self.table_name, ["date_time", key])
            if self.validate_sensor_reading(sensor_values):

                sensor_value = sensor_values[1]
                max_value = self.alarm_values[key]["high"]

                try:

                    if list(self.alarm_values[key].keys()).index("high") >= 0:

                        if sensor_value >= self.alarm_values[key]["high"]:

                            message = f"Sensor value for '{key}' on '{self.name}' is to high. Alarm set" \
                                      f" to '{max_value}'. Current value is '{sensor_value}'"
                            self.email_controller.send_email(key, EmailReasons.HIGH_VALUE, message)
                            log.getLogger().warning(message)

                except AttributeError:
                    log.getLogger().warning(f"FAILED multi-sensor '{self.name}' tried to send an email alert but "
                                            f"does not have a email controller set")
                    break

                except:
                    log.getLogger().critical(f"Fail to send email with controller '{self.email_controller}'")
                    break

        log.getLogger().debug(f"DONE check_for_high_values '{self.name}'")

    def check_for_low_values(self):
        """
        Using the low values set in the json file under "alarm_values" check
        to see if a notification should be sent.

        :return: None
        """

        log.getLogger().debug(f"STARTING check_for_low_values '{self.name}'")

        for key in self.alarm_values:

            sensor_values = database.get_sensor_reading(self.database_name, self.table_name, ["date_time", key])
            if self.validate_sensor_reading(sensor_values):

                sensor_value = sensor_values[1]
                min_value = self.alarm_values[key]["low"]

                try:

                    if list(self.alarm_values[key].keys()).index("low") >= 0:

                        if sensor_value <= self.alarm_values[key]["low"]:

                            message = f"Sensor value for '{key}' on '{self.name}' is to low. Alarm set" \
                                      f" to '{min_value}'. Current value is '{sensor_value}'"
                            self.email_controller.send_email(EmailReasons.LOW_VALUE, message)

                except AttributeError:
                    log.getLogger().warning(f"Multi-sensor '{self.name}' tried to send an email alert but does not have"
                                            f" a email controller set")

                except:
                    log.getLogger().critical(f"Fail to send email with controller '{self.email_controller}'")

        log.getLogger().debug(f"DONE check_for_low_values '{self.name}'")

    def validate_sensor_reading(self, sensor_values: list) -> bool:
        """
        Checks to see if the sensor value is valid or not. A reading is invalid if it is 'None' or if the number of
        seconds since the reading is greater than the set interval.

        :return: if the sensor reading is valid or not
        """

        log.getLogger().debug(f"STARTING validate_sensor_reading '{self.name}'")

        if sensor_values is None:
            return False

        reading_timestamp = datetime.strptime(sensor_values[0], "%m/%d/%Y %H:%M:%S")
        now = datetime.now()

        sensor_value = sensor_values[1]

        time_since_last_reading = now - reading_timestamp
        if sensor_value is not None and time_since_last_reading.days == 0:

            result = True

        else:
            result = False

        log.getLogger().debug(f"DONE validate_sensor_reading '{self.name}'")

        return result

    def set_email_controller(self, email_controller: EmailController) -> None:
        """
        Gives a reference to the email object so notifications can be sent.

        :param email_controller: the email controller object
        :return: None
        """

        log.getLogger().debug(f"STARTING set_email_controller '{self.name}'")

        self.email_controller = email_controller

        log.getLogger().debug(f"DONE set_email_controller '{self.name}'")
