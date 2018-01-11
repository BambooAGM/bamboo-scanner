from tkinter import *

from backend.bsc import *
from gui.widgets.custom import YellowButton, GreenButton, ResponsiveImage, EntryWithPlaceholder
from gui.widgets.helpers import make_rows_responsive, make_columns_responsive, reset_both_responsive


class RefObjectBSC(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.title = "Configure Scale"
        self.responsive_image = None
        self.boxes = []
        self.stage1_widgets = []
        self.stage2_widgets = []
        self.initialize_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def initialize_widgets(self):
        # WATCHERS

        # Update state of navigation buttons
        self.current_contour_var = IntVar()
        self.current_contour_var.trace("w", self.update_navigation)

        # Transition between stages
        self.selected_object_var = StringVar()
        self.selected_object_var.trace("w", self.update_stage)

        # Switch between horizontal and vertical bisections
        self.dimension_type = StringVar()
        self.dimension_type.set("horizontal")
        self.dimension_type.trace("w", self.update_image)
        
        # Update confirm button state
        self.real_dimension_var = StringVar()
        self.real_dimension_var.trace("w", self.update_confirm_button)

        # title of ref object image
        self.ref_object_var = StringVar()
        self.ref_object_title = Label(self, textvariable=self.ref_object_var, font=self.controller.header_font)
        self.ref_object_title.grid(row=0, column=0, sticky=W, padx=20, pady=20)

        # STAGE 1

        # Controls to navigate contours
        self.prev_button = GreenButton(self, text="Previous", image=self.controller.arrow_left, compound=LEFT,
                                       command=lambda: self.show_contour(self.current_contour_var.get() - 1))
        self.stage1_widgets.append((self.prev_button,
                                    lambda: self.prev_button.grid(row=0, column=1, sticky=SE, padx=5, pady=20)))

        self.next_button = GreenButton(self, text="Next", image=self.controller.arrow_right, compound=RIGHT,
                                       command=lambda: self.show_contour(self.current_contour_var.get() + 1))
        self.stage1_widgets.append((self.next_button,
                                    lambda: self.next_button.grid(row=0, column=2, sticky=SW, pady=20)))

        # image in row=1, col=0, colspan=3, rowspan varies with stage

        # instructions
        self.instructions_var = StringVar()
        self.instructions = Label(self, textvariable=self.instructions_var, relief=GROOVE, padx=10, pady=10)
        self.instructions.grid(row=1, column=3, padx=40)

        # select reference object
        self.select_button = YellowButton(self, text="Use this object as reference",
                                          command=lambda: self.selected_object_var.set(self.current_contour_var.get()))
        self.stage1_widgets.append((self.select_button,
                                    lambda: self.select_button.grid(row=2, column=3, sticky=N)))

        # STAGE 2

        # Change reference object
        self.change_button = GreenButton(self, text="Change",
                                         command=lambda: self.selected_object_var.set(""))
        self.stage2_widgets.append((self.change_button,
                                    lambda: self.change_button.grid(row=0, column=1, columnspan=2, sticky=SE, pady=20)))

        # select dimension to enter for the reference object
        self.dimension_label = Label(self, text="Select dimension", font=self.controller.header_font, anchor=SW)
        self.stage2_widgets.append((self.dimension_label,
                                    lambda: self.dimension_label.grid(row=2, column=3, sticky=NSEW, padx=40, pady=10)))

        self.dimension_width = Radiobutton(self, text="Width", variable=self.dimension_type, value="horizontal", cursor="hand2", anchor=SW)
        self.dimension_height = Radiobutton(self, text="Height", variable=self.dimension_type, value="vertical", cursor="hand2", anchor=NW)
        self.stage2_widgets.append((self.dimension_width,
                                    lambda: self.dimension_width.grid(row=3, column=3, sticky=NSEW, padx=60)))
        self.stage2_widgets.append((self.dimension_height,
                                    lambda: self.dimension_height.grid(row=4, column=3, sticky=NSEW, padx=60)))

        # user-entered dimension (for pixels-per-metric)
        self.real_dimension_label = Label(self, text="True measure of pink line (in centimeters)", font=self.controller.header_font, anchor=SW)
        self.stage2_widgets.append((self.real_dimension_label,
                                    lambda: self.real_dimension_label.grid(row=5, column=3, padx=40, pady=20, sticky=NSEW)))

        # %d = Type of action (1=insert, 0=delete, -1 for others)
        # %P = value of the entry if the edit is allowed
        # %S = the text string being inserted or deleted, if any
        validate_cmd = (self.register(self.validate_dimension), '%d', '%P', '%S')
        self.real_dimension = EntryWithPlaceholder(self, text_var=self.real_dimension_var, placeholder_text="0.00",
                                                   validate="key", validatecommand=validate_cmd, textvariable=self.real_dimension_var)
        self.stage2_widgets.append((self.real_dimension,
                                    lambda: self.real_dimension.grid(row=6, column=3, padx=60, sticky=NW)))

        # Invalid dimension message
        self.invalid_dimension = Label(self, text="Dimension must be between 1 and 28 centimeters", fg="red", anchor=W)

        # confirm button
        self.confirm_button = YellowButton(self, text="CONFIRM", command=self.confirm)
        self.stage2_widgets.append((self.confirm_button,
                                    lambda: self.confirm_button.grid(row=8, column=3, sticky=SE, padx=20, pady=20)))

        # set dimension entry placeholder
        self.real_dimension.set_placeholder()

        # start in stage 1
        self.selected_object_var.set("")

    def on_show_frame(self, event=None):
        # fetch all reference objects
        self.boxes = render_boxes()

        # Show the last object we were browsing, or the 1st one if this is a fresh session
        try:
            self.show_contour(self.current_contour_var.get())
        # In case something weird happens
        except IndexError:
            print("could not show contour; resetting")
            self.reset()
            self.on_show_frame()

    def show_contour(self, index):
        self.box = self.boxes[index]
        self.current_contour_var.set(index)
        self.update_image()

    def update_image(self, *args):
        image = self.box[self.dimension_type.get()][0]

        if self.responsive_image is not None:
            self.responsive_image.destroy()
        self.responsive_image = ResponsiveImage(self, image)

        # stage 2
        if self.selected_object_var.get():
            self.responsive_image.grid(row=1, column=0, rowspan=8, columnspan=3, sticky=NSEW, pady=20)
        # stage 1
        else:
            self.responsive_image.grid(row=1, column=0, rowspan=2, columnspan=3, sticky=NSEW, pady=20)

    def update_navigation(self, *args):
        current = self.current_contour_var.get()
        # update image title
        self.ref_object_var.set("Object #" + str(current + 1))

        # toggle prev
        if current == 0:
            self.prev_button.configure(state=DISABLED, cursor="arrow")
        else:
            self.prev_button.configure(state=NORMAL, cursor="hand2")

        # toggle next
        if current == len(self.boxes) - 1:
            self.next_button.configure(state=DISABLED, cursor="arrow")
        else:
            self.next_button.configure(state=NORMAL, cursor="hand2")

    def update_stage(self, *args):
        # Object has been selected
        if self.selected_object_var.get():
            # Show stage 2
            self.set_stage2()
        else:
            # Show stage 1
            self.set_stage1()

    def set_stage1(self):
        current = self.current_contour_var.get()
        # Update image title
        self.ref_object_var.set("Object #" + str(current + 1))

        # Update instructions
        self.instructions_var.set("The reference object should be a figure for which its width or height is known.\n"
                                  "This will allow the program to calculate the real dimensions of the bamboo slice.")

        # Hide stage 2
        for (widget, grid_command) in self.stage2_widgets:
            widget.grid_forget()

        # Hide invalid message
        self.invalid_dimension.grid_forget()

        # Show stage 1
        for (widget, grid_command) in self.stage1_widgets:
            grid_command()

        # Update responsive image
        if self.responsive_image is not None:
            self.responsive_image.grid(row=1, column=0, rowspan=2, columnspan=3, sticky=NSEW, pady=20)

        # Update responsive
        reset_both_responsive(self)
        make_columns_responsive(self, ignored=[1, 2])
        make_rows_responsive(self, ignored=[0])

    def set_stage2(self):
        # Update image title
        self.ref_object_var.set("Selected Reference Object")

        # Update instructions
        self.instructions_var.set("Now please tell us how long is the dimension given by the pink line in the image.\n"
                                  "Provide the most decimals for more accurate results!")

        # Hide stage 1
        for (widget, grid_command) in self.stage1_widgets:
            widget.grid_forget()

        # Show stage 2
        for (widget, grid_command) in self.stage2_widgets:
            grid_command()

        # Update responsive image
        if self.responsive_image is not None:
            self.responsive_image.grid(row=1, column=0, rowspan=8, columnspan=3, sticky=NSEW, pady=20)

        # Update responsive
        reset_both_responsive(self)
        make_columns_responsive(self, ignored=[0, 1])
        make_rows_responsive(self, ignored=[0, 2, 3, 4, 5, 6, 7])

    def validate_dimension(self, action, value_if_allowed, text):
        # only when inserting
        if (action == "1"):
            if text in "0123456789.":
                try:
                    # maximum set by size of scanner (8.5 x 11 inches)
                    if float(value_if_allowed) >= 1.0 and float(value_if_allowed) <= 28.0:
                        # remove invalid message
                        self.invalid_dimension.grid_forget()
                        return True
                    else:
                        # Make system bell sound
                        self.bell()
                        # Show invalid message
                        self.invalid_dimension.grid(row=7, column=3, sticky=NSEW, padx=60, pady=20)
                        return False
                except ValueError:
                    self.bell()
                    return False
            else:
                self.bell()
                return False
        else:
            return True

    def update_confirm_button(self, *args):
        dimension = self.real_dimension_var.get()

        try:
            # not empty string and greater than 1
            if dimension and float(dimension) >= 1.0:
                self.confirm_button.configure(state=NORMAL, cursor="hand2")
            else:
                self.confirm_button.configure(state=DISABLED, cursor="arrow")
        except ValueError:
            print("cannot cast dimension value to float")
            self.confirm_button.configure(state=DISABLED, cursor="arrow")

    def confirm(self):
        # pixels per metric = distance in pixels / distance in centimeters
        ppm = self.box[self.dimension_type.get()][1] / float(self.real_dimension.get())
        set_pixels_per_metric(ppm)

        if get_number_circumferences() > 2:
            # More than 2 circumferences; must handpick
            self.controller.show_frame("PickCircumferencesBSC")
        else:
            # Show results
            self.controller.show_frame("ResultsBSC")

    def reset(self):
        # destroy the image container
        if self.responsive_image is not None:
            self.responsive_image.grid_forget()
            self.responsive_image.destroy()
            self.responsive_image = None

        # reset real dimension entry field
        self.real_dimension.set_placeholder()

        # clear selected object; start in stage 1
        self.selected_object_var.set("")

        # clear ref objects
        self.boxes.clear()

        # Start showing 1st contour box
        self.current_contour_var.set(0)
