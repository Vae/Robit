import time
from vae_serial_v1 import VaeSerial

class Robit:
    def __init__(self):
        self.serial = VaeSerial("/dev/ttyUSB0", 115200)
        self.start_ms = int(round(time.time() * 1000))
        self.invert = True
        self.swap = False
    def _getMotorValue(self, value):
        if self.invert: return -value
        return value
    def _getMotor(self, motor):
        if self.swap:
            if motor == 1: return 2
            elif motor == 2: return 1
        return motor

    def move(self, distance):
        self._sendCommand(f"M3M{self._getMotorValue(distance)}")
    def spin(self, distance):
        self._sendCommand(f"M{self._getMotor(1)}M{self._getMotorValue(distance)}\nM{self._getMotor(2)}M{-self._getMotorValue(distance)}")
        #self._sendCommand(f"M{self._getMotor(2)}M{-self._getMotorValue(distance)}")
    def reset(self):
        self._sendCommand("SR")
    def _sendCommand(self, command):
        self.serial.sendCommand(command)
