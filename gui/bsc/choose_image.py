from tkinter import filedialog, messagebox
from tkinter import *
from backend.bsc import *
from gui.widgets.custom import YellowButton, GreenButton
from gui.widgets.grid_helpers import make_rows_responsive, make_columns_responsive
from utils import resize_keep_aspect


class ConfigBSC(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.title = "Select an image of a bamboo slice"
        self.initialize_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def initialize_widgets(self):
        # Watchers

        # Update begin button state
        self.image_path = StringVar()
        self.image_path.trace("w", self.update_begin_button)

        # choose image button
        self.choose_button = GreenButton(self, text="Choose image", command=self.load_image)
        self.choose_button.grid(row=0, column=0, sticky=SE, padx=10, pady=20)

        # selected image path
        self.path_entry = Entry(self, textvariable=self.image_path, state="readonly")
        self.path_entry.grid(row=0, column=1, sticky=S+E+W, pady=20)

        # image to be processed
        self.placeholder_image = ImageTk.PhotoImage(Image.open("assets/placeholder_image.png"))
        self.image_container = Label(self, image=self.placeholder_image)
        self.image_container.grid(row=1, column=0, columnspan=2, sticky=N)

        # begin button
        self.begin_button = YellowButton(self, text="BEGIN", command=self.begin, image=self.controller.arrow_right, compound=RIGHT)
        self.begin_button.grid(row=2, column=2, sticky=E, padx=10, pady=20)

        # make_rows_responsive(self)
        make_columns_responsive(self)

    def load_image(self):
        # open a file chooser dialog and allow the user to select a source image
        temp_path = filedialog.askopenfilename(title="Select an image to process",
                                               filetypes=(("All files", "*.*"),
                                                          ("PNG", "*.png"),
                                                          ("JPEG", "*.jpg")))

        # TODO - check file extension, restrict to image

        # ensure a file path was selected
        if len(temp_path) > 0:
            # update image path & enable begin button
            self.image_path.set(temp_path)

            # create a Tkinter-compatible photo image
            self.image = Image.open(temp_path)
            self.image = resize_keep_aspect(self.image, self.image.width, self.image.height, 600, 600)
            self.tk_image = ImageTk.PhotoImage(self.image)

            # update image container
            self.image_container.configure(image=self.tk_image)

    def update_begin_button(self, *args):
        if self.image_path.get():
            self.begin_button.grid()
            self.path_entry.grid()
        else:
            self.begin_button.grid_remove()
            self.path_entry.grid_remove()

    def begin(self):
        status = process_image(self.image_path.get(), new_h=self.image.height)

        if status == "OK":
            # Go to results page
            self.controller.show_frame("RefObjectBSC")
        else:
            # show error message
            messagebox.showerror("Something's not right", status)
            # disable begin button
            self.image_path.set("")

    def on_show_frame(self, event=None):
        self.update_begin_button()

    def reset(self):
        # update the container before removing the image reference
        self.image_container.configure(image=self.placeholder_image)
        self.image = None
        self.image_path.set("")
