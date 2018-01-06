import threading
from tkinter import font, messagebox
from tkinter import *
from PIL import ImageTk, Image
from backend.bpc import reset_bpc_backend
from backend.bsc import reset_bsc_backend
from gui.home import Home
from gui.bsc.choose_image import ConfigBSC
from gui.bsc.choose_ref_object import RefObjectBSC
from gui.bsc.pick_circumferences import PickCircumferencesBSC
from gui.bsc.results import ResultsBSC
from gui.bpc.configuration import ConfigBPC
from gui.bpc.measure import MeasureBPC
from gui.bpc.results import ResultsBPC
from gui.widgets.grid_helpers import make_rows_responsive, make_columns_responsive
from utils import resize_keep_aspect


class BambooScanner(Tk):

    def __init__(self):
        Tk.__init__(self)

        # global program closing event (for threads)
        self.main_quit = threading.Event()

        # Global fonts
        self.global_font_family = font.Font(family="Segoe UI Emoji")
        self.common_font = font.Font(family="Segoe UI Emoji", size=14)
        self.bold_font = font.Font(family="Segoe UI Emoji", size=13, weight="bold")
        self.header_font = font.Font(family="Segoe UI Emoji", size=16, weight="bold")
        self.title_font = font.Font(family="Segoe UI Emoji", size=28, weight="bold")
        self.important_font = font.Font(family="Segoe UI Emoji", size=28, weight="bold", underline=True)

        # update widget fonts
        self.option_add("*Font", self.global_font_family)
        self.option_add("*Button.Font", self.bold_font)
        self.option_add("*Label.Font", self.common_font)

        # Main page layout: hosts page content and global widgets
        self.container = Frame(self)
        # Container fills the entire window
        self.container.pack(side=TOP, fill=BOTH, expand=True)

        # Navigation bar
        self.navbar = Frame(self.container, bg="#35AD35")
        self.navbar.grid(row=0, columnspan=2, sticky=NSEW)

        # Home button
        home_image = Image.open("assets/home.png")
        # resize home button image
        home_image = resize_keep_aspect(home_image, w=home_image.width, h=home_image.height, max_w=100, max_h=60)
        home_image = ImageTk.PhotoImage(home_image)
        self.home = Label(self.navbar, image=home_image, cursor="hand2")
        self.home.image = home_image
        # bind to click event
        self.home.bind("<Button-1>", self.go_home)
        self.home.grid(row=0, column=0, sticky=NSEW)

        # Page title
        self.title_var = StringVar()
        self.page_title = Label(self.navbar, textvariable=self.title_var,
                                bg="#35AD35", fg="#FFFFFF", font=self.title_font)
        self.page_title.grid(row=0, column=1, sticky=W, padx=10)

        # Step indicator
        self.step = StringVar()
        self.page_step = Label(self.navbar, textvariable=self.step,
                               bg="#35AD35", fg="#FFFFFF")
        self.page_step.grid(row=0, column=2, sticky=E, padx=10)

        make_columns_responsive(self.navbar, ignored=[0])

        # Bamboo
        bamboo_image = ImageTk.PhotoImage(Image.open("assets/bamboo.png"))
        self.bamboo = Label(self.container, image=bamboo_image)
        self.bamboo.image = bamboo_image
        self.bamboo.grid(row=1, column=0, sticky=NW)

        # Common images
        self.arrow_left = ImageTk.PhotoImage(Image.open("assets/arrow_left.png"))
        self.arrow_right = ImageTk.PhotoImage(Image.open("assets/arrow_right.png"))
        self.save_icon = ImageTk.PhotoImage(Image.open("assets/save.png"))

        # The class names for both BSC and BPC
        self.bsc_pages = (ConfigBSC, RefObjectBSC, PickCircumferencesBSC, ResultsBSC)
        self.bpc_pages = (ConfigBPC, MeasureBPC, ResultsBPC)

        # Initialize all pages and keep their references accessible
        self.frames = {}
        for F in (() + (Home,) + self.bsc_pages + self.bpc_pages):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame

            # Add all frames to the container, on top of each other
            frame.grid(row=1, column=1, sticky=NSEW)

        # Allow the grid to expand with the window
        make_rows_responsive(self.container, ignored=[0])
        make_columns_responsive(self.container, ignored=[0])

        # Start on the home page
        self.active_frame = None
        self.show_frame("Home")

    def go_home(self, event):
        result = messagebox.askokcancel("Unsaved progress will be lost", "If you leave now, all progress will be lost.",
                                        default="cancel", icon="warning")

        if result:
            # Reset the tool we were using
            # came from BPC
            if type(self.active_frame) in self.bpc_pages:
                self.reset_BPC()
            # came from BSC
            else:
                self.reset_BSC()

            # go home
            self.show_frame("Home")

    def show_frame(self, page_name):
        """
        Raise a "leave" event on the current frame, a "show" event on the new one, and display it.

        :param page_name: class name of destination frame
        """

        # If there is an active frame, signal its exit
        if self.active_frame is not None:
            self.active_frame.event_generate("<<LeaveFrame>>")

        # Switch to new active frame
        self.active_frame = self.frames[page_name]

        # update page title and step, except for Home page
        if type(self.active_frame) != Home:
            self.update_page_title(self.active_frame.title)
            self.update_page_step()

        self.active_frame.update()
        self.active_frame.event_generate("<<ShowFrame>>")
        self.active_frame.tkraise()

    def get_frame(self, page_name):
        """
        Get the instance of a page

        :return: The frame of the specified page
        """
        return self.frames[page_name]

    def update_page_title(self, title):
        self.title_var.set(title)

    def update_page_step(self):
        # Check if active frame is from BPC
        for i, page in enumerate(self.bpc_pages, start=1):
            # find the active page
            if type(self.active_frame) == page:
                message = "Pole Characterization\n step " + str(i) + " of " + str(len(self.bpc_pages))
                self.step.set(message)
                return

        # Active frame is from BSC
        for i, page in enumerate(self.bsc_pages, start=1):
            # find the active page
            if type(self.active_frame) == page:
                message = "Slice Characterization\n step " + str(i) + " of " + str(len(self.bsc_pages))
                self.step.set(message)
                return

    def hide_navbar(self):
        self.navbar.grid_remove()

    def restore_navbar(self):
        self.navbar.grid()

    def reset_BPC(self):
        """
        Reset all the BPC GUI frames and its backend module
        """
        # reset GUI
        for page in self.bpc_pages:
            name = page.__name__
            self.frames[name].reset()

        # reset backend
        reset_bpc_backend()

    def reset_BSC(self):
        """
        Reset all the BSC GUI frames and its backend module
        """
        # reset GUI
        for page in self.bsc_pages:
            name = page.__name__
            self.frames[name].reset()

        # reset backend
        reset_bsc_backend()


if __name__ == "__main__":
    def exit_handler():
        if messagebox.askokcancel("Quit", "Do you really wish to quit?", default="cancel", icon="warning"):
            # Close port before quitting
            app.main_quit.set()
            # Exit
            app.destroy()

    # start GUI
    app = BambooScanner()
    # window title
    app.title("Bamboo Scanner")
    # Program exit handler
    app.protocol("WM_DELETE_WINDOW", exit_handler)
    app.mainloop()
