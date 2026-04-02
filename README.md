# Robit

"Robit" is the first in a series of robots intended to help me learn more about hardware, software and physical designs (CAD).

Robit itself is a small robot about 120cm in diameter, controllable using a web interface, using the following hardware constraints:
* 1x Raspberry Pi Zero with front mounted camera for FPV
* 1x OTG USB hub - this is needed since the Pi Zero only has one USB port
* USB Wifi dongle
* 1x Arduino connected via USB
* 2x Stepper motor 28BYJ-48 with ULN2003 as a driver
* 1x off the shelf USB battery pack which continuously delivers power when connecting or disconnecting a charge port

These requirements were set to make the project as simple as possible. There's many other routes to accomplish the same outcome, but I wanted to keep things very simple for the first robot. Later robots will use more advanced techniques.

There are stretch goals, but they may be applied to future robots:
* Indoor mapping and navigation (Lidar/SLAM)
* Onboard RGB lighting

More to come