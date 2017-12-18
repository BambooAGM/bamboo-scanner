from tkinter import filedialog, messagebox
from tkinter import *
from backend.bsc import *
from gui.widgets.custom import YellowButton
from gui.widgets.grid_helpers import make_rows_responsive, make_columns_responsive


class ConfigBSC(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.title = "Slice Characterization"
        self.initialize_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def initialize_widgets(self):
        # Watchers

        # Update begin button state
        self.image_path = StringVar()
        self.image_path.trace("w", self.update_begin_button)

        # image to be processed
        self.image_label = StringVar()
        self.image_label.set("Click below to browse for an image")
        self.placeholder_image = ImageTk.PhotoImage(Image.open("assets/placeholder_image.png"))
        self.image_container = Label(self, image=self.placeholder_image, textvariable=self.image_label,
                                     font=self.controller.bold_font, compound=BOTTOM, pady=10, width=400, height=400)
        # bind to click event
        self.image_container.bind("<Button-1>", self.load_image)
        self.image_container.grid(row=0, column=0, columnspan=2)

        # self.path_entry = Entry(self, textvariable=self.image_path, state="readonly")
        # self.path_entry.grid(row=0, column=2, columnspan=2, sticky=EW)

        # begin button
        self.begin_button = YellowButton(self, text="BEGIN", command=self.begin)
        self.begin_button.grid(row=1, column=1, sticky=E, padx=10)

        make_rows_responsive(self)
        make_columns_responsive(self)

    def load_image(self, event):
        # open a file chooser dialog and allow the user to select a source image
        temp_path = filedialog.askopenfilename(title="Select an image",
                                               filetypes=(("PNG", "*.png"),
                                                          ("JPEG", "*.jpg"),
                                                          ("All files", "*.*")))

        # TODO - check file extension, restrict to image

        # ensure a file path was selected
        if len(temp_path) > 0:
            # update image path & enable begin button
            self.image_path.set(temp_path)

            # Creates a Tkinter-compatible photo image, which can be used everywhere Tkinter expects an image object.
            image = ImageTk.PhotoImage(Image.open(temp_path))

            self.image_label.set("Image to be processed")
            # update image container
            self.image_container.configure(image=image)
            # keep a reference
            self.image_container.image = image

    def update_begin_button(self, *args):
        if self.image_path.get():
            self.begin_button.grid()
        else:
            self.begin_button.grid_remove()

    def begin(self):
        status = process_image(self.image_path.get())

        if status == "OK":
            # Go to results page
            self.controller.show_frame("RefObjectBSC")
        else:
            # show error message
            messagebox.showerror("Something's not right", status)
            # disable begin button
            self.image_path.set("")

    def on_show_frame(self, event=None):
        # update page title
        self.controller.update_page_title(self.title)
        # reset state
        self.reset()
        self.update_begin_button()

    def reset(self):
        # update the container before removing the image reference
        self.image_container.configure(image=self.placeholder_image)
        self.image_container.image = None
        self.image_label.set("Click below to browse for an image")
        self.image_path.set("")
        reset_backend()
