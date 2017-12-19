from datetime import datetime
from tkinter import filedialog, messagebox
from tkinter import *
from gui.widgets.grid_helpers import make_columns_responsive, make_rows_responsive
from gui.widgets.custom import TableLeftHeaders, GreenButton, YellowButton, RedButton


class ResultsBPC(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.title="Review Your Measurements"
        # TODO Generate headers ?
        self.sensor_headers = ["Z (cm)", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10", "S11", "S12"]
        self.initialize_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)
        self.bind("<<LeaveFrame>>", self.on_leave_frame)

    def initialize_widgets(self):
        # Go back button
        self.back_button = GreenButton(self, text="I'm not done yet", command=self.go_back,
                                       image=self.controller.arrow_left, compound=LEFT)
        self.back_button.grid(row=1, column=0, sticky=W)

        # Save button
        self.save_button = YellowButton(self, text="SAVE", command=self.save, image=self.controller.save_icon,
                                        compound=LEFT)
        self.save_button.grid(row=1, column=1, sticky=E, padx=5)

        # Discard button
        self.discard_button = RedButton(self, text="DISCARD", command=self.discard)
        self.discard_button.grid(row=1, column=2, sticky=W, padx=5)

        make_rows_responsive(self)
        make_columns_responsive(self)

    def on_show_frame(self, event=None):
        # TODO fetch from backend
        self.captured_data = [
            ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
            ["2.5", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
            ["5", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        ]

        # Captured measurements table with delete column support
        self.create_table()

    def create_table(self):
        self.table = TableLeftHeaders(self, rows=len(self.captured_data[0]), columns=len(self.captured_data),
                                      header_values=self.sensor_headers, can_select_columns=True, button_command=self.delete_z)
        # Set background of top row
        for column in range(len(self.captured_data)):
            self.table.cells[0][column].configure(bg="#5E5E5E", fg="#FFFFFF", font=self.controller.bold_font)
        self.table.headers[0].configure(bg="#5E5E5E", fg="#FFFFFF")
        self.table.grid(row=0, columnspan=3)

        # load cells with captured measurements
        self.table.update_cells(self.captured_data)

    def destroy_table(self):
        # Remove checkboxes and table from grid, and destroy them
        self.table.grid_forget()
        self.table.destroy()

    def delete_z(self):
        deleted_columns = self.table.get_checked_indices()
        # self.captured_data = bpc.delete(deleted_columns)
        print(deleted_columns)
        # Re-create table
        self.destroy_table()
        self.create_table()

    def on_leave_frame(self, event=None):
        # Destroy captured measurements table
        self.destroy_table()

    def go_back(self):
        self.controller.show_frame("MeasureBPC")

    def save(self):
        date = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        save_path = filedialog.asksaveasfilename(title="Save as", defaultextension=".txt", initialfile="BPC_" + date)

        # make sure the user didn't cancel the dialog
        if len(save_path) > 0:
            # reset BPC
            self.controller.reset_BPC()
            # Go to BPC configuration page
            self.controller.show_frame("ConfigBPC")

            # uncomment when integrated
            # if generate_text_file(save_path):
            #     # all good
            #     messagebox.showinfo("Success!", "File was generated successfully.")
            #     # reset BPC
            #     self.controller.reset_BPC()
            #     # Go to BPC configuration page
            #     self.controller.show_frame("ConfigBPC")
            # else:
            #     messagebox.showerror("Error generating text file", "Make sure you have access to the selected destination.")

    def discard(self):
        result = messagebox.askokcancel("Discard captured measurements?", "You will lose all the measurements you have captured so far.",
                             default="cancel", icon="warning")
        if result:
            # reset BPC
            self.controller.reset_BPC()
            # Go to BPC configuration page
            self.controller.show_frame("ConfigBPC")

    def reset(self):
        # must provide this method because master Tk widget calls reset on all the frames.
        pass
