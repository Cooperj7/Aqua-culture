#include "ph_grav.h"  
#include "DHT.h" 
#include <OneWire.h>
#include <DallasTemperature.h>  

// Setup for the TDS meter
#define TdsSensorPin A1
#define VREF 5.0      // analog reference voltage(Volt) of the ADC
#define SCOUNT  30           // sum of sample point 

int analogBuffer[SCOUNT];    // store the analog value in the array, read from ADC
int analogBufferTemp[SCOUNT];
int analogBufferIndex = 0,copyIndex = 0;
float averageVoltage = 0,tdsValue = 0,temperature = 25;

// Setup for temperature and humidity sensor
#define DHTPIN 3
#define DHTTYPE DHT22     
DHT dht(DHTPIN, DHTTYPE);

// Setup for the water temp. sensor
OneWire oneWire(2);                                                             
DallasTemperature sensors(&oneWire);

// Setup for ph meter
Gravity_pH pH = Gravity_pH(A2);                     
uint8_t user_bytes_received = 0;                
const uint8_t bufferlen = 32;                   
char user_data[bufferlen];  

void setup() {
  
  Serial.begin(9600);
  pinMode(TdsSensorPin,INPUT);
  
  sensors.begin();
  dht.begin();
  pH.begin();
}

void loop() {

  Serial.print("TDS: ");
  Serial.print(getTDS());

  Serial.print(" Ph: ");
  Serial.print(getPh());

  Serial.print(" Water Temp: ");
  Serial.print(getWaterTemp());


  Serial.print(" Air Temp: ");
  Serial.print(getAirTemp());

  Serial.print(" Humidity: ");
  Serial.println(getHumidity());

  delay(5000);
}

float getAirTemp(){
  /*
   * Gets the temperature value form the DHT22 temperature and humidity sensor.  
   */

  float temperature = dht.readTemperature(true);
  if (isnan(temperature)) {
    temperature = -1;
  }

  return temperature;
}

float getHumidity(){
  /*
   * Gets the humidiy value from the DHT22 temperature and humidity sensor.
   */

  float humidity = dht.readHumidity();
  if (isnan(humidity)) {
    humidity = -1;
  }
  
  return humidity;
}

float getWaterTemp(){
  /*
   * Gets the temperature value from the waterproof sesnor. The sensor being used is a DS18B20.
   */
 
  sensors.requestTemperatures();
  float waterTemp = sensors.getTempCByIndex(0);

  if(isnan(waterTemp)){
    
    waterTemp = -1;
  }
  else{
    
    waterTemp = waterTemp * 1.8 + 23;
  }

  return waterTemp;
}

float getTDS(){
  /* 
   *  Partial code taken from df robot (website of purchase)
   *  
   *  Gets the Total Dissolved Solids (TDS) reading in ppm of the liquid the sensor is placed in. Sensors used is Gravity Analog TDS Sensor.
   *  
   *  https://wiki.dfrobot.com/Gravity__Analog_TDS_Sensor___Meter_For_Arduino_SKU__SEN0244#More_Documents
   */

  analogBuffer[analogBufferIndex] = analogRead(TdsSensorPin);    //read the analog value and store into the buffer
  analogBufferIndex++;
  if(analogBufferIndex == SCOUNT) 
    analogBufferIndex = 0;  

    float compensationCoefficient=1.0+0.02*(temperature-25.0);    //temperature compensation formula: fFinalResult(25^C) = fFinalResult(current)/(1.0+0.02*(fTP-25.0));
    float compensationVolatge=averageVoltage/compensationCoefficient;  //temperature compensation
    tdsValue=(133.42*compensationVolatge*compensationVolatge*compensationVolatge - 255.86*compensationVolatge*compensationVolatge + 857.39*compensationVolatge)*0.5;

    return tdsValue;
}

float getPh(){
  /*
   * Partial code taken from df robot (website of purchase)
   * 
   * Gets the Ph value from the Ph sensor
   * 
   * https://www.atlas-scientific.com/circuits/gravity-analog-ph-sensor-meter/
   */

  if (Serial.available() > 0) {                                                      
    user_bytes_received = Serial.readBytesUntil(13, user_data, sizeof(user_data));   
  }

  if (user_bytes_received) {                                                      
    parse_cmd(user_data);                                                          
    user_bytes_received = 0;                                                        
    memset(user_data, 0, sizeof(user_data));                                         
  }

  return pH.read_ph();
}

void parse_cmd(char* string) {
  /*
   * Code taken from Atlas Scientific. Used in getTDS().
   * 
   * https://www.atlas-scientific.com/circuits/gravity-analog-ph-sensor-meter/
   */
                     
  strupr(string);                                
  if (strcmp(string, "CAL,7") == 0) {       
    pH.cal_mid();                                
    Serial.println("MID CALIBRATED");
  }
  else if (strcmp(string, "CAL,4") == 0) {            
    pH.cal_low();                                
    Serial.println("LOW CALIBRATED");
  }
  else if (strcmp(string, "CAL,10") == 0) {      
    pH.cal_high();                               
    Serial.println("HIGH CALIBRATED");
  }
  else if (strcmp(string, "CAL,CLEAR") == 0) { 
    pH.cal_clear();                              
    Serial.println("CALIBRATION CLEARED");
  }
}
