from tkinter import *
from backend.bsc import *
from gui.widgets.custom import YellowButton, GreenButton, RedButton, ResponsiveImage
from gui.widgets.grid_helpers import make_rows_responsive, make_columns_responsive


class PickCircumferencesBSC(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.title = "Select Circumferences"
        self.selected_circumferences = []
        self.responsive_image = None
        self.initialize_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def initialize_widgets(self):

        # Watchers

        # Update state of navigation buttons
        self.current_circumference_var = IntVar()
        self.current_circumference_var.trace("w", self.update_navigation)

        # Update buttons
        self.selected_count_text = StringVar()
        # Update count label
        self.selected_count_var = IntVar()
        self.selected_count_var.trace("w", self.update_count_text)
        self.selected_count_var.set(0)
        # set here to avoid trigerring update buttons during init
        self.selected_count_text.trace("w", self.update_buttons)

        # title of circumference image
        self.circumference_title_var = StringVar()
        self.circumference_title = Label(self, textvariable=self.circumference_title_var, font=self.controller.header_font)
        self.circumference_title.grid(row=0, column=0, columnspan=2, pady=20)

        # Image
        # self.image_container = Label(self)
        # self.image_container.grid(row=1, column=0, rowspan=3, columnspan=2)

        # instructions
        instructions_text = "More than 2 circumferences were found.\n"
        instructions_text += "Choose the most appropriate ones."
        self.instructions = Label(self, text=instructions_text, relief=GROOVE)
        self.instructions.grid(row=1, column=2, columnspan=2)

        # Controls to navigate contours
        self.prev_button = GreenButton(self, text="Previous contour", image=self.controller.arrow_left, compound=LEFT,
                                       command=lambda: self.show_circumference(self.current_circumference_var.get() - 1))
        self.prev_button.grid(row=4, column=0, sticky=E, padx=5, pady=20)

        self.next_button = GreenButton(self, text="Next contour", image=self.controller.arrow_right, compound=RIGHT,
                                       command=lambda: self.show_circumference(self.current_circumference_var.get() + 1))
        self.next_button.grid(row=4, column=1, sticky=W, padx=5, pady=20)

        # remove button
        self.remove_button = RedButton(self, text="Deselect circumference", command=self.deselect)
        self.remove_button.grid(row=2, column=2, columnspan=2)

        # select button
        self.select_button = YellowButton(self, text="Use this circumference", command=self.select)
        self.select_button.grid(row=2, column=2, columnspan=2)

        # Selection count
        self.selected_count = Label(self, textvariable=self.selected_count_text, font=self.controller.important_font)
        self.selected_count.grid(row=3, column=2, columnspan=2, sticky=N)

        # confirm button
        self.confirm_button = YellowButton(self, text="CONFIRM", command=self.confirm)
        self.confirm_button.grid(row=5, column=3, sticky=E, padx=10)

        # make_rows_responsive(self)
        make_columns_responsive(self)

    def on_show_frame(self, event=None):
        self.images = render_all_circumferences()
        # generate selected flags
        self.selected_circumferences = [False] * len(self.images)
        self.show_circumference(0)
        self.update_confirm_button()

    def show_circumference(self, index):
        self.current_circumference_var.set(index)
        image = self.images[index]
        # update image container
        # self.image_container.configure(image=image)
        if self.responsive_image is not None:
            self.responsive_image.destroy()
        self.responsive_image = ResponsiveImage(self, image)
        self.responsive_image.grid(row=1, column=0, rowspan=3, columnspan=2)

    def update_navigation(self, *args):
        current = self.current_circumference_var.get()
        self.circumference_title_var.set("Circumference #" + str(current + 1))

        # toggle prev
        if current == 0:
            self.prev_button.configure(state=DISABLED)
        else:
            self.prev_button.configure(state=NORMAL)

        # toggle next
        if current == len(self.images) - 1:
            self.next_button.configure(state=DISABLED)
        else:
            self.next_button.configure(state=NORMAL)

        # Toggle select and remove buttons
        self.update_select_remove_buttons()

    def update_buttons(self, *args):
        self.update_select_remove_buttons()
        self.update_confirm_button()

    def update_select_remove_buttons(self):
        # only if array has been initialized
        if len(self.selected_circumferences):

            # selected
            if self.selected_circumferences[self.current_circumference_var.get()]:
                # this one is selected; show remove button
                self.select_button.grid_remove()
                self.remove_button.grid()

            # not selected
            else:
                # show select button
                self.remove_button.grid_remove()
                self.select_button.grid()

                # 2 already selected; disable select button
                if self.selected_count_var.get() == 2:
                    self.select_button.configure(state=DISABLED)
                else:
                    # still can select; re-enable button
                    self.select_button.configure(state=NORMAL)

    def update_confirm_button(self):
        # Toggle confirm button
        if self.selected_count_var.get() == 2:
            self.confirm_button.grid()
        else:
            self.confirm_button.grid_remove()

    def update_count_text(self, *args):
        # update label text
        self.selected_count_text.set(str(self.selected_count_var.get()) + " of 2 selected")

    def deselect(self):
        # deselect
        self.selected_circumferences[self.current_circumference_var.get()] = False

        # Decrease count
        self.selected_count_var.set(self.selected_count_var.get() - 1)

    def select(self):
        # mark as selected
        self.selected_circumferences[self.current_circumference_var.get()] = True

        # Increase count
        self.selected_count_var.set(self.selected_count_var.get() + 1)

    def confirm(self):
        selected = []

        for index, selected_flag in enumerate(self.selected_circumferences):
            if selected_flag:
                selected.append(index)

        # Apply in backend
        set_final_circumferences(selected)

        # Show results
        self.controller.show_frame("ResultsBSC")

    def reset(self):
        self.selected_count_var.set(0)
        self.selected_circumferences.clear()

        # destroy the image container
        if self.responsive_image is not None:
            self.responsive_image.destroy()
            self.responsive_image = None
