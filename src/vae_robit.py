import time
from vae_serial_v1 import VaeSerial

class Robit:
    def __init__(self):
        self.serial = VaeSerial("/dev/ttyUSB0", 115200)
        self.start_ms = int(round(time.time() * 1000))

    def moveForward(self, distance):
        pass
    def moveBackward(self, distance):
        pass
    def moveLeft(self, distance):
        pass
    def moveRight(self, distance):
        pass
    def spin(self, distance):
        pass