import numpy as np
import cupy as cp
from nodes.Node import Node
from nodes.tools.IMAGE_FUNCTIONS import add_alpha_GPU
from nodes.components.cButton import cButton
from tkinter import filedialog, PhotoImage
from PIL import Image, ImageTk



class Image_Node(Node):
    def __init__(self,window,canvas, rectangle):
        self.busy = False
        self.image_path = "No image loaded"
        # Initialize components
        self.components = [
            cButton(
            self, canvas, rectangle, command=self.show_file_chooser,args=None, text="open file select")
            #Scale(self),
            #Translate(self),
        ]

        # Call parent initializer
        super().__init__(window,canvas,"Image Input", rectangle, anchor_option="LR")

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

    import cupy as cp
    from PIL import Image

    def update_image(self, file_path):
        """Updates the image label with the selected image using CuPy."""
        if file_path:
            try:
                # Load the image using Pillow
                pil_image = Image.open(file_path)

                # Convert the image to a NumPy array
                np_image = np.array(pil_image)

                # Transfer the image to the GPU (CuPy array)
                self.image = cp.asarray(np_image)

                # Add alpha channel if necessary
                self.image = add_alpha_GPU(self.image)

            except Exception as e:
                e

