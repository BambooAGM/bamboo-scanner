from datetime import datetime
from tkinter import *
from tkinter import filedialog, messagebox

import matplotlib

matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib import style
style.use("ggplot")

from backend.bsc import *
from gui.widgets.custom import RedButton, YellowButton, ResponsiveImage
from gui.widgets.helpers import make_columns_responsive, make_rows_responsive


class ResultsBSC(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.title = "Slice Results"
        self.responsive_image = None
        self.initialize_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def initialize_widgets(self):

        # Result image row=0, col=0, columnspan=2

        # Save button
        self.save_button = YellowButton(self, text="Save coordinates", command=self.save, image=self.controller.save_icon,
                                        compound=LEFT)
        self.save_button.grid(row=2, column=0, sticky=E, padx=10, pady=20)

        # Discard button
        self.discard_button = RedButton(self, text="DISCARD", command=self.discard)
        self.discard_button.grid(row=2, column=1, sticky=W, padx=10, pady=20)

        # min size of buttons row
        self.grid_rowconfigure(2, minsize=80)

        make_rows_responsive(self, ignored=[0])
        make_columns_responsive(self)

    def on_show_frame(self, event=None):
        # generate polar coordinates and avg diameter of circumferences
        data_circumferences = circumferences_to_polar_and_avg_diameter()

        # create plot
        figure = Figure(figsize=(5,5), dpi=100)
        ax = figure.add_subplot(111, projection="polar")

        # plot both circumferences
        for (r, theta, _) in data_circumferences:
            ax.plot(theta, r)

        # Create a Tk canvas of the plot
        self.polar_plot = FigureCanvasTkAgg(figure, self)
        self.polar_plot.show()
        self.polar_plot.get_tk_widget().grid(row=1, column=1, sticky=NSEW, padx=20)

        # Show some controls for the figure
        self.toolbar_container = Frame(self)
        self.plot_toolbar = NavigationToolbar(self.polar_plot, self.toolbar_container)
        self.plot_toolbar.update()
        self.toolbar_container.grid(row=0, column=1, sticky=NSEW, padx=20, pady=20)

        # original image with both circumferences outlined
        self.image = get_slice_roi()
        self.responsive_image = ResponsiveImage(self, self.image)
        self.responsive_image.grid(row=1, column=0, sticky=NSEW, padx=20, pady=20)

    def save(self):
        date = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        save_path = filedialog.asksaveasfilename(title="Save as", defaultextension=".txt", initialfile="BSC_" + date)

        # make sure the user didn't cancel the dialog
        if len(save_path) > 0:
            if generate_text_file(save_path):
                # all good
                messagebox.showinfo("Success!", "File was generated successfully.")
                # reset BSC
                self.controller.reset_BSC()
                # go to home screen
                self.controller.show_frame("Home")
            else:
                messagebox.showerror("Error generating text file", "Make sure you have access to the selected destination.")

    def discard(self):
        result = messagebox.askokcancel("Discard results?", "All progress will be lost.", default="cancel", icon="warning")
        if result:
            # reset BSC
            self.controller.reset_BSC()
            # go to home screen
            self.controller.show_frame("Home")

    def reset(self):
        # destroy the image container
        if self.responsive_image is not None:
            self.responsive_image.destroy()
            self.responsive_image = None
            self.image = None

        # destroy the plot
        self.polar_plot = None


class NavigationToolbar(NavigationToolbar2TkAgg):
    # Remove the zoom-to-rectangle button; not for polar plots
    toolitems = [t for t in NavigationToolbar2TkAgg.toolitems if t[0] != "Zoom"]
