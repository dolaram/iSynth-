import serial
import fluidsynth
import sys, os
import datetime
import time
import rotatefile
import termios, fcntl
import select

# Myoware sensor intensity map
#intensity_map = [
#    [85,150,95],
#    [150,280,115],
#    [280,1024,127]
#]

#intensity_map = [
#    [160,220,80],
#    [220,280,115],
#    [280,1024,127]
#]

intensity_map = [
    [160,220,100],
    [220,1024,127]
]

# Keyboard key map
keymap = {
    'q':59,
    'a':60,
    'w':61,
    's':62,
    'e':63,
    'd':64,
    'r':65,
    'f':66,
    't':67,
    'g':68,
    'y':69,
    'h':70,
    'u':71,
    'j':72,
    'i':73,
    'k':74,
    'o':75,
    'l':76,
    'p':77,
    ';':78,
    '\'':79,
    '[':80,
    ']':81,
    'z':82,
    'x':83,
    'c':84,
    'v':85,
    'b':86,
    'n':87,
    'm':88,
    ',':89,
    '.':90,
    '/':91
}

MAXFILESIZE=1048576*2
#PEAK_SAMPLING_TIME=10
PEAK_SAMPLING_TIME=5

# Serial port settings
ser = serial.Serial('/dev/ttyACM0')
SLEEP_INTERVAL=0.050

# Keyboard input settings
rotfile = rotatefile.RotatingFile(max_file_size=MAXFILESIZE,filename='snd')
fd = sys.stdin.fileno()
newattr = termios.tcgetattr(fd)
newattr[3] = newattr[3] & ~termios.ICANON
newattr[3] = newattr[3] & ~termios.ECHO
termios.tcsetattr(fd, termios.TCSANOW, newattr)
oldterm = termios.tcgetattr(fd)
oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

# Fluidsynth settings
fs = fluidsynth.Synth()
fs.start()
fs.start(driver="alsa")
#sfid = fs.sfload("FluidR3_GM.sf2")
sfid = fs.sfload("Nice-Keys-Ultimate-V2.3.sf2")
fs.program_select(0, sfid, 0, 0)

final_string = ""

while 1:
    velocity = 80
    final_string = ""
    now = datetime.datetime.now()
    ser_bytes = ser.readline()
    #print ("Data read was " + str(ser_bytes[0:4]))
    try:
        converted_data = int(ser_bytes[0:4],16)
        if (converted_data >= intensity_map[0][0]):
            for i in range (0,PEAK_SAMPLING_TIME):
                ser_bytes = ser.readline()
            converted_data = int(ser_bytes[0:4],16)
            final_string = "Sensor value crossed threshold;"+str(converted_data)
            for interval in intensity_map:  
                if interval[0] <= converted_data < interval[1]:
                    velocity = interval[2]
                    final_string = final_string + ";" + str(interval[2])
    
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                keypressed = sys.stdin.read()
                if (keypressed[0] == '/'):
                    break
                fs.noteon(0, keymap[keypressed[0]], velocity)
                final_string = final_string + ";Key: " + str(keypressed[0])
                print (final_string)
    
        else:
            final_string = str(converted_data)
            final_string = "Boring! Sensor value;" + str(converted_data)

    except:
        print ("Exception was " + str(sys.exc_info()[0]))
        print ("Data was invalid, skipping to next trial!")
        continue

    #print (final_string)
    rotfile.write(now.isoformat() + ";" + final_string + '\n')
    #time.sleep(SLEEP_INTERVAL)

# Reset the terminal:
termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
