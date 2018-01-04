import random
import time
import math
import numpy as np

#import matplotlib.pyplot as plt
#import plotly.plotly as py
#from plotly.graph_objs import *
#from bpc_calibration import getCleanSensorData

sample_description = ""
textDescTest = " This is a test for BPC text file generation. \n"
'''finalArray = [[3.4, 10.49, 1.69, 10.06, 6.33, 6.48, 3.43, 12.94, 5.76, 5.54, 10.36, 4.82, 1.55],
              [10.98, 4.09, 0.3, 6.26, 14.32, 0.99, 8.79, 5.39, 11.73, 3.48, 11.78, 5.74, 11.13],
              [4.92, 7.13, 9.08, 12.37, 10.36, 7.36, 5.91, 7.53, 13.27, 10.57, 0.6, 0.33, 4.13],
              [13.58, 6.61, 7.9, 11.72, 6.14, 11.15, 9.16, 2.68, 4.79, 0.6, 0.97, 9.56, 0.19],
              [13.25, 1.94, 6.91, 0.29, 11.78, 6.53, 5.08, 7.86, 3.69, 10.08, 8.24, 0.07, 3.77],
              [5.45, 6.12, 2.56, 13.7, 10.48, 7.52, 14.51, 7.44, 9.12, 0.27, 14.8, 0.47, 8.53],
              [4.43, 6.27, 13.77, 11.04, 8.2, 4.44, 12.55, 1.44, 10.42, 9.3, 2.63, 12.15, 8.21],
              [11.8, 11.63, 12.81, 3.86, 13.33, 3.2, 4.4, 13.36, 5.76, 3.27, 1.14, 7.37, 14.72],
              [13.3, 7.19, 4.74, 9.89, 10.34, 8.28, 0.36, 14.1, 13.4, 7.98, 0.22, 11.41, 2.96],
              [7.41, 2.1, 2.11, 14.79, 4.28, 5.25, 10.35, 5.75, 10.12, 12.11, 6.28, 2.78, 11.73],
              [11.49, 2.84, 5.57, 2.34, 13.16, 4.69, 4.52, 9.4, 11.27, 1.03, 14.35, 3.49, 7.93],
              [1.01, 4.66, 11.51, 3.96, 10.17, 4.27, 4.44, 8.51, 1.9, 3.78, 0.77, 11.7, 8.6],
              [5.18, 4.42, 6.69, 7.63, 14.05, 6.28, 9.68, 6.71, 12.51, 12.73, 4.78, 13.57, 13.8]]

finalArray_Aprox_RealData = [[10.4, 10.49, 9.69, 8.06, 7.33, 11.48, 7.43, 14.94, 10.00, 8.92, 10.36, 4.82, 1.55],
                             [10.98, 4.09, 0.3, 6.26, 14.32, 0.99, 8.79, 5.39, 11.73, 3.48, 11.78, 5.74, 11.13],
                             [4.92, 7.13, 9.08, 12.37, 10.36, 7.36, 5.91, 7.53, 13.27, 10.57, 0.6, 0.33, 4.13],
                             [13.58, 6.61, 7.9, 11.72, 6.14, 11.15, 9.16, 2.68, 4.79, 0.6, 0.97, 9.56, 0.19],
                             [13.25, 1.94, 6.91, 0.29, 11.78, 6.53, 5.08, 7.86, 3.69, 10.08, 8.24, 0.07, 3.77],
                             [5.45, 6.12, 2.56, 13.7, 10.48, 7.52, 14.51, 7.44, 9.12, 0.27, 14.8, 0.47, 8.53],
                             [4.43, 6.27, 13.77, 11.04, 8.2, 4.44, 12.55, 1.44, 10.42, 9.3, 2.63, 12.15, 8.21],
                             [11.8, 11.63, 12.81, 3.86, 13.33, 3.2, 4.4, 13.36, 5.76, 3.27, 1.14, 7.37, 14.72],
                             [13.3, 7.19, 4.74, 9.89, 10.34, 8.28, 0.36, 14.1, 13.4, 7.98, 0.22, 11.41, 2.96],
                             [7.41, 2.1, 2.11, 14.79, 4.28, 5.25, 10.35, 5.75, 10.12, 12.11, 6.28, 2.78, 11.73],
                             [11.49, 2.84, 5.57, 2.34, 13.16, 4.69, 4.52, 9.4, 11.27, 1.03, 14.35, 3.49, 7.93],
                             [1.01, 4.66, 11.51, 3.96, 10.17, 4.27, 4.44, 8.51, 1.9, 3.78, 0.77, 11.7, 8.6],
                             [5.18, 4.42, 6.69, 7.63, 14.05, 6.28, 9.68, 6.71, 12.51, 12.73, 4.78, 13.57, 13.8]]

test3 = [[6.44, 6.60, 5.97, 12],
         [6.46, 6.62, 6.61, 12],
         [6.36, 6.57, 6.56, 12],
         [5.56, 6.51, 6.54, 12],
         [6.41, 5.13, 6.44, 12],
         [6.44, 6.54, 5.16, 12],
         [6.46, 6.60, 6.59, 12],
         [6.43, 6.59, 6.59, 12],
         [6.33, 6.62, 6.62, 12],
         [5.79, 6.60, 6.64, 12],
         [5.11, 6.44, 6.54, 12],
         [6.46, 6.74, 6.72, 12],
         [6.44, 6.84, 5.35, 12],
         [6.44, 7.13, 7.02, 12],
         [6.44, 7.22, 7.22, 12],
         [6.28, 7.14, 7.16, 12],
         [6.46, 6.52, 7.24, 12],
         [6.46, 7.18, 5.67, 12],
         [6.44, 7.00, 6.98, 12],
         [6.30, 6.96, 6.98, 12],
         [4.69, 6.60, 6.74, 12],
         [6.46, 6.54, 6.76, 12],
         [6.44, 6.93, 6.84, 12],
         [6.41, 7.24, 7.24, 12],
         [5.68, 6.27, 7.04, 12],
         [6.41, 6.27, 6.97, 12],
         [6.33, 6.91, 7.04, 12],
         [5.26, 5.68, 6.54, 12],
         [5.71, 6.56, 6.57, 12],
         [5.68, 6.64, 6.67, 12]]
'''
saved_measurent = []
finalArray2 = []
number_of_samples = 9
sensor_qty = 4
radius_of_ring = 15


# Test for three sensors in prototype
'''def clean_test(array):
    test_clean = array
    result = 0
    result_array = []
    for i in range(0, len(test_clean)):
        for j in range(0, len(test_clean[i]) - 1):
            test_clean[i][j] = round(7.5 - test_clean[i][j], 2)
            result = test_clean[i][j] - 7.5
            result_array.append(result)
    return test_clean
'''

# Creates a dummy array of array with random data from sensors, The they are
# rounded to the second decimal point. Also, we are subtracting the radius of the ring to the
# measurements because it gives us the measurement from the center to the sensor.
'''def fill_dummy():
    global finalArray
    for i in range(0, number_of_samples):
        finalArray.append([])
    for i in range(0, len(finalArray)):
        for j in range(0, sensor_qty - 1):
            number = radius_of_ring - random.uniform(0.0, 15.0)
            number = round(number, 2)
            finalArray[i].append(number)
        finalArray[i].append(round(random.uniform(15.24, 645), 2))
    print("UNSORTED ARRAY")
    print(finalArray)
    return finalArray
'''

# Resets all global variables in case of a discard or return home
def reset_BPC():
    global textDesc, sensorLiveMeasurements, sortedArray, finalArray
    textDesc = ""
    sensorLiveMeasurements = []
    finalArray = []
    sortedArray = []


# Gets current date for the generation of the text file, from the user's machine
def get_date():
    date = time.strftime("Created on %m/%d/%y %I:%M %p \n")
    return date


# Sample Description, user input
def set_sampleDescription(sample_description):
    global textDesc
    textDesc = sample_description
    return textDesc

'''
def capture_measurement():
    result_array  = getcleandata()
    save_measurent.append(result_array)
    return result_array
'''
# Checks for a sensor that's not reading and returns a list of damaged ones.
# If the sensors are not damaged, they passed the diagnostic
'''def sensors_diagnostic(array):
    if not array:
        print("Array must not be empty")
    sensors_check = array
    damaged_sensors = []
    for i in range(0, len(sensors_check) - 1):
        for j in range(0, sensor_qty - 1):
            if sensors_check[i][j] < 0 or sensors_check[i][j] > 16:
                damaged_sensors.append(i)
    if not damaged_sensors:
        return "DIAGNOSTIC PASSED"
    else:
        return damaged_sensors
'''
#def save_measurements():



# Sorts the measurements list for preview display and text file generation.
def sort_ByZeta(array):
    if not array:
        print("Array must not be empty")
    array.sort(key=lambda x: x[len(array) - 1])
    # print("SORTED BY ZETA")
    # print(array)
    return array


# Gets the average of each radius and multiplies it by two, thus the result
# the result is average diameter
def average_diameter(index, array):
    if index < 0:
        print("Index must not be negative or out of index of slice ")
    if not array:
        print("Array must not be empty.")
    avg_d = 0
    for i in range(0, len(array[index]) - 1):
        print(array[index][i])
        avg_d += (array[index][i]) * 2
    avg_d = round((avg_d / (len(array[index]) - 1)), 2)
    # print("AVERAGE DIAMETER")
    # print(avg_d)
    return avg_d


# Reads the Z-axis value for a determined index, used for preview and generate text file
def read_ultrasonic(index, array):
    if index < 0:
        print("Index must not be negative or out of index of slice ")
    if not array:
        print("Array must not be empty ")
    zeta = array[index][len(array[index]) - 1]
    print("READ ZETA")
    print(zeta)
    return zeta


# Deletes the element 'index' at the given array
def delete_measurement(index, array):
    if index < 0:
        print("Index must not be negative or out of index of slice.")
    if (len(array)) == 0:
        print("Array must not be empty. ")
    # global finalArray
    # delete = finalArray
    del array[index]


# Calulates te X and Y coordinates of the array of radius given by the Arduino respect to ring
# where centroid is (0,0)
def calculate_xy(index, array):
    if index < 0:
        print("Index must not be negative or out of index of slice ")
    if not array:
        print("Array must not be empty ")
    data = array
    angle = 0
    increment = 360 / (sensor_qty - 1)
    result_XY_coords = []
    # print("SENSOR DATA")
    # print(finalArray)
    for j in range(0, len(data[index]) - 1):
        x = round(data[index][j] * (math.cos(math.radians(angle))), 2)
        y = round(data[index][j] * (math.sin(math.radians(angle))), 2)
        angle += increment
        result_XY_coords.append([x, y])
    # print("XY COORDINATES REPECT TO CENTROIDE [0,0]")
    # print(result_XY_coords)
    return result_XY_coords


# Calculates the centroid of the object based an the X and Y coordinates
# Where index is the slice of mesures and array the data from the sensors.
def centroide_object(index, array):
    if index < 0:
        print("Index must not be negative or out of index of slice ")
    if not array:
        print("Array must not be empty ")
    XY_from_zerozero = calculate_xy(index, array)
    print("ARREGLO DE XY")
    print(XY_from_zerozero)
    x_T = []
    y_T = []
    for i in range(0, len(XY_from_zerozero)):
        x_coord = XY_from_zerozero[i][0]
        x_T.append(x_coord)
    for j in range(0, len(XY_from_zerozero)):
        y_coord = XY_from_zerozero[j][1]
        y_T.append(y_coord)

    object_centroid = [round(sum(x_T) / len(x_T), 2), round(sum(y_T) / len(y_T), 2)]
    # print("CENTROIDE RESPECTO AL SLICE")
    # print(object_centroid)
    # plt.scatter(x_T, y_T)
    # plt.show()
    return object_centroid


# This function calculates the polar coordinates with r in cm and theta in degrees.
# It receives the X and Y coordinates of an object and its center respect to the ring
def rect_to_polar(xy_array, center):
    if center[0] < -30 or center[0] > 30 or center[1] < -30 or center[1] > 30:
        print("Center is out of bounds ")
    if not xy_array:
        print("XY Array must not be empty ")

    polar_coords = []
    x_c = center[0]
    y_c = center[1]
    for i in range(0, len(xy_array)):
        x_o = xy_array[i][0]
        y_o = xy_array[i][1]
        x_total = x_o - x_c
        y_total = y_o - y_c
        r = math.sqrt(float(np.square(x_total)) + float(np.square(y_total)))
        r = round(r, 2)
        theta = math.atan2(y_total, x_total)
        theta = round(math.degrees(theta), 2)
        polar_coords.append([r, theta])
    print("COORDENADAS POLARES [RADIO, ANGULO] RESPECTO AL CENTRO DEL OBJETO")
    print(polar_coords)
    return polar_coords


# Generates a text file in the proyect folder. It receives as a parameter the data from the sensors.
# Then proceeds to call previous funcions for generating the zeta, polar coordinates, average diameter and centroide
# of the object being measured.
def generate_textfile(array):
    if not array:
        print("XY Array must not be empty ")
    array = sort_ByZeta(array)
    f = open("Samples.txt", "w+")
    f.write(set_sampleDescription(textDescTest))
    f.write(get_date())
    f.write("Samples take %s \n" % (len(array)))
    f.write(" ")
    for i in range(0, len(array)):
        center = centroide_object(i, array)
        xy = calculate_xy(i, array)
        polar = rect_to_polar(xy, center)
        f.write(" |%s|  " % read_ultrasonic(i, array))
        for j in range(0, len(polar)):
            f.write("  %s  " % (polar[j]))
        f.write("  Average Diameter |%s|" % average_diameter(i, array))
        f.write("  Centroide del objeto [ %s , %s ] " % (center[0], center[1]))
        f.write("\n ")
    return


#finalArray = fill_dummy()
print(finalArray)
delete_measurement(2, finalArray)
print(finalArray)
# average_diameter(0, test)
# print("TEST TO CLEAN")
# print(test3)
# test_limpio = clean_test(test3)
# print(test_limpio)

# finalArray = fill_dummy()
# average_diameter().demo(-1, finalArray)
# finalArray = fill_dummy()
# print("RANDOM DUMMY DATA")
# print(finalArray)

# print("DO SENSOR DIAGNOSTIC")
# diagnose = sensors_diagnostic(finalArray)
# print(diagnose)

# delete_measurement(2, finalArray)
# print("DELETE MEASUREMENT TEST")
# print(finalArray)
# for i in range(0, len(test_limpio)):
# test = calculate_xy(i, sort_ByZeta(test_limpio))
# avg = average_diameter(i, sort_ByZeta(test_limpio))
# print("AVERAGE DIAMETER TEST")
# print(avg)
# print("TEST XY COORDINATES RESPECT TO RING ")
# print(test)

# print("TEST 1")
# print(test)
# print(finalArray)
polar = rect_to_polar(calculate_xy(0, sort_ByZeta(finalArray)), centroide_object(0, sort_ByZeta(finalArray)))
print("TEST 2")
# print(polar)

# centroi = centroide_object(0, sort_ByZeta(finalArray))
# print("TEST 3")
# print(centroi)
print(finalArray)
# Functions
#final = getCleanSensorData()
generate_textfile(finalArray)
