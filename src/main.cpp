// #include <Arduino.h>
// #include <Wire.h>
// #include <SD.h>
// #include "SparkFun_u-blox_GNSS_v3.h"

// #include <pressure.h>

// uint32_t OSR = 256; // Set the oversampling rate, options: 256, 512, 1024, 2048, 4096
// uint16_t model = 1; // Set the model of the sensor, options: 1, 2
// uint8_t address = 0x76; // Set the I2C address of the sensor: 0x76, 0x77

// MS_5803 pressureSensor(OSR, address, model);
// SFE_UBLOX_GNSS myGNSS;

// const int chipSelect = BUILTIN_SDCARD;  // Using the built-in SD card slot on Teensy 4.1
// File dataFile;

// unsigned long lastGPSReadTime = 0;
// unsigned long lastPressureReadTime = 0;
// long lastTime = 0;

// float pressure, temperature;

// struct GPSTimeData {
//     uint32_t epoch;
//     uint32_t micros;
//     bool timeFullyResolved;
//     bool timeValid;
//     bool confirmedTime;
//     uint8_t SIV;
//     uint32_t localTimer;
// };

// GPSTimeData getGPSTimeData(SFE_UBLOX_GNSS &myGNSS) {
//     GPSTimeData data;

//     // Get Unix Epoch and microseconds
//     data.epoch = myGNSS.getUnixEpoch(data.micros);

//     // Get time resolution and validity
//     data.timeFullyResolved = myGNSS.getTimeFullyResolved();
//     data.timeValid = myGNSS.getTimeValid();
//     data.confirmedTime = myGNSS.getConfirmedTime();

//     // Get the number of satellites in view (SIV)
//     data.SIV = myGNSS.getSIV();

//     // Get the local time
//     data.localTimer = millis();

//     return data;
// }

// class SerialAndFileStream : public Stream {
// public:
//     virtual size_t write(uint8_t c)
//     {
//         // Serial.write(c);
//         dataFile = SD.open("nmea_log.txt", FILE_WRITE);
//         if (dataFile)
//             dataFile.write(c);
//         dataFile.close();
//         return 1;
//     }

//     virtual size_t write(const uint8_t *buffer, size_t size)
//     {
//         // Serial.write(buffer, size);
//         dataFile = SD.open("nmea_log.txt", FILE_WRITE);
//         if (dataFile)
//             dataFile.write(buffer, size);
//         dataFile.close();
//         return size;
//     }

//     virtual int available() { return Serial.available(); }
//     virtual int read() { return Serial.read(); }
//     virtual int peek() { return Serial.peek(); }
//     virtual void flush() { Serial.flush(); }
// };

// SerialAndFileStream SerialAndFile;


// void setup() {
//     Serial.begin(115200);
//     while (!Serial) {
//         ; // Wait for serial port to connect.
//     }
//     Serial.println("Serial initialized.");

//     // Initialize SD card
//     if (!SD.begin(chipSelect)) {
//         Serial.println("SD card initialization failed. Data will only be printed to Serial.");
//     } else {
//         // TODO: create new files every time the program is run, write csv headers
//         Serial.println("SD card initialized successfully.");
//         dataFile = SD.open("gps_log.txt", FILE_WRITE);
//         if (!dataFile) {
//             Serial.println("Error opening gps_log.txt");
//         } else {
//             Serial.println("Logging to gps_log.txt");
//         }
//         dataFile.close();
//         dataFile = SD.open("pressure_log.txt", FILE_WRITE);
//         if (!dataFile) {
//             Serial.println("Error opening pressure_log.txt");
//         } else {
//             Serial.println("Logging to pressure_log.txt");
//         }
//         dataFile.close();
//     }

//     Wire.begin();

//     // Initialize pressure sensor
//     if (!pressureSensor.begin()) {
//         Serial.println("Failed to initialize MS5803 sensor!");
//         while (1) ; // Halt execution
//     }
//     Serial.println("MS5803 sensor initialized successfully.");

//     // Initialize GNSS module
//     if (myGNSS.begin() == false) {
//         Serial.println(F("u-blox GNSS module not detected at default I2C address. Please check wiring. Freezing."));
//         while (1);
//     }

//     myGNSS.setI2COutput(COM_TYPE_UBX | COM_TYPE_NMEA); //Set the I2C port to output both NMEA and UBX messages
//     myGNSS.saveConfigSelective(VAL_CFG_SUBSEC_IOPORT); //Save (only) the communications port settings to flash and BBR

//     myGNSS.setProcessNMEAMask(SFE_UBLOX_FILTER_NMEA_ALL); // Make sure the library is passing all NMEA messages to processNMEA

//     // myGNSS.setProcessNMEAMask(SFE_UBLOX_FILTER_NMEA_GGA); // Or, we can be kind to MicroNMEA and _only_ pass the GGA messages to it
//     myGNSS.setNMEAOutputPort(SerialAndFile);
//     myGNSS.setAutoPVT(true);

// }

// void loop() {
//     unsigned long currentTime = millis();

//     // GPS DATA //
//     if (currentTime - lastGPSReadTime >= 10000) {
//         myGNSS.checkUblox(); //See if new data is available. Process bytes as they come in.
//         Serial.println("Checking GNSS");
//         if (myGNSS.getPVT()) {
//             long latitude_mdeg = myGNSS.getLatitude();
//             long longitude_mdeg = myGNSS.getLongitude();


//             Serial.print("Latitude (deg): ");
//             Serial.println(latitude_mdeg / 1000000., 6);
//             Serial.print("Longitude (deg): ");
//             Serial.println(longitude_mdeg / 1000000., 6);

//             GPSTimeData gpsTime = getGPSTimeData(myGNSS);

//             dataFile = SD.open("gps_log.txt", FILE_WRITE);
//             if (dataFile) {
//                 dataFile.print(gpsTime.epoch);
//                 dataFile.print(",");
//                 dataFile.print(gpsTime.micros);
//                 dataFile.print(",");
//                 dataFile.print(gpsTime.timeFullyResolved);
//                 dataFile.print(",");
//                 dataFile.print(gpsTime.timeValid);
//                 dataFile.print(",");
//                 dataFile.print(gpsTime.confirmedTime);
//                 dataFile.print(",");
//                 dataFile.print(gpsTime.SIV);
//                 dataFile.print(",");
//                 dataFile.print(gpsTime.localTimer);
//                 dataFile.print(",");
//                 dataFile.print(latitude_mdeg / 1000000., 6);
//                 dataFile.print(",");
//                 dataFile.println(longitude_mdeg / 1000000., 6);
//                 dataFile.close();
//             } else {
//                 Serial.println("Error opening gps_log.txt");
//             }
        
//         } else {
//             dataFile = SD.open("gps_log.txt", FILE_WRITE);
//             if (dataFile) {
//                 dataFile.print(millis());
//                 dataFile.println(",No GPS data");
//                 dataFile.close();
//             } else {
//                 Serial.println("Error opening gps_log.txt");
//             }
//         }
        
//         lastGPSReadTime = currentTime;
//     }


//     // PRESSURE DATA //
//     if (currentTime - lastPressureReadTime >= 2) {
//         pressureSensor.readSensor();

//         pressure = pressureSensor.getPressure();
//         temperature = pressureSensor.getTemp();

//         // teleplot data
//         Serial.print(">pressure:");
//         Serial.println(pressure);
//         Serial.print(">temperature:");
//         Serial.println(temperature);


//         // write to SD card
//         dataFile = SD.open("pressure_log.txt", FILE_WRITE);
//         if (dataFile) {
//             dataFile.print(millis());
//             dataFile.print(",");
//             dataFile.print(pressure, 2);
//             dataFile.print(",");
//             dataFile.println(temperature, 2);
//             dataFile.close();
//         } else {
//             Serial.println("Error opening pressure_log.txt");
//         }


//         lastPressureReadTime = currentTime;
//     }

// }


// #include <Arduino.h>
// #include <Wire.h>
// #include <SD.h>

// #include <pressure.h>

// uint32_t OSR = 4096; // Set the oversampling rate, options: 256, 512, 1024, 2048, 4096
// uint16_t model = 1; // Set the model of the sensor, options: 1, 2
// uint8_t address = 0x76; // Set the I2C address of the sensor: 0x76, 0x77

// MS_5803 pressureSensor(OSR, address, model);

// const int chipSelect = BUILTIN_SDCARD;  // Using the built-in SD card slot on Teensy 4.1
// File dataFile;

// void setup() {
//     Serial.begin(115200);
//     while (!Serial) {
//         ; // Wait for serial port to connect.
//     }
//     Serial.println("Serial initialized.");

//     // Initialize SD card
//     // if (!SD.begin(chipSelect)) {
//     //     Serial.println("SD card initialization failed. Data will only be printed to Serial.");
//     // } else {
//     //     // TODO: create new files every time the program is run, write csv headers
//     //     Serial.println("SD card initialized successfully.");
//     //     dataFile = SD.open("fast.txt", FILE_WRITE);
//     //     if (!dataFile) {
//     //         Serial.println("Error opening fast.txt");
//     //     } else {
//     //         Serial.println("Logging to fast.txt");
//     //     }
//     //     dataFile.close();
//     // }

//     Wire.begin();
//     Wire.setClock(400000); // Increase I2C clock speed to 400kHz

//     // Initialize pressure sensor
//     if (!pressureSensor.begin()) {
//         Serial.println("Failed to initialize MS5803 sensor!");
//         while (1) ; // Halt execution
//     }
//     Serial.println("MS5803 sensor initialized successfully.");
// }

// void loop() {

//     // PRESSURE DATA //
//     pressureSensor.readSensor();

//     float pressure = pressureSensor.getPressure();
//     // float temperature = pressureSensor.getTemp();

//     // teleplot data
//     Serial.print(">pressure:");
//     Serial.println(pressure);
//     // Serial.print(">temperature:");
//     // Serial.println(temperature);

//     // // write to SD card
//     // dataFile = SD.open("fast.txt", FILE_WRITE);
//     // if (dataFile) {
//     //     dataFile.print(millis());
//     //     dataFile.print(",");
//     //     dataFile.print(pressure, 2);
//     //     dataFile.print(",");
//     //     dataFile.println(temperature, 2);
//     //     dataFile.close();
//     // } else {
//     //     Serial.println("Error opening fast.txt");
//     // }
// }
#include <Wire.h>
#include <SPI.h>
#include <MS5803_01.h> 

// Declare 'sensor' as the object that will refer to your MS5803 in the sketch
// Enter the oversampling value as an argument. Valid choices are
// 256, 512, 1024, 2048, 4096. Library default = 512.
MS_5803 sensor = MS_5803(256);

void setup() {
  // Start the serial ports.
  Serial.begin(115200); // other values include 9600, 14400, 57600 etc.
  delay(2000);
  // Initialize the MS5803 sensor. This will report the
  // conversion coefficients to the Serial terminal if present.
  // If you don't want all the coefficients printed out, 
  // set sensor.initializeMS_5803(false).
  if (sensor.initializeMS_5803()) {
    Serial.println( "MS5803 CRC check OK." );
  } 
  else {
    Serial.println( "MS5803 CRC check FAILED!" );
  }
  delay(3000);
}

void loop() {
  // Use readSensor() function to get pressure and temperature reading. 
  sensor.readSensor();
   // Uncomment the print commands below to show the raw D1 and D2 values
//  Serial.print("D1 = ");
//  Serial.println(sensor.D1val());
//  Serial.print("D2 = ");
//  Serial.println(sensor.D2val());

    // Show pressure
  Serial.print(">pressure:");
  Serial.println(sensor.pressure());

//   Serial.print("Pressure = ");
//   Serial.print(sensor.pressure());
//   Serial.println(" mbar");
  
//   // Show temperature
  Serial.print(">temperature:");
  Serial.println(sensor.temperature());
//   Serial.print("Temperature = ");
//   Serial.print(sensor.temperature());
//   Serial.println("C");

//   delay(1000); // For readability
}