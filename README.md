iSynth

iSynth is a simple music synthesizer written in 
Python & utilizes the pyFluidSynth as well as 
FluidSynth libraries for production of sound.


Which scripts to run ?

To do a simple keyboard test :
    # cd fluidsynth
    # python hamsadhwani_keytest.py

To test with Myoware's Muscle Sensor for modulating
the velocity of a keypress :
    # cd myosensor
    # python hamsadhwani_single_threshold.py
        or
    # hamsadhwani_fine_threshold.py

To test with the virtual keyboard (printed on a sheet
of paper with a camera for OpenCV feed) :
    # cd virtualkeyboard
    # python3 final_music_vkeyboard.py
    
CREDITS 

For detecting fingerpresses on the virtual keyboard, we re-used
an existing algorithm implemented by Joe Thomas as described in 
his webpage :

    https://jsthomas.github.io/vkeyboard.html

His paper can be found here :

    https://jsthomas.github.io/docs/vkeyboard/vkeyboard.pdf

Also, the following code was adapted to suit our needs :

    https://jsthomas.github.io/docs/vkeyboard/vkeyboard.zip
