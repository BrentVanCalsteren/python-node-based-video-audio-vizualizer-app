from pickle import GLOBAL
from pydoc import render_doc
from tkinter import messagebox

import tkinter as tk
import cupy as cp

from nodes.Node import Node
import numpy as np
from PIL import Image, ImageTk
from VALUES import v

from nodes.components.cButton import cButton

FRAME_DURATION = 1 / v.FPS
start_time = 0
frame_count = 0


class Render_Node(Node):
    node_list = []
    def __init__(self,window, canvas, rectangle):
        # Initialize components
        self.render_canvas = None
        button1 = cButton(
            self, canvas, rectangle, command=open_render_window,args=None, text="open render window", offset=(10,30), size=(40, 40), times=2
        )
        button2 = cButton(
            self, canvas, rectangle, command=self.update_frame,args=None, text="start render", offset=(80,30), size=(40, 40)
        )
        self.components = [
            button1,
            button2
        ]
        self.rectangle = rectangle

        super().__init__(window, canvas, "Render Node", rectangle, anchor_option="L")
        v.ACTIVE_RENDER_NODE = self



    def render(self):
        image = self.calculate_image_output()
        render_cupy_image(image)

    def update_frame(self):
        if v.RENDER_CANVAS is not None:
            self.render()

    def calculate_image_output(self):
        image = None
        for node in self.node_list:
            image,x_offset, y_offset = node.overlay_images_anchors()
            image, x_offset, y_offset = node.image_operation(image, x_offset, y_offset)
        if image is None:
            return v.GPU_BLACK_IMAGE
        return image

    def image_operation(self, image, x_offset=0, y_offset=0 ):
        return image, x_offset, y_offset

    def calculate_node_list(self):
        self.node_list = []
        self.append_nodes(self)

    def append_nodes(self, node):
        for anchor in node.anchors_left:
            if anchor.link:
                self.append_nodes(anchor.link.anchorRight.node)
        self.node_list.append(node)

def open_render_window():
    height, width = 300, 400
    if v.RENDER_WINDOW is None:
        v.RENDER_WINDOW = tk.Tk()
        v.RENDER_WINDOW.title("Simple Window")
        v.RENDER_WINDOW.geometry("600x400")  # Set window size (width x height)
        # Add a label to the window
        label = tk.Label(v.RENDER_WINDOW, text="This is a simple window.")
        label.pack()
        v.RENDER_CANVAS = tk.Canvas(v.RENDER_WINDOW, width=width, height=height)
        v.RENDER_CANVAS.pack()

        # Run the window + bind closing
        v.RENDER_WINDOW.protocol("WM_DELETE_WINDOW", on_closing)
        v.RENDER_WINDOW.mainloop()






def render_cupy_image(cp_image):
    """
    Renders a CuPy image on the canvas.
    """
    print("Rendering new image")
    if v.RENDER_WINDOW is None:
        print("no canvas")
        return

    # Delete the last rendered image if it exists
    if hasattr(v, 'LAST_RENDERED_IMAGE') and v.LAST_RENDERED_IMAGE:
        v.RENDER_CANVAS.delete(v.LAST_RENDERED_IMAGE)

    # Ensure the CuPy array is in uint8 format
    if cp_image.dtype != cp.uint8:
        cp_image = cp_image.astype(cp.uint8)

    # Convert CuPy array to NumPy for Pillow compatibility
    np_image = cp.asnumpy(cp_image)

    # Convert NumPy array to a Pillow Image
    pillow_image = Image.fromarray(np_image)

    # Convert Pillow Image to Tkinter-compatible format
    v.DISPLAYED_IMAGE = ImageTk.PhotoImage(pillow_image, master=v.RENDER_CANVAS)

    # Display the image on the canvas
    v.LAST_RENDERED_IMAGE = v.RENDER_CANVAS.create_image(0, 0, anchor=tk.NW, image=v.DISPLAYED_IMAGE)




def on_closing():
    if messagebox.askokcancel("Close", "Do you want to close v.RENDER_WINDOW?"):
        v.RENDER_WINDOW.destroy()
        v.RENDER_WINDOW = None
        v.RENDER_CANVAS = None







