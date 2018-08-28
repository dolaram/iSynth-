import time
import fluidsynth
import sys
import tty
import termios

# max velocity is 127

velocity = 127

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

old_settings = termios.tcgetattr(sys.stdin)
fs = fluidsynth.Synth()
fs.start()
fs.start(driver="alsa")

#sfid = fs.sfload("example.sf2")
#sfid = fs.sfload("FluidR3_GM.sf2")
sfid = fs.sfload("Nice-Keys-Ultimate-V2.3.sf2")
#sfid = fs.sfload("OmegaGMGS2.sf2")
#sfid = fs.sfload("styvell-saxoaltovib.sf2")
#sfid = fs.sfload("463-Trumpet.sf2")
#sfid = fs.sfload("198-SY-1\ sax.SF2")
#sfid = fs.sfload("Santur.sf2")
#fs.program_select(0, sfid, 0, 0)  # Nice-Keys-Ultimate-V2.3.sf2
fs.program_select(0, sfid, 0, 11)
#fs.program_select(0, sfid, 0, 2)  # Electric piano OmegaGMGS2.sf2
#fs.program_select(0, sfid, 0, 26)  # Jazz Guitar OmegaGMGS2.sf2
#fs.program_select(0, sfid, 1, 65)  # Sax Omega styvell-saxoaltovib.sf2

tty.setcbreak(sys.stdin)

while True:
    try:

        if (velocity >= 127):
            print('Max velocity reached, truncating it to 127')
            velocity = 127

        if (velocity <= 0):
            print('Min velocity reached, truncating it to 0')
            velocity = 0

        keypressed = sys.stdin.read(1)

        if (keypressed == '/'):
            print('Cya!')
            break;
        elif (keypressed == '+'):
            print ('Velocity increased to ' + str(velocity))
            velocity = velocity + 1
            continue
        elif (keypressed == '-'):
            velocity = velocity - 1
            print ('Velocity decreased to ' + str(velocity))
            continue

        print (keypressed)
        print (keymap[keypressed])
        fs.noteon(0, keymap[keypressed], velocity)
        #time.sleep(0.120)
        #fs.noteoff(0, keymap[keypressed])
        print
    except:
        print ('Sorry, that key was not supported')

termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
sys.stdin.close()
fs.delete()
