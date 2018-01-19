import math

import numpy as np

from backend.sensors_manager import distToPointSingleIRSensor, sensorArray
from backend.utils import get_timestamp, twoPointDistance

sample_description = ""
saved_measurement = []
finalArray2 = []
sensor_qty = 4

# calibration settings
ring_diameter = 0.0
calibration_obj_diameter = 0.0
rail_z_distance = 0.0


def get_calibration_settings():
    return ring_diameter, calibration_obj_diameter, rail_z_distance


def set_calibration_settings(ringDiameter, obj_diameter, distance_z):
    global ring_diameter, calibration_obj_diameter, rail_z_distance

    ring_diameter = ringDiameter
    calibration_obj_diameter = obj_diameter
    rail_z_distance = distance_z


# Resets all global variables in case of a discard or return home
def reset_bpc_backend():
    global sample_description, saved_measurement, sortedArray, finalArray, ring_diameter, calibration_obj_diameter, rail_z_distance
    sample_description = ""
    saved_measurement.clear()

    ring_diameter = 0.0
    calibration_obj_diameter = 0.0
    rail_z_distance = 0.0
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


def extract_data_from_saved_measurements():
    """
    Translates recorded distances into rectangular coordinates.

    :return: x, y, z coordinates for each snapshot, along with its centroid and average diameter
    return format = ((temp_xS, temp_yS, temp_zS), (temp_centroid_xS, temp_centroid_yS, temp_centroid_zS))
    """
    # surface coordinates
    temp_xS = []
    temp_yS = []
    temp_zS = []

    # centroid coordinates
    temp_centroid_xS = []
    temp_centroid_yS = []
    temp_centroid_zS = []

    # average diameters
    temp_average_diameters = []

    # convert captured measurements into rectangular coordinates
    for sensor_data in saved_measurement:
        # reading from sensor Z * applied calibration factor
        z = sensor_data[-1] * sensorArray[-1].factor

        # store diameters here to calculate average
        temp_diameters = []

        # convert IR sensor readings to x, y
        for i in range(len(sensor_data) - 1):
            (x, y) = distToPointSingleIRSensor(s=sensorArray[i], distanceMeasured=sensor_data[i])

            # radius
            r = twoPointDistance((x, y), (0, 0))

            # save diameter for average
            temp_diameters.append(r * 2.0)

            # save them separately
            temp_xS.append(x)
            temp_yS.append(y)
            temp_zS.append(z)

        # calculate centroid for this group of sensor data
        centroid_x = np.mean(temp_xS)
        centroid_y = np.mean(temp_yS)

        # save them separately
        temp_centroid_xS.append(centroid_x)
        temp_centroid_yS.append(centroid_y)
        temp_centroid_zS.append(z)

        # calculate average diameter
        average_diameter = np.mean(temp_diameters)
        temp_average_diameters.append(average_diameter)

    return ((temp_xS, temp_yS, temp_zS), (temp_centroid_xS, temp_centroid_yS, temp_centroid_zS), temp_average_diameters)


def generate_text_file(file_path):
    global sample_description

    ((xS, yS, zS), (centroid_xS, centroid_yS, centroid_zS), avg_diameters) = extract_data_from_saved_measurements()

    try:
        f = open(file_path, "w+")
        f.write(get_timestamp())
        f.write("\n")

        # write sample description
        f.write("Bamboo sample description:\n")
        f.write("%s\n" % sample_description)
        f.write("\n")

        # write x, y, z coordinates
        f.write("Rectangular coordinates:\n")
        f.write("x, y, z\n")
        for (x, y, z) in zip(xS, yS, zS):
            f.write("%s, %s, %s\n" % (x, y, z))
        f.write("\n")

        # write centroids
        f.write("Centroids:\n")
        f.write("x, y, z\n")
        for (x, y, z) in zip(centroid_xS, centroid_yS, centroid_zS):
            f.write("%s, %s, %s\n" % (x, y, z))
        f.write("\n")

        # write average diameter
        f.write("Average Diameters:\n")
        f.write("z, avg diameter\n")
        for (z, avg_diameter) in zip(centroid_zS, avg_diameters):
            f.write("%s, %s\n" % (z, avg_diameter))
        f.write("\n")

        f.close()
        return True

    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno, e.strerror))
        return False


# Generates a text file in the proyect folder. It receives as a parameter the data from the sensors.
# Then proceeds to call previous funcions for generating the zeta, polar coordinates, average diameter and centroide
# of the object being measured.
# def generate_textfile(array):
#     # TODO update this
#     if not array:
#         print("XY Array must not be empty ")
#     array = sort_ByZeta(array)
#     f = open("Samples.txt", "w+")
#     f.write(sample_description)
#     f.write(get_timestamp())
#     f.write("Samples take %s \n" % (len(array)))
#     f.write(" ")
#     for i in range(0, len(array)):
#         center = centroide_object(i, array)
#         xy = calculate_xy(i, array)
#         polar = rect_to_polar(xy, center)
#         f.write(" |%s|  " % read_ultrasonic(i, array))
#         for j in range(0, len(polar)):
#             f.write("  %s  " % (polar[j]))
#         f.write("  Average Diameter |%s|" % average_diameter(i, array))
#         f.write("  Centroide del objeto [ %s , %s ] " % (center[0], center[1]))
#         f.write("\n ")
#     return
