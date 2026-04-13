import tkinter as tk
from tkinter import filedialog, PhotoImage
from PIL import Image, ImageTk

from nodes.components.Component import Component
from nodes.components.cButton import cButton


class Image_Input(Component):
    def __init__(self, parent, canvas, rectangle):
        super().__init__(parent, canvas, rectangle)
        self.image_path = "No image loaded"
        self.busy = False

        # Create button to load an image



        self.widgets.append(self.button)


    def show_file_chooser(self):
        """Display a file chooser dialog and load the selected image."""
        if self.busy:
            return

        self.busy = True
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )

        if file_path:
            self.image_path = file_path
            self.update_image(self.image_path)

        self.busy = False

    def update_image(self, file_path):
        """Updates the image label with the selected image."""
        if file_path:
            try:
                # Load and resize the image
                pil_image = Image.open(file_path)

                self.button.config(text=file_path)  # Update button text with file path
            except Exception as e:
                print(f"Error loading image: {e}")
                self.button.config(text="Error loading image")
