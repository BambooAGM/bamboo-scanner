import math

import numpy as np

from backend.utils import get_timestamp

sample_description = ""
saved_measurement = []
finalArray2 = []
sensor_qty = 4

# calibration settings
ring_diameter = 0.0
calibration_obj_radius = 0.0
rail_z_distance = 0.0


def set_calibration_settings(ringDiameter, obj_radius, distance_z):
    global ring_diameter, calibration_obj_radius, rail_z_distance

    ring_diameter = ringDiameter
    calibration_obj_radius = obj_radius
    rail_z_distance = distance_z


# Resets all global variables in case of a discard or return home
def reset_bpc_backend():
    global sample_description, saved_measurement, sortedArray, finalArray
    sample_description = ""
    saved_measurement.clear()
    # finalArray.clear()
    # sortedArray.clear()


# Sample Description, user input
def set_sampleDescription(description):
    global sample_description

    sample_description = description


def save_measurements(array):
    global saved_measurement

    saved_measurement.append(array)


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
def delete_measurement(array):
    global saved_measurement
    if not array:
        return saved_measurement
    adjust = 0
    for i in range(0, len(array)):
        del saved_measurement[array[i]-adjust]
        adjust += 1
    return saved_measurement


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
    # TODO update this
    if not array:
        print("XY Array must not be empty ")
    array = sort_ByZeta(array)
    f = open("Samples.txt", "w+")
    f.write(sample_description)
    f.write(get_timestamp())
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
