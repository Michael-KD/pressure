#include <Arduino.h>
#include <Wire.h>
#include <SD.h>
#include "SparkFun_u-blox_GNSS_v3.h"

#include <pressure.h>

uint32_t OSR = 256; // Set the oversampling rate, options: 256, 512, 1024, 2048, 4096
uint16_t model = 1; // Set the model of the sensor, options: 1, 2
uint8_t address = 0x76; // Set the I2C address of the sensor: 0x76, 0x77

MS_5803 pressureSensor(OSR, address, model);

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  while (!Serial) {
    ; // Wait for serial port to connect. Needed for native USB port only
  }

  // Initialize I2C communication
  Wire.begin();

  // Initialize the pressure sensor
  if (!pressureSensor.begin()) {
    Serial.println("Failed to initialize MS5803 sensor!");
    while (1) ; // Halt execution
  }

  Serial.println("MS5803 sensor initialized successfully.");
}

void loop() {
  // Read sensor data
  pressureSensor.readSensor();

  // Get pressure and temperature values
  float pressure = pressureSensor.getPressure();
  float temperature = pressureSensor.getTemp();

  // Print the results
  Serial.print("Pressure: ");
  Serial.print(pressure, 2);
  Serial.print(" mbar, Temperature: ");
  Serial.print(temperature, 2);
  Serial.println(" C");

  // Wait for a bit before next reading
  delay(1000);
}



















// SFE_UBLOX_GNSS myGNSS;

// const int chipSelect = BUILTIN_SDCARD;  // Using the built-in SD card slot on Teensy 4.1
// File dataFile;

// class SerialAndFileStream : public Stream
// {
// public:
//     virtual size_t write(uint8_t c)
//     {
//         Serial.write(c);
//         if (dataFile)
//             dataFile.write(c);
//         return 1;
//     }

//     virtual size_t write(const uint8_t *buffer, size_t size)
//     {
//         Serial.write(buffer, size);
//         if (dataFile)
//             dataFile.write(buffer, size);
//         return size;
//     }

//     virtual int available() { return Serial.available(); }
//     virtual int read() { return Serial.read(); }
//     virtual int peek() { return Serial.peek(); }
//     virtual void flush() { Serial.flush(); }
// };

// SerialAndFileStream SerialAndFile;

// void setup()
// {
//     Serial.begin(115200);
//     // while (!Serial) {
//     //     ; // Wait for serial port to connect
//     // }
//     Serial.println("SparkFun u-blox Example with SD logging");

//     // Initialize SD card
//     if (!SD.begin(chipSelect)) {
//         Serial.println("SD card initialization failed. Data will only be printed to Serial.");
//     } else {
//         Serial.println("SD card initialized successfully.");
//         dataFile = SD.open("gps_log.txt", FILE_WRITE);
//         if (!dataFile) {
//             Serial.println("Error opening gps_log.txt");
//         } else {
//             Serial.println("Logging to gps_log.txt");
//         }
//     }

//     Wire.begin();

//     if (myGNSS.begin() == false)
//     {
//         SerialAndFile.println(F("u-blox GNSS module not detected at default I2C address. Please check wiring. Freezing."));
//         while (1);
//     }

//     // This will pipe all NMEA sentences to both Serial and SD card
//     myGNSS.setNMEAOutputPort(SerialAndFile);
// }

// void loop()
// {
//     SerialAndFile.println("======================");
//     myGNSS.checkUblox(); // See if new data is available. Process bytes as they come in.

//     // Ensure data is written to the SD card
//     if (dataFile) {
//         dataFile.flush();
//     }

//     delay(250); // Don't pound too hard on the I2C bus
// }


// #include <Arduino.h>
// #include <SD.h>
// #include <SPI.h>
// #include <TimeLib.h>

// #include <gps.h>
// #include <pressure.h>

// const int chipSelect = BUILTIN_SDCARD;
// const char* fileName = "sensor_data.csv";

// // Placeholder functions for sensor readings
// float pressure() {
//   // Replace with actual pressure reading code
//   return random(1000, 1100) / 10.0;  // Simulated pressure between 100.0 and 110.0
// }

// float temp() {
//   // Replace with actual temperature reading code
//   return random(200, 300) / 10.0;  // Simulated temperature between 20.0 and 30.0
// }

// void setup() {
//   Serial.begin(9600);
//   while (!Serial) {
//     ; // Wait for serial port to connect
//   }

//   if (!SD.begin(chipSelect)) {
//     Serial.println("SD card initialization failed!");
//     return;
//   }
//   Serial.println("SD card initialized successfully.");

//   // Create or open the CSV file and write the header
//   File dataFile = SD.open(fileName, FILE_WRITE);
//   if (dataFile) {
//     if (dataFile.size() == 0) {
//       dataFile.println("Time,Pressure,Temperature");
//     }
//     dataFile.close();
//   } else {
//     Serial.println("Error opening file!");
//     return;
//   }

//   // Initialize the time (you might want to set this more accurately)
//   setTime(12, 0, 0, 1, 1, 2024);  // 12:00:00 January 1, 2024
// }

// void loop() {
//   // Get current sensor values
//   float pressureValue = pressure();
//   float tempValue = temp();

//   // Get current time
//   char timeStr[20];
//   sprintf(timeStr, "%04d-%02d-%02d %02d:%02d:%02d", year(), month(), day(), hour(), minute(), second());

//   // Create the data string
//   char dataString[50];
//   sprintf(dataString, "%s,%.2f,%.2f", timeStr, pressureValue, tempValue);

//   // Open the file and write the new line
//   File dataFile = SD.open(fileName, FILE_WRITE);
//   if (dataFile) {
//     dataFile.println(dataString);
//     dataFile.close();
//     Serial.println("Data written to file: " + String(dataString));
//   } else {
//     Serial.println("Error opening file for writing!");
//   }

//   delay(5000);  // Wait for 5 seconds before the next reading
// }