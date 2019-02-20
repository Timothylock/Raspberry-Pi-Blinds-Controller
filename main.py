from flask import Flask
from flask import request
import json
import RPi.GPIO as GPIO
import time
import threading
app = Flask(__name__)

# Variables
isOpen = False
inMotion = False
motorOpen = None
motorClose = None
motorOpenPin = 20
motorClosePin = 21

# App routes
@app.route("/")
def index():
    return "It Works! Try interacting with /state instead"


@app.route("/state", methods=['GET', 'POST'])
def state():
    if request.method == 'POST':
        return setState()
    elif request.method == "GET":
        return fetchState()

# Helper Functions
def setState():
    c = request.json

    if "active" not in c:
        return "missing \"active\" field", 400

    if c["active"] == "true":
        if turnOn():
            return "turned on", 200
        else:
            return "failed to turn on", 500

    if c["active"] == "false":
        if turnOff():
            return "turned off", 200
        else:
            return "failed to turn off", 500

    return "Invalid payload", 400

def fetchState():
    return json.dumps({"is_active": str(isOpen).lower()}), 200

def turnOn():
    global isOpen
    global inMotion

    # early bypass
    if isOpen:
        return True

    isOpen = True

    if inMotion:
        return False

    t = threading.Thread(target=openBlinds)
    t.start()

    return True

def turnOff():
    global isOpen
    global inMotion

    # early bypass
    if not isOpen:
        return True

    isOpen = False

    if inMotion:
        return False

    t = threading.Thread(target=closeBlinds)
    t.start()

    return True

def openBlinds():
    global isOpen
    global inMotion

    inMotion = True
    motorOpen.start(100)
    time.sleep(15)
    motorOpen.stop()
    inMotion = False

def closeBlinds():
    global isOpen
    global inMotion

    inMotion = True
    motorClose.start(60)
    time.sleep(45)
    motorClose.stop()
    inMotion = False


def setup():
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(motorOpenPin, GPIO.OUT)
    GPIO.setup(motorClosePin, GPIO.OUT)

    global motorOpen
    global motorClose

    motorOpen = GPIO.PWM(motorOpenPin, 100)
    motorClose = GPIO.PWM(motorClosePin, 100)

    # Close the blinds slowly
    motorClose.start(60)
    time.sleep(60)
    motorClose.stop()

if __name__ == "__main__":
    setup()
    app.run(host="0.0.0.0")
