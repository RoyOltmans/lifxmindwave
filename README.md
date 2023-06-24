# lifxmindwave
Release Beta 2023
A while ago I got a question if I could get this project working for the Permenant Future Lab in Utrecht (thats where I build this Proof Of Concept in a evenening). Therefor it's quite a while ago that I meshed this up.

Soon after I started the first problems popped up. I build this project on a 64bit machine and PMF wanted a Arm solutin (RPI). This took a couple of months where I spent some hours to fix it with a current version of Raspbian and a legacy version of Python2.7 combined with some other interesting problems I wont delve to deep in I managed to get it all working.

After that and testing the real problems rised up the LIFX api moved from beta to stable and changed in these 6 years. They did not work anymore, so I had to write a whole new API integration (lazy me only for sending).
Als the Bluetooth connection is somewhat unstable on ARM so I had to write a lot of error catching around it to work.

Now the whole env has moved from alpha (quick and dirty), to a bit more tidy.

The remarks below still need to be taken serious.

Have fun if you want to use or reuse this.

Release Alpha 2017
Mashup of two features Lifx and Mindwave. 
This creates a view of EEG signals via Mindwave measurements and visualizes this in the real world trough Lifx light bulbs.

This was a quick and dirty solution that works, I do not give any guarantees if this will work for you and or will damage any soft or hardware. 

Created with help of:
 Akloster/Python-mindwave https://github.com/akloster/python-mindwave Software License Agreement (BSD License)
 niltonvolpato/python-progressbar https://github.com/niltonvolpato/python-progressbar (GNU LGPL license or BSD license)
 phoniclynx/NateKodilifx https://github.com/phoniclynx/NateKodilifx (nothing found)
