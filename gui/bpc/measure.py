import queue
from tkinter import messagebox
from tkinter import *
from backend.bpc import saved_measurement
from backend.bpc_threading import *
from gui.widgets.grid_helpers import make_rows_responsive, make_columns_responsive
from gui.widgets.custom import TableLeftHeaders, YellowButton, GreenButton


class MeasureBPC(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.title = "Live Sensor Readings (cm)"
        self.initialize_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)
        self.bind("<<LeaveFrame>>", self.on_leave_frame)

        # Queue where live feed thread writes data
        self.queue = queue.LifoQueue()

    def add_to_queue(self, data):
        self.queue.put(data)

    def initialize_widgets(self):
        # Watchers
        # Update captured count
        self.count_str = StringVar()
        self.count_number = IntVar()
        self.count_number.trace("w", self.update_count_label)

        # Loading message
        self.status_var = StringVar()
        self.status_message = Label(self, textvariable=self.status_var, font=self.controller.header_font)
        self.status_message.grid(row=0, column=0, columnspan=2)

        # 12 IR sensors
        sensor_headers = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10", "S11", "S12"]
        self.table = TableLeftHeaders(self, rows=len(sensor_headers), columns=1, header_values=sensor_headers)
        self.table.grid(row=1, column=0, rowspan=4)

        # Sensor Z
        self.z_value = StringVar()
        self.z_label = Label(self, textvariable=self.z_value, font=self.controller.important_font)
        self.z_label.grid(row=1, column=1, sticky=S)

        # captured count
        self.captured_count = Label(self, textvariable=self.count_str, font=self.controller.bold_font)
        self.captured_count.grid(row=2, column=1, sticky=S, pady=10)

        # capture button
        self.capture_button = YellowButton(self, text="CAPTURE", command=self.capture)
        self.capture_button.grid(row=3, column=1, sticky=N)

        # view results button
        self.results_button = GreenButton(self, text="View Results", command=self.view_results,
                                          image=self.controller.arrow_right, compound=RIGHT)
        self.results_button.grid(row=4, column=1, sticky=SE, padx=20, pady=20)

        make_rows_responsive(self)
        make_columns_responsive(self)

    def on_show_frame(self, event=None):
        # TODO get count from function
        self.count_number.set(len(saved_measurement))

        # Controls update callback
        self.do_update = True
        # Flag to only update buttons and message when necessary
        self.showing_message = False

        # start live GUI
        self.update_live_gui()
        # Open port and start reading
        self.run_live_thread()

    def run_live_thread(self):
        self.live_thread = threading.Thread(target=get_live_sensors, name="live_sensors",
                                            args=(self, reading_sensors, main_quit, kill_thread, no_arduino,
                                                  disconnected, port_lock, capture_now))
        self.live_thread.start()

    def update_live_gui(self):
        # No Arduino found alert
        if no_arduino.is_set():
            no_arduino.clear()

            result = messagebox.askretrycancel("Error opening serial port",
                                               "Make sure the Arduino is properly connected, and try again.",
                                               icon="error")
            # Retry
            if result:
                # open new thread
                self.run_live_thread()
            else:
                self.controller.show_frame("ConfigBPC")
                return

        # Arduino disconnected alert
        if disconnected.is_set():
            disconnected.clear()

            result = messagebox.askretrycancel("Error reading from Arduino",
                                               "Make sure the Arduino is properly connected, and try again.",
                                               icon="error")
            # Retry
            if result:
                # open new thread
                self.run_live_thread()
            else:
                self.controller.show_frame("ConfigBPC")
                return

        # Capturing data
        if capture_now.is_set() and not self.showing_message:
            # Show status message
            self.status_var.set("Capturing data...")

            # Disable buttons
            self.capture_button.configure(state=DISABLED, cursor="wait")
            self.results_button.configure(state=DISABLED, cursor="wait")

            # message has been set
            self.showing_message = True

        # Update live feed
        elif reading_sensors.is_set() and not capture_now.is_set():
            try:
                while True:
                    data = self.queue.get_nowait()
                    # print(data)

                    # Update GUI with new sensor data
                    self.table.update_cells(data[0: len(data) - 1])
                    self.z_value.set("Z = " + data[len(data) - 1] + " cm")

                    # only do it once
                    if self.showing_message:
                        # Hide loading message
                        self.status_var.set("Ready!")

                        # Restore buttons
                        self.capture_button.configure(state=NORMAL, cursor="hand2")

                        # only enable view results if there are any
                        if self.count_number.get():
                            self.results_button.configure(state=NORMAL, cursor="hand2")
                        # leave it disabled, but with a different cursor
                        else:
                            self.results_button.configure(state=DISABLED, cursor="arrow")

                        # message has been removed
                        self.showing_message = False

                    self.update_idletasks()
            except queue.Empty:
                pass

        # Sensors are still initializing
        elif not reading_sensors.is_set() and self.do_update and not self.showing_message:
            # Show loading message
            self.status_var.set("One moment please... Initializing sensors.")

            # Disable buttons
            self.capture_button.configure(state=DISABLED, cursor="wait")
            self.results_button.configure(state=DISABLED, cursor="wait")

            # message has been set
            self.showing_message = True

        # Keep updating until we leave this frame
        if self.do_update:
            self.after(100, self.update_live_gui)

    def on_leave_frame(self, event=None):
        # stop live feed and close serial port
        kill_thread.set()
        reading_sensors.clear()
        self.do_update = False

    def capture(self):
        # only one at a time
        if not capture_now.is_set():
            # Let the worker thread handle it
            capture_now.set()

            # update captured count label
            self.count_number.set(self.count_number.get() + 1)

    def update_count_label(self, *args):
        self.count_str.set(str(self.count_number.get()) + " measurements captured")

    def view_results(self):
        self.controller.show_frame("ResultsBPC")

    def reset(self):
        # reset captured count
        self.count_number.set(0)
