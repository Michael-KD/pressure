# write a function to write n lines of data to a CSV file, with the header Time, temp, pressure, long, lat
# The time should be Unix time, temp and pressure should be random numbers between 0 and 100, and long and lat should be random numbers between -180 and 180

import random
import time
import math

def write_csv(n):
    with open('data.csv', 'w') as file:
        file.write("Time,Pressure,Temperature,Longitude,Latitude\n")
        for i in range(n):
            # cut off data at 4 decimal points
            data = f"{time.time():.4f},{random.random()*100:.4f},{random.random()*100:.4f},{random.random()*360-180:.4f},{random.random()*360-180:.4f}\n"
            file.write(data)
            # print out a progress bar that updates one line in the ternimal
            print(f"\r{i/n*100:.2f}%", end='')
    print("\nDone")
            
def write_csv_mult(n):
    with open('data.csv', 'w') as file:
        file.write("Time,Pressure,Temperature,Longitude,Latitude\n")
        for i in range(n):
            # cut off data at 4 decimal points, then multiply each value by 1000, store as ints
            data = f"{int(time.time()*1000)},{int(random.random()*100*1000)},{int(random.random()*100*1000)},{int(random.random()*360*1000-180*1000)},{int(random.random()*360*1000-180*1000)}\n"
            file.write(data)
            # print out a progress bar that updates one line in the ternimal
            print(f"\r{i/n*100:.2f}%", end='')
    print("\nDone")

num_lines =  10000
write_csv(num_lines)

# print the size in bytes of the file
import os
file_size = os.path.getsize('data.csv')
print(f'{file_size} bytes')
print(f'aprox {file_size/num_lines} bytes per line')

max_size = 1024**3*1
print(f'1gb file would be {math.ceil(1024**3/(file_size/num_lines)):e} lines long')

print(f'300 lines per second would take {math.ceil(1024**3/(file_size/num_lines)/300):e} seconds to write a 1gb file')
print(f'{math.ceil(1024**3/(file_size/num_lines)/300/60):e} minutes, or {math.ceil(1024**3/(file_size/num_lines)/300/60/60):e} hours')

print("=========================================")

write_csv_mult(num_lines)
file_size = os.path.getsize('data.csv')
print(f'{file_size} bytes')
print(f'aprox {file_size/num_lines} bytes per line')
print(f'1gb file would be {math.ceil(1024**3/(file_size/num_lines)):e} lines long')
print(f'300 lines per second would take {math.ceil(1024**3/(file_size/num_lines)/300):e} seconds to write a 1gb file')
print(f'{math.ceil(1024**3/(file_size/num_lines)/300/60):e} minutes, or {math.ceil(1024**3/(file_size/num_lines)/300/60/60):e} hours')
