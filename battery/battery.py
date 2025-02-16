import time
import board
import analogio

# Create an analog input object for the battery ADC pin
bat_adc = analogio.AnalogIn(board.BAT_ADC)


def get_battery_voltage():
    # Return percentage based on max possible ADC value
    max_adc = 65535  # Maximum 16-bit ADC value
    percentage = (bat_adc.value / max_adc) * 100
    return percentage


if __name__ == "__main__":
    while True:
        voltage = get_battery_voltage()
        raw_voltage = bat_adc.value
        print("Battery Voltage: {:.2f} V".format(voltage))
        print("Raw Voltage: {}".format(raw_voltage))
        time.sleep(10)
