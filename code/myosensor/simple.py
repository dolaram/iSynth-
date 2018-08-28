import serial
import datetime
import time
import rotatefile

intensity_map = [
    [0,70,80],
    [70,150,95],
    [150,280,115],
    [280,1024,127]
]

MAXFILESIZE=1048576*2

ser = serial.Serial('/dev/ttyACM0')
SLEEP_INTERVAL=0.050

rotfile = rotatefile.RotatingFile(max_file_size=MAXFILESIZE,filename='snd')

final_string = ""

while 1:
    final_string = ""
    now = datetime.datetime.now()
    ser_bytes = ser.readline()
    #print ("Data read was " + str(ser_bytes[0:4]))
    try:
        converted_data = int(ser_bytes[0:4],16)
        final_string = str(converted_data)
        #print ("Converted Data was " + str(converted_data))
        for interval in intensity_map:
            if interval[0] <= converted_data < interval[1]:
                final_string = final_string + " ; " + str(interval[2])
        print (final_string)
    except:
        print ("Data was invalid, skipping to next trial!")
        continue
    #rotfile.write(now.isoformat() + " ; " + str(converted_data) + '\n')
    rotfile.write(now.isoformat() + " ; " + final_string + '\n')
    #print ("Filtered Data was " + str(ser_bytes[0:4]))
    #time.sleep(SLEEP_INTERVAL)
