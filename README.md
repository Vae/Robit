# Robit

"Robit" is the first in a series of robots intended to help me learn more about hardware, software and physical designs (CAD).

Robit itself is a small robot about 180mm in diameter (printable on an Ender 3), controllable using a web interface, using the following hardware constraints:
* 1x Raspberry Pi Zero with front mounted camera for FPV
* 1x OTG USB hub - this is needed since the Pi Zero only has one USB port
* 1x USB Wifi dongle
* 1x Arduino connected via USB
* 2x Stepper motor 28BYJ-48 with ULN2003 as a driver
* 1x off the shelf USB battery pack which continuously delivers power when connecting or disconnecting its charge port

These requirements were set to make the project as simple as possible. There's many other routes to accomplish the same outcome, but I wanted to keep things very simple for the first robot. Later robots will use more advanced techniques.

Core Goals, completed marked with ✅
* ✅ Web interface for controlling robot
* ✅ FPV
* Docking station for charging: should be able to drive the robot remotely to a dock to recharge
  * Allow the bot's wheels to drive onto docking station in order to prevent the bot from pushing it
  * Should have some texture to help prevent wheel slippage
  * ? Should the upper structure be on a bearing so that it can rotate to match bot orientation ?
    * Would need something on the bot to catch to make it rotate--the wheel wells

Stretch goals:
* Indoor mapping and navigation (Lidar/SLAM)
* Onboard RGB lighting

More to come