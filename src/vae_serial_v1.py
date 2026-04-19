import threading
import time
import serial
from collections import deque

class VaeSerialMotor:
    def __init__(self, index):
        self.index = index
        self.position = 0
        self.maxSpeed = 0
        self.acceleration = 0
        self.remainingTravel = 0
        self.targetPosition = 0
    def state(self):
        return {
            "index": self.index,
            "position": self.position,
            "maxSpeed": self.maxSpeed,
            "acceleration": self.acceleration,
            "remainingTravel": self.remainingTravel,
            "targetPosition": self.targetPosition
        }

class VaeSerial:
    def __init__(self, serialPort: str, serialBaudRate: int, serialTimeout: int = 1):
        self.serial = ser = serial.Serial(serialPort, serialBaudRate, timeout=serialTimeout)
        self.position = (0, 0)
        self.motorCount = 2
        self.motors = []
        for i in range(self.motorCount):
            self.motors.append(VaeSerialMotor(i))

        self.MAX_LINES = 100
        self.history = deque(maxlen=self.MAX_LINES)
        self.history_lock = threading.Lock()
        self.serial_write_lock = threading.Lock()

        # Start background reader thread
        self.readerThread = threading.Thread(target=self._serial_reader, daemon=True).start()
        self.reportInterval = 2

        self.timerThread = threading.Thread(target=self._run_periodically, daemon=True)  # Set as daemon to stop when main program exits
        self.timerThread.start()

        self.targetReached = None

    def setTargetReached(self, method):
        self.targetReached = method

    def sendCommand(self, command):
        with self.serial_write_lock:
            self.serial.write((command + "\n").encode())
            self.serial.flush()

    def parse(self, line):
        #First check if this is a report line (starts with :)
        if line[0] == ":":
            return

        elements = line.split()
        elementContext = ""
        elementIndex = 0
        motorIndex = 0
        motorsAffected = 0

        for element in elements:
            match element[0]:
                case 'A' | 'X' | 'P' | 'R' | 'T':
                    elementContext = element[0]
                case _:
                    motorIndex += 1
                    elements[elementIndex] = elementContext + elements[elementIndex]
            value = elements[elementIndex][1:]
            #print(f"Motor {motorIndex} : {elementContext} with value {value}")

            match elementContext:
                case 'A':
                    self.motors[motorIndex].acceleration = float(value)
                case 'X':
                    self.motors[motorIndex].position = float(value)
                case 'P':
                    self.motors[motorIndex].position = int(value)
                case 'R':
                    if self.motors[motorIndex].remainingTravel != int(value):
                        self.motors[motorIndex].remainingTravel = int(value)
                        motorsAffected += 1
                    if self.motors[0].remainingTravel == 0 and self.motors[1].remainingTravel == 0:
                        self.sendCommand("M3D")
                        # print("Stop motors")
                case 'T':
                    self.motors[motorIndex].targetPosition = int(value)
            elementIndex += 1
            motorIndex = 0

    def _serial_reader(self):
        """Continuously read from serial and store lines"""
        while True:
            try:
                line = self.serial.readline().decode(errors="ignore").strip()
                if line:
                    # print(f"Line: {line}")
                    with self.history_lock:
                        self.history.append(line)
                        self.parse(line)
            except Exception as e:
                with self.history_lock:
                    self.history.append(f"[ERROR] {e}")
                time.sleep(1)

    def _run_periodically(self):
        while True:
            self.sendCommand("RP")
            time.sleep(self.reportInterval)  # Sleep for 1 second

    def state(self):
        return {
            "motors": (
                self.motors[0].state(),
                self.motors[1].state(),
            )
        }