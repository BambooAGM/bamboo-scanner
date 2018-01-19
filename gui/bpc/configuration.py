from tkinter import *

from backend.bpc import set_sampleDescription, set_calibration_settings
from gui.widgets.custom import ScrollableTextArea, YellowButton, EntryWithPlaceholder
from gui.widgets.helpers import make_columns_responsive, make_rows_responsive


class ConfigBPC(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.title = "Configuration"
        self.initialize_widgets()

    def initialize_widgets(self):
        # CALIBRATION

        # Ring diameter entry value
        self.ring_diameter_var = StringVar()
        self.ring_diameter_var.trace("w", self.update_begin_button)

        # Calibration object value
        self.calibration_object_var = StringVar()
        self.calibration_object_var.trace("w", self.update_begin_button)

        # Distance to end of rail value
        self.distance_z_var = StringVar()
        self.distance_z_var.trace("w", self.update_begin_button)

        # %d = Type of action (1=insert, 0=delete, -1 for others)
        # %P = value of the entry if the edit is allowed
        # %S = the text string being inserted or deleted, if any
        # %W = the name of the widget
        validate_cmd = (self.register(self.validate_calibration_settings), '%d', '%P', '%S', '%W')

        # Calibration settings group
        self.calibration_settings = LabelFrame(self, text="Calibration Settings (all measures in centimeters)",
                                               fg="grey", padx=20, pady=20, font=self.controller.header_font)
        self.calibration_settings.grid(row=0, column=0, sticky=NSEW, padx=20, pady=20)

        # Ring diameter
        self.ring_diameter_label = Label(self.calibration_settings, text="Ring structure diameter", anchor=SW,
                                         font=self.controller.bold_font)
        self.ring_diameter_label.grid(row=0, column=0, sticky=SW, padx=20)

        # ring diameter range
        self.range_ring_diameter = Label(self.calibration_settings, text="[Valid range: 10 - 30]", fg="grey", anchor=SW,
                                         font=self.controller.small_font)
        self.range_ring_diameter.grid(row=1, column=0, sticky=NW, padx=20)

        self.ring_diameter_entry = EntryWithPlaceholder(self.calibration_settings, text_var=self.ring_diameter_var,
                                                        placeholder_text="0.00", validatecommand=validate_cmd,
                                                        validate="key", textvariable=self.ring_diameter_var,
                                                        name="ring")
        self.ring_diameter_entry.grid(row=2, column=0, sticky=NW, padx=20, pady=20)

        # Calibration object
        self.calibration_object_label = Label(self.calibration_settings, text="Calibration object diameter",
                                              font=self.controller.bold_font, anchor=SW)
        self.calibration_object_label.grid(row=0, column=1, sticky=SW, padx=20)

        # calibration object diameter range
        self.range_calibration_obj_diameter = Label(self.calibration_settings, text="[Valid range: 2 - 26]", fg="grey",
                                                    anchor=NW, font=self.controller.small_font)
        self.range_calibration_obj_diameter.grid(row=1, column=1, sticky=NW, padx=20)

        self.calibration_object_entry = EntryWithPlaceholder(self.calibration_settings, text_var=self.calibration_object_var,
                                                             placeholder_text="0.00", validatecommand=validate_cmd,
                                                             textvariable=self.calibration_object_var, validate="key",
                                                             name="calibration_obj")
        self.calibration_object_entry.grid(row=2, column=1, sticky=NW, padx=20, pady=20)

        # Distance to flat surface at end of rail
        self.distance_z_label = Label(self.calibration_settings, text="Distance to the end of the rail", anchor=SW,
                                      font = self.controller.bold_font)
        self.distance_z_label.grid(row=3, column=0, sticky=SW, padx=20)

        # z distance range
        self.range_z_distance = Label(self.calibration_settings, text="[Valid range: 15.24 - 645]", fg="grey", anchor=NW,
                                      font=self.controller.small_font)
        self.range_z_distance.grid(row=4, column=0, sticky=NW, padx=20)

        self.distance_z_entry = EntryWithPlaceholder(self.calibration_settings, text_var=self.distance_z_var,
                                                     placeholder_text="0.00", validate="key", name="z_distance",
                                                     validatecommand=validate_cmd, textvariable=self.distance_z_var)
        self.distance_z_entry.grid(row=5, column=0, sticky=NW, padx=20, pady=20)

        # calibration object diameter greater than ring diameter
        self.calibration_obj_greater_ring = Label(self.calibration_settings,
                                                  text="The calibration object's diameter\ncan't be greater than the ring diameter",
                                                  fg="red", anchor=NW)

        # make calibration section responsive
        make_columns_responsive(self.calibration_settings)
        make_rows_responsive(self.calibration_settings)

        # description label
        self.description_label = Label(self, text="Information about the bamboo sample (optional)",
                                       font=self.controller.bold_font)
        self.description_label.grid(row=1, column=0, sticky=SW, padx=20, pady=20)

        # Description text area
        self.text_area = ScrollableTextArea(self)
        self.text_area.grid(row=2, column=0, sticky=NW, padx=20)

        # begin button
        self.begin_button = YellowButton(self, text="BEGIN", command=self.begin,
                                         image=self.controller.arrow_right, compound=RIGHT)
        self.begin_button.grid(row=3, column=0, sticky=SE, padx=20, pady=20)

        # set placeholders
        self.ring_diameter_entry.set_placeholder()
        self.calibration_object_entry.set_placeholder()
        self.distance_z_entry.set_placeholder()

        make_rows_responsive(self)
        make_columns_responsive(self)

        # min size of buttons row
        self.grid_rowconfigure(3, minsize=80)


    def validate_calibration_settings(self, action, value_if_allowed, text, widget):
        # only when inserting
        if action == "1":
            if text in "0123456789.":
                try:
                    # name of the widget
                    widget_name = str(widget).split(".")[-1]

                    # ring
                    if widget_name == "ring":
                        # valid range [10,30]
                        if float(value_if_allowed) >= 1.0 and float(value_if_allowed) <= 30.0:
                            return True
                        else:
                            # Make system bell sound
                            self.bell()
                            return False

                    # calibration object    
                    elif widget_name == "calibration_obj":
                        # valid range [2,26]
                        if float(value_if_allowed) >= 1.0 and float(value_if_allowed) <= 26.0:
                            return True
                        else:
                            # Make system bell sound
                            self.bell()
                            return False

                    # z distance entry
                    else:
                        # valid range [15.24, 645]
                        if float(value_if_allowed) >= 1.0 and float(value_if_allowed) <= 645.0:
                            return True
                        else:
                            # Make system bell sound
                            self.bell()
                            return False

                except ValueError:
                    self.bell()
                    return False
            else:
                self.bell()
                return False
        else:
            return True

    def update_begin_button(self, *args):
        ring_diameter = self.ring_diameter_var.get()
        calibration_obj = self.calibration_object_var.get()
        distance_z = self.distance_z_var.get()

        # valid range [10,30]
        ring_diameter_ok = ring_diameter and float(ring_diameter) >= 10.0
        # valid range [2,26]
        calibration_object_ok = calibration_obj and float(calibration_obj) >= 2.0
        # valid range [15.24, 645]
        distance_z_ok = distance_z and float(distance_z) >= 15.24

        # show invalid message when calibration object diameter is greater than ring
        if ring_diameter_ok and calibration_object_ok and (float(ring_diameter) - float(calibration_obj)) > 0:
            self.calibration_obj_greater_ring.grid_forget()
        elif ring_diameter_ok and calibration_object_ok and (float(ring_diameter) - float(calibration_obj)) <= 0:
            self.calibration_obj_greater_ring.grid(row=3, column=1, sticky=NW, padx=20)

        # All entries valid
        if ring_diameter_ok and calibration_object_ok and distance_z_ok and \
                (float(ring_diameter) - float(calibration_obj)) > 0:
            # enable begin button
            self.begin_button.configure(state=NORMAL, cursor="hand2")

        # at least one entry is not valid
        else:
            # disable begin button
            self.begin_button.configure(state=DISABLED, cursor="arrow")

    def begin(self):
        # save sample description
        set_sampleDescription(self.text_area.text.get(1.0, END))

        # save calibration settings
        ring_diameter = float(self.ring_diameter_var.get())
        calibration_obj = float(self.calibration_object_var.get())
        distance_z = float(self.distance_z_var.get())
        set_calibration_settings(ringDiameter=ring_diameter, obj_diameter=calibration_obj, distance_z=distance_z)

        # Show sensors live feed
        self.controller.show_frame("MeasureBPC")

    def reset(self):
        # reset description
        self.text_area.text.delete(1.0, END)
