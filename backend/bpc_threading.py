import threading

from serial import SerialException

from backend.bpc import save_measurements, ring_diameter, calibration_obj_radius, rail_z_distance
from backend.sensors_manager import *

# Semaphore lock to guarantee only 1 thread at a time
port_lock = threading.Semaphore()

# Error flags
no_arduino = threading.Event()
disconnected = threading.Event()

# Main program was closed
main_quit = threading.Event()


class LiveFeedThread(threading.Thread):
    """
    A thread to display live sensor data, capture it, or calibrate sensors.
    """

    def __init__(self, widget):
        threading.Thread.__init__(self)

        # the widget who creates this thread; for writing data to its queue
        self.widget = widget

        # an event to kill this thread
        self.kill_thread = threading.Event()

        # Signals port is open
        self.reading_sensors = threading.Event()

        # Tells the thread to capture data; cleared when data is ready
        self.capture_now = threading.Event()
        # Tell the gui to grab the captured data
        self.capture_done = threading.Event()

        # Tells the thread to calibrate sensors; cleared when done
        self.calibrate_now = threading.Event()
        # Tell the gui to grab the calibration data
        self.calibration_done = threading.Event()

    def run(self):
        # Semaphore lock to guarantee only 1 thread at a time
        with port_lock:

            # don't bother if the user has already left the tool
            if not main_quit.is_set() and not self.kill_thread.is_set():
                # open serial port
                try:
                    openArduinoSerial()
                except IOError:
                    no_arduino.set()
                    print("no arduino found")
                    return

                # Notify we are reading
                self.reading_sensors.set()

                # Keep reading sensors
                while not main_quit.is_set() and not self.kill_thread.is_set():
                    try:
                        # User wants to capture data
                        if self.capture_now.is_set() and not self.capture_done.is_set():
                            # do not use cache
                            clearCache()

                            # Get sensor data
                            data = getCleanSensorData()

                            # don't save if the user has already left the tool
                            if not main_quit.is_set() and not self.kill_thread.is_set():
                                # Save data in backend
                                save_measurements(data)

                                # signal data has been captured
                                self.capture_done.set()
                            else:
                                print("capture aborted")

                        # User wants to calibrate sensors
                        elif self.calibrate_now.is_set() and not self.calibration_done.is_set():
                            # do not use cache
                            clearCache()

                            # init sensors
                            initSensors(structureRadius=ring_diameter * 0.5)

                            # clear cache again
                            clearCache()

                            # run calibration
                            calibrateAllSensors(testRadius=calibration_obj_radius, testDistance=rail_z_distance)
                            print(sensorArray)

                            # don't give the signal if the user has already left the tool
                            if not main_quit.is_set() and not self.kill_thread.is_set():
                                # signal calibration is done
                                self.calibration_done.set()

                        # Show live feed
                        else:
                            data = getInstantRawSensorData()
                            # Place data in queue so widget can access it in a non-blocking way
                            self.widget.add_to_queue(data)

                    except SerialException:
                        disconnected.set()
                        print("arduino disconnected")
                        return

                # close serial port
                closeArduinoSerial()

            print("thread finished")
