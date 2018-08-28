import serial
import fluidsynth
import sys, os
import datetime
import time
import rotatefile
import termios, fcntl
import select

THRESHOLD    = 460
MAX_VELOCITY = 127
MIN_VELOCITY = 90

'''
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
'''

keymap = {
    'q':59,
    'a':61,
    'w':62,
    's':65,
    'e':63,
    'd':66,
    'r':65,
    'f':68,
    't':67,
    'g':70,
    'y':69,
    'h':73,
    'u':71,
    'j':77,
    'i':73,
    'k':78,
    'o':75,
    'l':80,
    'p':77,
    ';':82,
    '\'':79,
    '[':80,
    ']':81,
    'z':73,
    'x':77,
    'c':78,
    'v':80,
    'b':82,
    'n':85,
    'm':89,
    ',':90,
    '.':92,
    '/':94
}


MAXFILESIZE=1048576*2

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
#sfid = fs.sfload("rhodes.sf2")
#fs.program_select(0, sfid, 0, 5)
fs.program_select(0, sfid, 0, 0)

final_string = ""
exit = 0

def play_key (velocity):
    return_string = ""
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        keypressed = sys.stdin.read()
        if (keypressed == '/'):
            print("Exiting the program")
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
            fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
            os._exit(0)
        fs.noteon(0, keymap[keypressed[0]], velocity)
        return_string = ";Key: " + str(keypressed[0])
    return return_string

while 1:
    velocity = 80
    final_string = ""
    now = datetime.datetime.now()
    ser_bytes = ser.readline()
    print ("Data read was " + str(ser_bytes[0:4]))
    try:
        if (exit == 1):
            break
        converted_data = int(ser_bytes[0:4],16)
        if (converted_data >= THRESHOLD):
            final_string = "Sensor value crossed threshold;"+str(converted_data)
            final_string = final_string + play_key(MAX_VELOCITY)
        
        else:
            final_string = "Boring! Sensor value;" + str(converted_data)
            final_string = final_string + play_key(MIN_VELOCITY)

    except:
        print ("Exception was " + str(sys.exc_info()[0]))
        print ("Data was invalid, skipping to next trial!")
        continue

    print (final_string)
    rotfile.write(now.isoformat() + ";" + final_string + '\n')
    #time.sleep(SLEEP_INTERVAL)

# Reset the terminal:
termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
