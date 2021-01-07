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
slidingMotorOpen = None
slidingMotorClose = None
turningMotorOpen = None
turningMotorClose = None
slidingMotorOpenPin = 20
slidingMotorClosePin = 21
turningMotorOpenPin = 19
turningMotorClosePin = 26
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
    global slidingMotorOpen
    global turningMotorOpen

    inMotion = True
    isOpen = True
    turningMotorOpen.start(100)
    time.sleep(7)
    turningMotorOpen.stop()
    slidingMotorOpen.start(100)
    time.sleep(30)
    slidingMotorOpen.stop()
    inMotion = False

def closeBlinds():
    global isOpen
    global inMotion
    global slidingMotorClose
    global turningMotorClose

    inMotion = True
    isOpen = False
    slidingMotorClose.start(100)
    time.sleep(32)
    slidingMotorClose.stop()
    turningMotorClose.start(80)
    time.sleep(10)
    turningMotorClose.stop()
    inMotion = False

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

    GPIO.setup(slidingMotorOpenPin, GPIO.OUT)
    GPIO.setup(slidingMotorClosePin, GPIO.OUT)
    GPIO.setup(turningMotorOpenPin, GPIO.OUT)
    GPIO.setup(turningMotorClosePin, GPIO.OUT)

    global slidingMotorOpen
    global slidingMotorClose
    global turningMotorOpen
    global turningMotorClose

    slidingMotorOpen = GPIO.PWM(slidingMotorOpenPin, 100)
    slidingMotorClose = GPIO.PWM(slidingMotorClosePin, 100)
    turningMotorOpen = GPIO.PWM(turningMotorOpenPin, 100)
    turningMotorClose = GPIO.PWM(turningMotorClosePin, 100)

    slidingMotorOpen.stop()
    slidingMotorClose.stop()
    turningMotorOpen.stop()
    turningMotorClose.stop()

    # Close the blinds
    slidingMotorClose.start(100)
    time.sleep(60)
    slidingMotorClose.stop()
    turningMotorClose.start(75)
    time.sleep(45)
    turningMotorClose.stop()

    threading.Thread(target=checker).start()

if __name__ == "__main__":
    setup()
    app.run(host="0.0.0.0")
