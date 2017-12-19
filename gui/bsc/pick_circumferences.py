from tkinter import *
from backend.bsc import *
from gui.widgets.custom import YellowButton, GreenButton, RedButton
from gui.widgets.grid_helpers import make_rows_responsive, make_columns_responsive


class PickCircumferencesBSC(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.title = "Select Circumferences"
        self.selected_circumferences = []
        self.initialize_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def initialize_widgets(self):
        # Watchers
        # Update state of navigation buttons
        self.current_circumference_var = IntVar()
        self.current_circumference_var.trace("w", self.update_navigation)

        # Update buttons
        self.selected_count_var = StringVar()
        self.selected_count_var.set(str(len(self.selected_circumferences)) + " of 2 selected")
        self.selected_count_var.trace("w", self.update_buttons)

        # title of ref object image
        self.circumference_title_var = StringVar()
        self.circumference_title = Label(self, textvariable=self.circumference_title_var, font=self.controller.bold_font)
        self.circumference_title.grid(row=0, column=0)

        # Controls to navigate circumferences
        self.prev_button = GreenButton(self, text="Previous",
                                       command=lambda: self.show_circumference(self.current_circumference_var.get() - 1))
        self.prev_button.grid(row=0, column=1, sticky=E)

        self.next_button = GreenButton(self, text="Next",
                                       command=lambda: self.show_circumference(self.current_circumference_var.get() + 1))
        self.next_button.grid(row=0, column=2, sticky=W)

        # Image
        self.image_container = Label(self, width=400, height=400)
        self.image_container.grid(row=1, column=0, columnspan=3)

        # Selection count
        self.selected_count = Label(self, textvariable=self.selected_count_var)
        self.selected_count.grid(row=1, column=2)

        # remove button
        self.remove_button = RedButton(self, text="Remove", command=self.remove)
        self.remove_button.grid(row=2, column=0, columnspan=2)

        # select button
        self.select_button = GreenButton(self, text="Select", command=self.select)
        self.select_button.grid(row=2, column=0, columnspan=2)

        # confirm button
        self.confirm_button = YellowButton(self, text="CONFIRM", command=self.confirm)
        self.confirm_button.grid(row=2, column=3, sticky=E, padx=10)

        make_rows_responsive(self)
        make_columns_responsive(self)

    def on_show_frame(self, event=None):
        self.images = render_all_circumferences()
        self.show_circumference(0)
        self.update_confirm_button()

    def show_circumference(self, index):
        self.current_circumference_var.set(index)
        image = self.images[index]
        # update image container
        self.image_container.configure(image=image)

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
        if self.current_circumference_var.get() in self.selected_circumferences:
            # this one is selected; show remove button
            self.select_button.grid_remove()
            self.remove_button.grid()
        else:
            # not selected; show select button
            self.remove_button.grid_remove()
            self.select_button.grid()

    def update_confirm_button(self):
        # Toggle confirm button
        if len(self.selected_circumferences) == 2:
            self.confirm_button.grid()
        else:
            self.confirm_button.grid_remove()

    def remove(self):
        # delete last element
        del self.selected_circumferences[self.current_circumference_var.get()]
        self.selected_count_var.set(str(len(self.selected_circumferences)) + " of 2 selected")

    def select(self):
        # add to selected
        self.selected_circumferences.append(self.current_circumference_var.get())
        self.selected_count_var.set(str(len(self.selected_circumferences)) + " of 2 selected")

    def confirm(self):
        set_final_circumferences(self.selected_circumferences)
        # Show results
        self.controller.show_frame("ResultsBSC")

    def reset(self):
        pass
