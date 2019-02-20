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
desiredState = "closed"

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
    global desiredState
    c = request.json

    if "active" not in c:
        return "missing \"active\" field", 400

    if c["active"] == "true":
        desiredState = "open"

    if c["active"] == "false":
        desiredState = "closed"

    return "OK", 200

def fetchState():
    return json.dumps({"is_active": str(isOpen).lower()}), 200

def turnOn():
    global desiredState
    desiredState = "open"
    return True

def turnOff():
    global desiredState
    desiredState = "closed"
    return True

def openBlinds():
    global isOpen
    global inMotion
    global motorOpen

    inMotion = True
    motorOpen.start(100)
    time.sleep(15)
    motorOpen.stop()
    inMotion = False
    isOpen = True

def closeBlinds():
    global isOpen
    global inMotion
    global motorClose

    inMotion = True
    motorClose.start(60)
    time.sleep(45)
    motorClose.stop()
    inMotion = False
    isOpen = False

def checker():
    global isOpen
    global inMotion
    global desiredState

    while True:
        time.sleep(0.5)

        # Skip if the blinds are in motion
        if inMotion:
            continue

        if desiredState == "open" and not isOpen:
            threading.Thread(target=openBlinds).start()

        if desiredState == "closed" and isOpen:
            threading.Thread(target=closeBlinds).start()


def setup():
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(motorOpenPin, GPIO.OUT)
    GPIO.setup(motorClosePin, GPIO.OUT)

    global motorOpen
    global motorClose

    motorOpen = GPIO.PWM(motorOpenPin, 100)
    motorClose = GPIO.PWM(motorClosePin, 100)

    motorOpen.stop()
    motorClose.stop()

    # Close the blinds slowly
    motorClose.start(60)
    time.sleep(60)
    motorClose.stop()

    threading.Thread(target=checker).start()

if __name__ == "__main__":
    setup()
    app.run(host="0.0.0.0")
