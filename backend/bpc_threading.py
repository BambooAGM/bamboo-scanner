import threading

from serial import SerialException

from backend.bpc import save_measurements
from backend.sensors_manager import getInstantRawSensorData, getCleanSensorData, openArduinoSerial, closeArduinoSerial, \
    clearCache, calibrateAllSensors, sensorArray

# Semaphore lock to guarantee only 1 thread at a time
port_lock = threading.Semaphore()

# Signals we are reading
reading_sensors = threading.Event()
# Tells the thread to capture data; cleared when data is ready
capture_now = threading.Event()
# Tells the thread to calibrate sensors; cleared when done
calibrate_now = threading.Event()
# Signal to kill thread
kill_thread = threading.Event()
# Main program was closed
main_quit = threading.Event()

# Error flags
no_arduino = threading.Event()
disconnected = threading.Event()


def get_live_sensors(widget):
    """
    Runs in a separate thread to retrieve live sensor data and display it without blocking the GUI.

    :param widget: The widget whose queue we are populating (MeasureBPC Frame)
    :param reading_sensors: signals the GUI when the port has been opened
    :param main_quit: signals the main thread has ended, and so shall the threads
    :param kill_thread: kill signal of thread, set when navigating away from MeasureBPC
    :param no_arduino: event when arduino is not found
    :param disconnected: event when not able to read from serial
    :param port_lock: semaphore to avoid race on serial port
    :param capture_now: event when data wants to be captured
    :return: None
    """
    # Semaphore lock to guarantee only 1 thread at a time
    with port_lock:
        # open serial port
        try:
            openArduinoSerial()
        except IOError:
            no_arduino.set()
            print("no arduino found")
            return

        # Notify we are reading
        reading_sensors.set()

        # Keep reading sensors
        while not main_quit.is_set() and not kill_thread.is_set():
            try:
                # Data wants to be captured
                if capture_now.is_set():
                    # do not use cache
                    clearCache()
                    # Get sensor data
                    data = getCleanSensorData()
                    print("saving", data)
                    # Save data in backend
                    save_measurements(data)
                    # clear once it has been saved
                    capture_now.clear()

                elif calibrate_now.is_set():
                    # do not use cache -- needed ???
                    clearCache()

                    # run calibration
                    calibrateAllSensors()
                    print(sensorArray)

                    # signal calibration is done
                    calibrate_now.clear()

                # Show live feed
                else:
                    data = getInstantRawSensorData()
                    # Place data in queue so widget can access it in a non-blocking way
                    widget.add_to_queue(data)

            except SerialException:
                disconnected.set()
                reading_sensors.clear()
                print("arduino disconnected")
                return

        # kill signal received or main has ended
        reading_sensors.clear()
        kill_thread.clear()
        closeArduinoSerial()
        print("thread finished")
