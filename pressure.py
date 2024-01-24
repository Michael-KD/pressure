import smbus2
import time
import csv
import argparse

### 0.001s -> 1ms

# Parse command line arguments
parser = argparse.ArgumentParser(description='Read sensor data with specified OSR value.')
parser.add_argument('osr', type=int, help='OSR value (256, 512, 1024, 2048, or 4096)')
parser.add_argument('model', type=int, help='Model number (01 or 02)')
parser.add_argument('delay', type=float, help='Delay value in milliseconds')
parser.add_argument('loops', type=int, help='Number of loops (0 for infinite)')
args = parser.parse_args()

# Convert delay
delay = args.delay / 1000

# Map OSR values to commands
osr_commands = {
    256: (0x40, 0x50),
    512: (0x42, 0x52),
    1024: (0x44, 0x54),
    2048: (0x46, 0x56),
    4096: (0x48, 0x58),
}

# Get the commands for the specified OSR value
if args.osr in osr_commands:
    D1_command, D2_command = osr_commands[args.osr]
else:
    print(f"Invalid OSR value: {args.osr}")
    exit(1)

# Get I2C bus
bus = smbus2.SMBus(1)

# MS5803_01BA address, 0x76(118)
# 0x1E(30) Reset command
bus.write_byte(0x76, 0x1E)

time.sleep(0.5)

# Read 12 bytes of calibration data
# Read pressure sensitivity
data = bus.read_i2c_block_data(0x76, 0xA2, 2)
C1 = data[0] * 256 + data[1]

# Read pressure offset
data = bus.read_i2c_block_data(0x76, 0xA4, 2)
C2 = data[0] * 256 + data[1]

# Read temperature coefficient of pressure sensitivity
data = bus.read_i2c_block_data(0x76, 0xA6, 2)
C3 = data[0] * 256 + data[1]

# Read temperature coefficient of pressure offset
data = bus.read_i2c_block_data(0x76, 0xA8, 2)
C4 = data[0] * 256 + data[1]

# Read reference temperature
data = bus.read_i2c_block_data(0x76, 0xAA, 2)
C5 = data[0] * 256 + data[1]

# Read temperature coefficient of the temperature
data = bus.read_i2c_block_data(0x76, 0xAC, 2)
C6 = data[0] * 256 + data[1]

print("starting read loop")




def read_data():
        # MS5803_01BA address, 0x76(118)
        # 0x40(64) Pressure conversion(OSR = INPUT) command
        bus.write_byte(0x76, D1_command)

        time.sleep(delay)

        # Read digital pressure value
        # Read data back from 0x00(0), 3 bytes
        # D1 MSB2, D1 MSB1, D1 LSB
        value = bus.read_i2c_block_data(0x76, 0x00, 3)
        D1 = value[0] * 65536 + value[1] * 256 + value[2]

        # MS5803_01BA address, 0x76(118)
        # 0x50(64) Temperature conversion(OSR = INPUT) command
        bus.write_byte(0x76, 0x50)
        
        time.sleep(0.6/1000)

        # Read digital temperature value
        # Read data back from 0x00(0), 3 bytes
        # D2 MSB2, D2 MSB1, D2 LSB
        value = bus.read_i2c_block_data(0x76, 0x00, 3)
        D2 = value[0] * 65536 + value[1] * 256 + value[2]

        dT = D2 - C5 * 256
        TEMP = 2000 + dT * C6 / 8388608

        if args.model == 1:
            OFF = C2 * 65536 + (C4 * dT) / 128
            SENS = C1 * 32768 + (C3 * dT ) / 256
            T2 = 0
            OFF2 = 0
            SENS2 = 0

            if TEMP >= 2000 :
                T2 = 0
                OFF2 = 0
                SENS2 = 0
                if TEMP > 4500 :
                    SENS2 = SENS2 - ((TEMP - 4500) * (TEMP - 4500)) / 8
            elif TEMP < 2000 :
                T2 = (dT * dT) / 2147483648
                OFF2 = 3 * ((TEMP - 2000) * (TEMP - 2000))
                SENS2 = 7 * ((TEMP - 2000) * (TEMP - 2000)) / 8
                if TEMP < -1500 :
                    SENS2 = SENS2 + 2 * ((TEMP + 1500) * (TEMP + 1500))

            TEMP = TEMP - T2
            OFF = OFF - OFF2
            SENS = SENS - SENS2
            pressure = ((((D1 * SENS) / 2097152) - OFF) / 32768.0) / 100.0
            cTemp = TEMP / 100.0
        elif args.model == 2:
            OFF = C2 * 131072 + (C4 * dT) / 64
            SENS = C1 * 65536 + (C3 * dT ) / 128
            T2 = 0
            OFF2 = 0
            SENS2 = 0

            if TEMP >= 2000 :
                T2 = 0
                OFF2 = 0
                SENS2 = 0
            elif TEMP < 2000 :
                T2 = (dT * dT) / 2147483648
                OFF2= 61 * ((TEMP - 2000) * (TEMP - 2000)) / 16
                SENS2= 2 * ((TEMP - 2000) * (TEMP - 2000))
                if TEMP < -1500 :
                    OFF2 = OFF2 + 20 * ((TEMP + 1500) * (TEMP + 1500))
                    SENS2 = SENS2 + 12 * ((TEMP + 1500) * (TEMP +1500))

            TEMP = TEMP - T2
            OFF = OFF - OFF2
            SENS = SENS - SENS2
            pressure = ((((D1 * SENS) / 2097152) - OFF) / 32768.0) / 100.0
            cTemp = TEMP / 100.0
        else:
            print(f"Invalid model number: {args.model}")
            exit(1)

        # Write the time, pressure, and temperature to the CSV file
        writer.writerow([time.time()-start_time, pressure, cTemp])


# Open a CSV file to write the data
with open('data.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Time", "Pressure", "Temperature"])

    start_time = time.time()
    
# run 1000 times
    if args.loops == 0:
        while True:
            read_data()
    else:
        for i in range(args.loops):
            read_data()
    
        
print("finished read loop, time taken:" + str(time.time() - start_time) + " seconds")
