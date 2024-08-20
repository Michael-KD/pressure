#include <Arduino.h>
#include <Wire.h>
#include <SD.h>
#include "SparkFun_u-blox_GNSS_v3.h"
#include <MicroNMEA.h>

#include <pressure.h>

uint32_t OSR = 256; // Set the oversampling rate, options: 256, 512, 1024, 2048, 4096
uint16_t model = 1; // Set the model of the sensor, options: 1, 2
uint8_t address = 0x76; // Set the I2C address of the sensor: 0x76, 0x77

MS_5803 pressureSensor(OSR, address, model);
SFE_UBLOX_GNSS myGNSS;

char nmeaBuffer[100];
MicroNMEA nmea(nmeaBuffer, sizeof(nmeaBuffer));



const int chipSelect = BUILTIN_SDCARD;  // Using the built-in SD card slot on Teensy 4.1
File dataFile;

unsigned long lastGPSReadTime = 0;
unsigned long lastPressureReadTime = 0;
long lastTime = 0;

float pressure, temperature;

struct GPSTimeData {
    uint32_t epoch;
    uint32_t micros;
    bool timeFullyResolved;
    bool timeValid;
    bool confirmedTime;
    uint8_t SIV;
    uint32_t localTimer;
};

GPSTimeData getGPSTimeData(SFE_UBLOX_GNSS &myGNSS) {
    GPSTimeData data;

    // Get Unix Epoch and microseconds
    data.epoch = myGNSS.getUnixEpoch(data.micros);

    // Get time resolution and validity
    data.timeFullyResolved = myGNSS.getTimeFullyResolved();
    data.timeValid = myGNSS.getTimeValid();
    data.confirmedTime = myGNSS.getConfirmedTime();

    // Get the number of satellites in view (SIV)
    data.SIV = myGNSS.getSIV();

    // Get the local time
    data.localTimer = millis();

    return data;
}

class SerialAndFileStream : public Stream {
public:
    virtual size_t write(uint8_t c)
    {
        // Serial.write(c);
        dataFile = SD.open("gps_log.txt", FILE_WRITE);
        if (dataFile)
            dataFile.write(c);
        dataFile.close();
        return 1;
    }

    virtual size_t write(const uint8_t *buffer, size_t size)
    {
        // Serial.write(buffer, size);
        dataFile = SD.open("gps_log.txt", FILE_WRITE);
        if (dataFile)
            dataFile.write(buffer, size);
        dataFile.close();
        return size;
    }

    virtual int available() { return Serial.available(); }
    virtual int read() { return Serial.read(); }
    virtual int peek() { return Serial.peek(); }
    virtual void flush() { Serial.flush(); }
};

SerialAndFileStream SerialAndFile;


void setup() {
    Serial.begin(115200);
    while (!Serial) {
        ; // Wait for serial port to connect.
    }

    // Initialize SD card
    if (!SD.begin(chipSelect)) {
        Serial.println("SD card initialization failed. Data will only be printed to Serial.");
    } else {
        // TODO: create new files every time the program is run, write csv headers
        Serial.println("SD card initialized successfully.");
        dataFile = SD.open("gps_log.txt", FILE_WRITE);
        if (!dataFile) {
            Serial.println("Error opening gps_log.txt");
        } else {
            Serial.println("Logging to gps_log.txt");
        }
        dataFile.close();
        dataFile = SD.open("pressure_log.txt", FILE_WRITE);
        if (!dataFile) {
            Serial.println("Error opening pressure_log.txt");
        } else {
            Serial.println("Logging to pressure_log.txt");
        }
        dataFile.close();
    }

    Wire.begin();

    // Initialize pressure sensor
    if (!pressureSensor.begin()) {
        Serial.println("Failed to initialize MS5803 sensor!");
        while (1) ; // Halt execution
    }
    Serial.println("MS5803 sensor initialized successfully.");

    // Initialize GNSS module
    if (myGNSS.begin() == false) {
        Serial.println(F("u-blox GNSS module not detected at default I2C address. Please check wiring. Freezing."));
        while (1);
    }

    myGNSS.setI2COutput(COM_TYPE_UBX | COM_TYPE_NMEA); //Set the I2C port to output both NMEA and UBX messages
    myGNSS.saveConfigSelective(VAL_CFG_SUBSEC_IOPORT); //Save (only) the communications port settings to flash and BBR

    myGNSS.setProcessNMEAMask(SFE_UBLOX_FILTER_NMEA_ALL); // Make sure the library is passing all NMEA messages to processNMEA

    // myGNSS.setProcessNMEAMask(SFE_UBLOX_FILTER_NMEA_GGA); // Or, we can be kind to MicroNMEA and _only_ pass the GGA messages to it
    myGNSS.setNMEAOutputPort(SerialAndFile);
}

void loop() {
    unsigned long currentTime = millis();

    if (currentTime - lastGPSReadTime >= 10000) {
        myGNSS.checkUblox(); //See if new data is available. Process bytes as they come in.
        Serial.println("Checking GNSS");
        if(nmea.isValid() == true) {
            long latitude_mdeg = nmea.getLatitude();
            long longitude_mdeg = nmea.getLongitude();

            Serial.print("Latitude (deg): ");
            Serial.println(latitude_mdeg / 1000000., 6);
            Serial.print("Longitude (deg): ");
            Serial.println(longitude_mdeg / 1000000., 6);

            nmea.clear(); // Clear the MicroNMEA storage to make sure we are getting fresh data
        }
        

        lastGPSReadTime = currentTime;
    }

    if (currentTime - lastPressureReadTime >= 30) {
        pressureSensor.readSensor();

        pressure = pressureSensor.getPressure();
        temperature = pressureSensor.getTemp();

        // teleplot data
        Serial.print(">pressure:");
        Serial.println(pressure);
        Serial.print(">temperature:");
        Serial.println(temperature);


        // write to SD card
        // GPSTimeData gpsTime = getGPSTimeData(myGNSS);
        dataFile = SD.open("pressure_log.txt", FILE_WRITE);
        if (dataFile) {
            // dataFile.print(gpsTime.epoch);
            // dataFile.print(",");
            // dataFile.print(gpsTime.micros);
            // dataFile.print(",");
            // dataFile.print(gpsTime.timeFullyResolved);
            // dataFile.print(",");
            // dataFile.print(gpsTime.timeValid);
            // dataFile.print(",");
            // dataFile.print(gpsTime.confirmedTime);
            // dataFile.print(",");
            // dataFile.print(gpsTime.SIV);
            // dataFile.print(",");
            // dataFile.print(gpsTime.localTimer);
            // dataFile.print(",");

            dataFile.print(millis());
            dataFile.print(",");
            dataFile.print(pressure, 2);
            dataFile.print(",");
            dataFile.println(temperature, 2);
            dataFile.close();
        } else {
            Serial.println("Error opening pressure_log.txt");
        }


        lastPressureReadTime = currentTime;
    }

}