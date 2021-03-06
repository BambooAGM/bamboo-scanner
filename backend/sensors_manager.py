import math
import statistics
import time
import warnings

import serial
import serial.tools.list_ports

from backend.utils import twoPointDistance

sensorArray = []
sensors_initialized = False

numberOfSamples = 10
cacheStructuredSensorData = []
usingCache = False

arduinoSerial = None
isPortOpen = False


# Returns usingCache value. Determines if system looks for new data or uses
# data stored in cacheStructuredSensorData
def isUsingCache():
    global usingCache
    return usingCache


# Clears cache, both usingCache and cacheStructuredSensorDara
def clearCache():
    global usingCache, cacheStructuredSensorData

    usingCache = False
    cacheStructuredSensorData.clear()
    print("Cache Cleared")


# Returns a line of raw data from Arduino.
def getInstantRawSensorData():
    global arduinoSerial, isPortOpen

    if isPortOpen:
        readLine = arduinoSerial.readline()
        lineFromPort = str(readLine)[2:len(readLine)]

        splittedArray = lineFromPort.split(";")

        return splittedArray

    else:
        openArduinoSerial()
        return getInstantRawSensorData()


# Gets data from Arduino and stores it in an array containing strings of the
# raw data from USB bus. Returns array with strings.
def getRawSensorData():
    ser = openArduinoSerial()

    resultsFromPort = []

    # Determines number of samples to be taken from USB bus
    for i in range(numberOfSamples):
        lineFromPortByteArray = ser.readline()
        # Convert bytes from USB to string. Strips first two characters
        lineFromPort = str(lineFromPortByteArray)[2:len(lineFromPortByteArray)]
        resultsFromPort.append(lineFromPort)

    return resultsFromPort


# Gets raw sensor data and creates an array of arrays. Each array contains sensor data
# correlated to its position (index 0 contains an array with S0 data from samples).
def getStructuredSensorData():
    # Has to be done in order to reference global variable
    global usingCache, cacheStructuredSensorData

    if (usingCache == True):
        if (len(cacheStructuredSensorData) <= 0):
            usingCache = False
            getStructuredSensorData()
        else:
            return cacheStructuredSensorData

    else:

        finalArray = []
        resultsFromPort = getRawSensorData()
        # Just to determine number of sensors reported by Arduino
        firstSplit = resultsFromPort[0].split(";")
        numberOfSensors = len(firstSplit)

        # Creates an array per sensor
        for i in range(numberOfSensors):
            finalArray.append([])

        # Iterates through samples and save each sensor data to its respective array
        for i in range(0, len(resultsFromPort)):

            splittedLine = resultsFromPort[i].split(";")
            # print(splittedLine)

            for j in range(numberOfSensors):
                finalArray[j].append(float(splittedLine[j]))

        # Cache data is now the data just collected
        # cacheStructuredSensorData = finalArray
        # Forces to use cache unless cache is cleared by invoking clearCache()
        # usingCache = True

        return finalArray


# Gets the Mean from each sensor data. Returns an array of floats.
def getMeanSensorData(data):
    try:
        resultArray = []

        for i in range(0, len(data)):
            resultArray.append(round(statistics.mean(data[i]), 2))

        return resultArray

    except statistics.StatisticsError as e:
        print("There was an error with the statistics module")
        print(e)
        return []


# Gets the Standard Deviation from each sensor data. Returns an array of floats.
def getStdevSensorData(data):
    try:
        resultArray = []

        for i in range(0, len(data)):
            resultArray.append(round(statistics.stdev(data[i]), 2))

        return resultArray

    except statistics.StatisticsError as e:
        print("There was an error with the statistics module")
        print(e)
        return []


# Removes outliers using mean and stdev for each sensor data. After removing ouliers,
# returns the average of the remaining data.
def getCleanSensorData():
    finalArray = []
    structuredData = getStructuredSensorData()
    meanData = getMeanSensorData(structuredData)
    stdevData = getStdevSensorData(structuredData)

    # print(structuredData)
    # print(meanData)
    # print(stdevData)

    for i in range(0, len(structuredData)):
        s = structuredData[i]
        mean = meanData[i]
        stdev = stdevData[i]
        temp_list = [x for x in s if (x > mean - 2 * stdev)]
        temp_list = [x for x in temp_list if (x < mean + 2 * stdev)]

        if (len(temp_list) > 0):
            finalArray.append(round(statistics.mean(temp_list), 2))

        else:
            finalArray.append(0.0)

    return finalArray


# Looks for Arduino port and opens it.
def openArduinoSerial():
    global arduinoSerial, isPortOpen

    if not isPortOpen:
        print("Searching for Arduino Port...")

        arduino_ports = [  # List of ports containing the word Arduino in their description
            p.device
            for p in serial.tools.list_ports.comports()
            if 'Arduino' in p.description
        ]
        if not arduino_ports:
            raise IOError("No Arduino found")
        if len(arduino_ports) > 1:
            warnings.warn('Multiple Arduinos found - using the first')

        arduinoSerial = serial.Serial(arduino_ports[0])
        print("Arduino Port found at %s" % (arduino_ports[0]))

        time.sleep(3)

        print("NOTICE: START signal send to Arduino")

        # Send START signal to Arduino. Has to be encoded from string to bytes.
        arduinoSerial.write("START".encode())
        readLine = arduinoSerial.readline()

        # Checks for handshake STARTREC
        while ("STARTREC" not in str(readLine)[2:len(readLine)]):
            print("WARNING: START not received, trying again...")
            print(readLine)
            time.sleep(1)
            # Send START signal again
            arduinoSerial.write("START".encode())
            readline = arduinoSerial.readline()

        print("NOTICE: Arduino Handshake Received")

        isPortOpen = True

    return arduinoSerial


def closeArduinoSerial():
    global arduinoSerial, isPortOpen

    arduinoSerial.write("STOP".encode())
    readLine = arduinoSerial.readline()

    # Checks for handshake STOPREC
    while ("STOPREC" not in str(readLine)[2:len(readLine)]):
        print("WARNING: STOP not received, trying again...")
        time.sleep(1)
        # Send STOP signal again
        arduinoSerial.write("STOP".encode())
        readLine = arduinoSerial.readline()

    print("NOTICE: Arduino Handshake Received")

    arduinoSerial.close()
    isPortOpen = False


def hardResetArduinoSerial():
    global arduinoSerial, isPortOpen

    arduinoSerial = None
    isPortOpen = False


###########################################################
## CALIBRATION
###########################################################
def are_sensors_initialized():
    return sensors_initialized


def threePointAngle(vertexp1, p2, p3):
    p12 = twoPointDistance(vertexp1, p2)
    p13 = twoPointDistance(vertexp1, p3)
    p23 = twoPointDistance(p2, p3)

    result = math.degrees(math.acos(round((pow(p12, 2.0) + pow(p13, 2.0) - pow(p23, 2.0)) / (2.0 * p12 * p13), 10)))

    return result


class IRSensor(object):
    # The class "constructor" - It's actually an initializer
    def __init__(self, xi, yi):
        self.xi = xi
        self.yi = yi
        self.xf = 0.0
        self.yf = 0.0
        self.r = 0.0  # CAMBIAR A 0
        self.isCalibrated = False
        self.repeatMeasurement = False
        self.devAngle = 0


class UltSensor(object):
    # The class "constructor" - It's actually an initializer
    def __init__(self):
        self.factor = 1


def PointsInCircum(r, n):
    return [(math.cos(2.0 * math.pi / n * x) * r, math.sin(2.0 * math.pi / n * x) * r) for x in range(0, n + 1)]


def initSensors(structureRadius=11.5):
    global sensorArray

    # clear sensor array
    sensorArray.clear()

    numberOfSensors = len(getStructuredSensorData())
    # numberOfSensors = 13 #TEMPORAL TWEAK
    # print(numberOfSensors)

    angle = 360
    decrement = 360 / (numberOfSensors - 1)

    for i in range(0, numberOfSensors - 1):
        # print(angle)
        x = round(structureRadius * (math.cos(math.radians(angle))), 2)
        y = round(structureRadius * (math.sin(math.radians(angle))), 2)
        angle = angle - decrement
        sensorArray.append(IRSensor(x, y))

    sensorArray.append(UltSensor())


def calibrateSingleIRSensor(s, distanceMeasured, testPoints):
    closestDiff = 999999
    closestPoint = (0, 0)
    r = 0.0

    for p in testPoints:
        tempDistance = math.sqrt(pow((p[0] - s.xi), 2.0) + pow((p[1] - s.yi), 2.0))
        tempDiff = math.fabs(tempDistance - distanceMeasured)

        if (tempDiff < closestDiff):
            closestDiff = tempDiff
            closestPoint = p
            r = tempDistance

    s.xf = closestPoint[0]
    s.yf = closestPoint[1]
    s.r = r

    deviation = threePointAngle((s.xi, s.yi), closestPoint, (0.0, 0.0))  # HACER TEST
    s.devAngle = round(deviation, 2)

    return s


def calibrateSingleUltSensor(s, distanceMeasured, testDistance):
    try:
        s.factor = testDistance / distanceMeasured

        return s

    except ZeroDivisionError:
        s.factor = 1

        return s


def calibrateAllSensors(testRadius=1.58, testDistance=10):
    global sensorArray, sensors_initialized

    if (len(sensorArray) == 0):
        initSensors()

    # Generate virtual calibration object
    testPoints = PointsInCircum(testRadius, 1000)

    # Grab fresh sensor readings
    measuredDistances = getCleanSensorData()

    # calibrate IR sensors
    for i in range(0, len(sensorArray) - 1):
        sensorArray[i] = calibrateSingleIRSensor(sensorArray[i], measuredDistances[i], testPoints)

    # calibrate ultrasonic sensor
    sensorArray[-1] = calibrateSingleUltSensor(sensorArray[-1], measuredDistances[-1], testDistance)

    # flag that sensors have been initialized/calibrated
    sensors_initialized = True


###############################################################
def distToPointSingleIRSensor(s, distanceMeasured):
    t = distanceMeasured / s.r

    if (t < 0 or distanceMeasured > 16):  # 16cm is the radius of the structure
        s.repeatReading = True

    newCoordinate = (((1.0 - t) * s.xi) + (t * s.xf), ((1.0 - t) * s.yi) + (t * s.yf))
    return newCoordinate


def distToPointAllIRSensors():
    global sensorArray
    resultCoordinates = []

    if (len(sensorArray) == 0):
        initSensors()

    measurements = getCleanSensorData()

    for i in range(0, len(sensorArray) - 1):
        resultCoordinates.append(distToPointSingleIRSensor(sensorArray[i], measurements[i]))

    return resultCoordinates
