import queue
import threading
from tkinter import *
from gui.widgets.grid_helpers import make_rows_responsive, make_columns_responsive
from gui.widgets.custom import TableLeftHeaders, YellowButton, GreenButton
from backend.sensors_manager import getInstantRawSensorData, closeArduinoSerial


def get_live_sensors(widget):
    while widget.do_sensors_update:
        # show loading

        # Fetch sensor data from arduino
        data = getInstantRawSensorData()

        # hide loading

        # Place data in queue so widget can access it in a non-blocking way
        widget.add_to_queue(data)

    closeArduinoSerial()
    print("thread finished")


class MeasureBPC(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.title = "Live Sensor Readings (cm)"
        self.queue = queue.LifoQueue()
        self.initialize_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)
        self.bind("<<LeaveFrame>>", self.on_leave_frame)

    def initialize_widgets(self):
        # Watchers
        # Update captured count
        self.count_str = StringVar()
        self.count_number = IntVar()
        self.count_number.trace("w", self.update_count_label)
        self.count_number.set(0)
        
        # 12 IR sensors
        sensor_headers = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10", "S11", "S12"]
        self.table = TableLeftHeaders(self, rows=len(sensor_headers), columns=1, header_values=sensor_headers)
        self.table.grid(row=0, column=0, rowspan=4)

        # Sensor Z
        self.z_value = StringVar()
        self.z_label = Label(self, textvariable=self.z_value, font=self.controller.important_font)
        self.z_label.grid(row=0, column=1, sticky=S)

        # captured count
        self.captured_count = Label(self, textvariable=self.count_str, font=self.controller.bold_font)
        self.captured_count.grid(row=1, column=1, sticky=S, pady=5)

        # capture button
        self.capture_button = YellowButton(self, text="CAPTURE", command=self.capture)
        self.capture_button.grid(row=2, column=1, sticky=N)

        # view results button
        self.results_button = GreenButton(self, text="View Results", command=self.view_results,
                                          image=self.controller.arrow_right, compound=RIGHT)
        self.results_button.grid(row=3, column=1)

        make_rows_responsive(self)
        make_columns_responsive(self)

    def add_to_queue(self, data):
        self.queue.put(data)

    def update_sensors(self):
        try:
            while True:
                data = self.queue.get_nowait()
                print(data)

                # Update GUI with new sensor data
                self.table.update_cells(data[0: len(data) - 1])
                self.z_value.set("Z = " + data[len(data) - 1] + " cm")

                self.update_idletasks()
        except queue.Empty:
            pass

        self.after(100, self.update_sensors)

    def on_show_frame(self, event=None):
        #TODO update count label
        # bpc.get_number_captured()
        self.update_results_button()
        
        # Start live feed
        self.do_sensors_update = True
        self.live_thread = threading.Thread(target=lambda: get_live_sensors(self), name="live_sensors")
        self.live_thread.start()
        self.update_sensors()

    def on_leave_frame(self, event=None):
        # stop live feed and close serial port
        self.do_sensors_update = False

    def capture(self):
        #bpc.save_measurements()
        # update captured count label
        self.count_number.set(self.count_number.get() + 1)

        # enable view results button after the 1st capture
        if self.count_number.get() == 1:
            self.update_results_button()
        print("captured")

    def update_results_button(self):
        if self.count_number.get():
            self.results_button.grid()
        else:
            self.results_button.grid_remove()

    def update_count_label(self, *args):
        self.count_str.set(str(self.count_number.get()) + " measurements captured")

    def view_results(self):
        self.controller.show_frame("ResultsBPC")

    def reset(self):
        # reset captured count
        self.count_number.set(0)
