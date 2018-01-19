import copy
from datetime import datetime
from tkinter import *
from tkinter import filedialog, messagebox

from backend.bpc import generate_text_file, saved_measurement, delete_measurement, sort_ByZeta
from gui.widgets.custom import HorizontalTable, YellowButton, RedButton, AutoScrollbar
from gui.widgets.helpers import make_columns_responsive, make_rows_responsive


class ResultsBPC(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.title="Review saved measurements"
        self.captured_data = []
        # TODO Generate headers ?
        self.sensor_headers = ["Z (cm)", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10", "S11", "S12"]
        self.initialize_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)
        self.bind("<<LeaveFrame>>", self.on_leave_frame)

    def initialize_widgets(self):
        # a canvas with scrollbars; the results table goes in it
        h_scrollbar = AutoScrollbar(self, orient=HORIZONTAL)
        h_scrollbar.grid(row=1, column=0, columnspan=2, sticky=EW)
        v_scrollbar = AutoScrollbar(self)
        v_scrollbar.grid(row=0, column=2, sticky=NS)

        self.canvas = Canvas(self, xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        h_scrollbar.config(command=self.canvas.xview)
        v_scrollbar.config(command=self.canvas.yview)

        # Empty message
        self.empty_message = Label(self, text="Nothing to see here. Go capture some measurements!",
                                   font=self.controller.header_font)

        # Save button
        self.save_button = YellowButton(self, text="Save coordinates", command=self.save, image=self.controller.save_icon,
                                        compound=LEFT)
        self.save_button.grid(row=2, column=0, sticky=S, pady=20)

        # Discard button
        self.discard_button = RedButton(self, text="DISCARD", command=self.discard)
        self.discard_button.grid(row=2, column=1, sticky=S, pady=20)

        # responsive except the scrollbars and the buttons
        make_rows_responsive(self, ignored=[1, 2])
        make_columns_responsive(self, ignored=[2])

    def on_show_frame(self, event=None):
        # restore canvas in grid
        self.canvas.grid(row=0, column=0, sticky=NSEW, columnspan=2, pady=20)

        # Enable save button
        self.save_button.configure(state=NORMAL, cursor="hand2")

        # sort captured measurements by Z value
        sort_ByZeta(saved_measurement)

        # Generate captured measurements table
        self.create_table()

    def create_table(self):
        # Create table if there are any captured measurements
        if saved_measurement:
            # Make a copy of the captured measurements
            self.captured_data = copy.deepcopy(saved_measurement)

            # Place Z as first element
            for column in self.captured_data:
                column.insert(0, column.pop())

            # the results table
            self.table = HorizontalTable(self.canvas, rows=len(self.captured_data[0]), columns=len(self.captured_data),
                                         header_values=self.sensor_headers, can_select_columns=True,
                                         button_command=self.delete_z)
            # Set background of top row
            for column in range(len(self.captured_data)):
                self.table.cells[0][column].configure(bg="#5E5E5E", fg="#FFFFFF", font=self.controller.bold_font)
            self.table.headers[0].configure(bg="#5E5E5E", fg="#FFFFFF")

            # load cells with captured measurements
            self.table.update_cells(self.captured_data)

            # place the table inside the canvas
            self.canvas.create_window(0, 0, anchor=NW, window=self.table)

            # wait for the canvas to create table
            self.table.update_idletasks()

            # update scroll region of table
            self.canvas.config(scrollregion=self.canvas.bbox("all"))

        # No captured measurements
        else:
            # Hide canvas
            self.canvas.grid_forget()

            # Show an empty message
            self.empty_message.grid(row=0, columnspan=2)

            # disable save button
            self.save_button.configure(state=DISABLED, cursor="arrow")

    def destroy_table(self):
        # Remove table from canvas
        self.canvas.delete("all")
        # Destroy the table
        self.table.destroy()

    def delete_z(self):
        # get indices to be deleted
        deleted_columns = self.table.get_checked_indices()

        # delete them
        delete_measurement(deleted_columns)

        # Re-create table
        self.destroy_table()
        self.create_table()

    def on_leave_frame(self, event=None):
        # Destroy table if there are any captured measurements
        if saved_measurement:
            self.destroy_table()

        # Otherwise hide empty message
        else:
            self.empty_message.grid_forget()

    def save(self):
        date = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        save_path = filedialog.asksaveasfilename(title="Save as", defaultextension=".txt", initialfile="BPC_" + date)

        # make sure the user didn't cancel the dialog
        if len(save_path) > 0:
            if generate_text_file(save_path):
                # all good
                messagebox.showinfo("Success!", "File was generated successfully.")
                # reset BPC
                self.controller.reset_BPC()
                # go to home screen
                self.controller.show_frame("Home")
            else:
                messagebox.showerror("Error generating text file", "Make sure you have access to the selected destination.")

    def discard(self):
        result = messagebox.askokcancel("Discard captured measurements?",
                                        "You will lose all the measurements you have captured so far.",
                                        default="cancel", icon="warning")
        if result:
            # reset BPC
            self.controller.reset_BPC()
            # go to home screen
            self.controller.show_frame("Home")

    def reset(self):
        self.captured_data.clear()
