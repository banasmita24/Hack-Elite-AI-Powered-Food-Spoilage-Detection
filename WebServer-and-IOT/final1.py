from machine import I2C, Pin, ADC
import utime
import machine_i2c_lcd
import time
from dht import DHT11

# I2C and LCD display setup (replace with your specific library functions)
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
lcd = machine_i2c_lcd.I2cLcd(i2c, 0x27, num_lines=2, num_columns=16)

# DHT11 sensor setup
data_pin = 15
data_pin_object = Pin(data_pin, Pin.OUT, Pin.PULL_DOWN)
sensor = DHT11(data_pin_object)

adc = ADC(Pin(28))

# Function to read temperature and humidity
def read_dht_sensor():
    sensor.measure()
    temperature_celsius = sensor.temperature
    humidity_percentage = sensor.humidity
    return temperature_celsius, humidity_percentage

# Calibration parameters
RO_CLEAN_AIR_FACTOR = 9.83  # RO value in clean air (change according to your sensor)
CALIBRATION_SAMPLE_TIMES = 25
CALIBRATION_SAMPLE_INTERVAL = 250  # milliseconds

# Define AQI thresholds (adjust based on your testing and local air quality standards)
aqi_thresholds = {
    "PM2.5": [0, 30, 85, 250, 350],  # Lowered Good and Moderate thresholds due to high PM2.5 concerns
    "PM10": [0, 50, 100, 250, 350, 430],  # Adjusted PM10 thresholds based on potential local concerns
    "O3": [0, 51, 100, 168],  # National 8-hour ozone standard
    "NO2": [0, 40, 80, 180],  # Tighter NO2 thresholds considering potential traffic pollution
    "CO": [0, 400, 1500, 2500, 3500, 4500],
    "SO2": [0, 40, 80, 380]
}

# Gas concentration ratio for CO2, CO, and NH4
R0_RATIO_CO2 = 60
R0_RATIO_CO = 4.5
R0_RATIO_NH4 = 3.5
R0_RATIO_ALCOHOL = 15  # Assuming a 1000 ppm alcohol concentration
R0_RATIO_CH4 = 9  # Placeholder value, needs calibration
R0_RATIO_BUTANE = 7

def read_R0():
    # Perform sensor calibration
    print("Calibrating MQ-135, please wait...")
    val = 0.0
    for _ in range(25):
        val += adc.read_u16()
        time.sleep_ms(250)
    val /= 25
    val = val / 65535 * 3.3  # Convert to voltage

    # Calculate R0 value
    RS_RO = val / RO_CLEAN_AIR_FACTOR
    return RS_RO

def calculate_gas_concentration(R0_ratio, RS_RO):
    # Calculate gas concentration based on the sensor ratio
    gas_concentration = (R0_ratio / RS_RO - 1) / 10
    return gas_concentration

def calculate_aqi(pollutant_concentration, pollutant_type):
  # Check for valid pollutant type
  if pollutant_type not in aqi_thresholds:
    return None  # Handle invalid pollutant

  thresholds = aqi_thresholds[pollutant_type]

  if pollutant_type == "PM2.5":
    pollutant_concentration = pollutant_concentration * 0.5 
  
  # Find the AQI index based on concentration
  for i in range(len(thresholds) - 1):
    if pollutant_concentration <= thresholds[i + 1]:
      return int((i * (aqi_thresholds[pollutant_type][i + 1] - aqi_thresholds[pollutant_type][i]) /
                 (thresholds[i + 1] - thresholds[i]) + aqi_thresholds[pollutant_type][i]))
  
  # Concentration exceeds highest threshold
  return aqi_thresholds[pollutant_type][-1]  # Return the highest AQI value

def get_air_quality_message(aqi_value):
    # Define air quality message mapping based on AQI (adjust based on your needs)
    air_quality_messages = {
        0: "Good",
        51: "Moderate",
        101: "Poor",
        151: "Very Poor",
        201: "Severe"
    }

    for threshold, message in air_quality_messages.items():
        if aqi_value is not None and aqi_value <= threshold:  # Check for None before comparison
            return message
    return "Hazardous"

def main():
    R0_CO2 = R0_RATIO_CO2 * read_R0()
    R0_CO = R0_RATIO_CO * read_R0()
    R0_NH4 = R0_RATIO_NH4 * read_R0()
    R0_ALCOHOL = R0_RATIO_ALCOHOL * read_R0()  # Calculate R0 for alcohol
    R0_CH4 = R0_RATIO_CH4 * read_R0()  # Calculate R0 for methane (placeholder)
    R0_BUTANE = R0_RATIO_BUTANE * read_R0()
    
    R0_calibrated = read_R0()
    R0_ratio_generic = 10# ADC pin for MQ-135 sensor (replace with your actual pin)

    while True:
        # Read temperature and humidity from DHT11 sensor
        temperature_celsius, humidity_percentage = read_dht_sensor()

        # Read gas concentrations
        sensor_value = adc.read_u16() / 65535 * 3.3  # Convert to voltage

        # Calculate a generic VOC concentration
        gas_concentration = calculate_gas_concentration(R0_ratio_generic, R0_calibrated)

        # Calculate AQI based on generic VOC concentration (consider adding specific pollutant calculation)
        aqi_value = calculate_aqi(gas_concentration, "PM2.5")  # Assuming PM2.5 as primary pollutant
        
        air_quality_message = get_air_quality_message(aqi_value)
        
        RS_RO_CO2 = sensor_value / R0_CO2
        RS_RO_CO = sensor_value / R0_CO
        RS_RO_NH4 = sensor_value / R0_NH4
        RS_RO_ALCOHOL = sensor_value / R0_ALCOHOL
        RS_RO_CH4 = sensor_value / R0_CH4
        RS_RO_BUTANE = sensor_value / R0_CH4
        
        CO2_concentration = calculate_gas_concentration(R0_RATIO_CO2, RS_RO_CO2)
        CO_concentration = calculate_gas_concentration(R0_RATIO_CO, RS_RO_CO)
        NH4_concentration = calculate_gas_concentration(R0_RATIO_NH4, RS_RO_NH4)
        alcohol_concentration = calculate_gas_concentration(R0_RATIO_ALCOHOL, RS_RO_ALCOHOL)
        methane_concentration = calculate_gas_concentration(R0_RATIO_CH4, RS_RO_CH4)
        butane_concentration = calculate_gas_concentration(R0_RATIO_BUTANE, RS_RO_CO2)  # Assuming some Butane presence with CO2

        # Display readings on LCD
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("Air: {}".format(air_quality_message))
        utime.sleep(2)
        
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("Temp: {:.2f} C".format(temperature_celsius))
        lcd.move_to(0, 1)
        lcd.putstr("Humidity: {:.1f}%".format(humidity_percentage))
        utime.sleep(2)

        # Display gas concentrations and temperature on LCD
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("CO2: {:.2f} ppm".format(CO2_concentration))
        lcd.move_to(0, 1)
        lcd.putstr("CO:  {:.2f} ppm".format(CO_concentration))
        utime.sleep(2)

        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("NH4: {:.2f} ppm".format(NH4_concentration))
        lcd.move_to(0, 1)
        lcd.putstr("C4H10: {:.2f} ppm".format(butane_concentration))
        utime.sleep(2)
        
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("Alc: {:.2f} ppm".format(alcohol_concentration))
        lcd.move_to(0, 1)
        lcd.putstr("CH4: {:.2f} ppm".format(methane_concentration))  # Add methane display
        utime.sleep(2)
    

if __name__ == "__main__":
    main()
