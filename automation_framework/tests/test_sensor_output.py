from time import sleep

from framework.json_loader import create_sensor_output

def test_sensor_output(sensor_output):

    natural_change = 25
    output_trend = 50
    total = 0
    numbers = 0

    sensor_output.value = 900

    while True:

        sensor_output.find_state()

        sensor_value = sensor_output.value
        if sensor_output.value_shift == '-':
            sensor_output.value = sensor_value + natural_change

        else:
            sensor_output.value = sensor_value - natural_change

        sensor_value = sensor_output.value
        if sensor_output.state:

            if sensor_output.value_shift == '-':
                sensor_output.value = sensor_value - output_trend

            else:
                sensor_output.value = sensor_value + output_trend

        total += sensor_output.value
        numbers += 1
        print('state: ', sensor_output.state, ' | value: ', sensor_output.value,
              ' | avg: ', (1 / numbers) * total)

        sleep(1)


if __name__ == "__main__":

    sensor_output = create_sensor_output("test_sensor_output.json")

    test_sensor_output(sensor_output)