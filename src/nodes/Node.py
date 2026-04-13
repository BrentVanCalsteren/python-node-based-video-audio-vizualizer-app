import tkinter as tk
from tkinter import Menu

import cv2
import numpy as np
from VALUES import v

from nodes.tools.Anchor import Anchor
from nodes.tools.IMAGE_FUNCTIONS import overlay_images_GPU

preview_width = 400
preview_height = 300

class Node:
    """Node class for creating interactive nodes on the canvas."""
    components = []
    image = None
    x_offset = 0
    y_offset = 0
    level = 0
    def __init__(self,window, canvas, title, rectangle, anchor_option="LR"):
        self.window = window
        self.canvas = canvas
        self.title = title
        self.rectangle = rectangle
        self.anchors_left = []
        self.anchors_right = []
        self.drag_start_pos = [0, 0]

        # Draw the node rectangle
        self.rect_id = self.canvas.create_rectangle(
            self.rectangle[0], self.rectangle[1],
            self.rectangle[0] + self.rectangle[2], self.rectangle[1] + self.rectangle[3],
            fill="lightgray"
        )
        for component in self.components:
            component.redraw()

        # Add a title label
        self.label_id = self.canvas.create_text(
            self.rectangle[0] + 10, self.rectangle[1] + 15,
            text=self.title, anchor="w"
        )

        self.generate_anchors(anchor_option)

        # Bind mouse events
        self.canvas.tag_bind(self.rect_id, "<ButtonPress-1>", self.mouse_press)
        self.canvas.tag_bind(self.rect_id, "<Button-3>", self.right_click_show_options)
        self.canvas.tag_bind(self.label_id, "<Button-3>", self.right_click_show_options)
        self.canvas.tag_bind(self.label_id, "<ButtonPress-1>", self.mouse_press)
        self.canvas.tag_bind(self.rect_id, "<Enter>", self.on_mouse_enter)
        self.canvas.tag_bind(self.rect_id, "<Leave>", self.on_mouse_leave)
        self.canvas.tag_bind(self.rect_id, "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind(self.rect_id, "<ButtonRelease-1>", self.on_release)

        self.bind_components()

    def bind_components(self):
        for component in self.components:
            self.canvas.tag_bind(component.get_shape(), "<ButtonPress-1>", component.mouse_press)
            self.canvas.tag_bind(component.get_shape(), "<Enter>", component.on_mouse_enter)
            self.canvas.tag_bind(component.get_shape(), "<Leave>", component.on_mouse_leave)
            self.canvas.tag_bind(component.get_shape(), "<ButtonRelease-1>", component.on_release)

    def generate_anchors(self, option):
        if option == "L":
            self.add_anchor_left()
        elif option == "R":
            self.add_anchor_right()
        elif option == "LR":
            self.add_anchor_left()
            self.add_anchor_right()

    def add_anchor(self, side):
        """
        Adds an anchor to the specified side ('Left' or 'Right') and updates positions of existing anchors.
        """
        if side == "Left":
            anchors = self.anchors_left
            x_offset = -5
        elif side == "Right":
            anchors = self.anchors_right
            x_offset = self.rectangle[2] - 5
        else:
            raise ValueError("Invalid side. Must be 'Left' or 'Right'.")

        num = len(anchors) + 1
        for i in range(num):
            y_offset = self.rectangle[1] + (i + 1) * self.rectangle[3] / (num + 1) - 5
            new_pos = (self.rectangle[0] + x_offset, y_offset)

            if i < len(anchors):
                # Update position of existing anchor
                anchors[i].update_position(new_pos)
            else:
                # Create and add a new anchor
                new_anchor = Anchor(self.window, self.canvas, self, side, new_pos)
                anchors.append(new_anchor)

    def add_anchor_left(self):
        self.add_anchor("Left")

    def add_anchor_right(self):
        self.add_anchor("Right")

    def remove_anchor(self, anchor_remove):
        if anchor_remove.anchor_type == "Left" and anchor_remove in self.anchors_left:
            self.anchors_left.remove(anchor_remove)
            self.update_anchor_positions(self.anchors_left, side="Left")
        elif anchor_remove.anchor_type == "Right" and anchor_remove in self.anchors_right:
            self.anchors_right.remove(anchor_remove)
            self.update_anchor_positions(self.anchors_right, side="Right")

    def update_anchor_positions(self, anchors, side):
        num = len(anchors)
        for i, anchor in enumerate(anchors):
            # Calculate evenly spaced positions along the vertical side of the rectangle
            x_offset = -5 if side == "Left" else self.rectangle[2] - 5
            y_offset = self.rectangle[1] + (i + 1) * self.rectangle[3] / (num + 1) - 5
            new_pos = (self.rectangle[0] + x_offset, y_offset)
            anchor.update_position(new_pos)

    def mouse_press(self, event):
        """Handle mouse press events for dragging."""
        self.drag_start_pos = [event.x - self.rectangle[0], event.y - self.rectangle[1]]
        for component in self.components:
            bbox = component.get_bbox()
            if bbox and bbox[0] <= self.canvas.canvasx(event.x) <= bbox[2] and bbox[1] <= self.canvas.canvasy(event.y) <= bbox[3]:
                return
        v.DRAG_NODE = self

    def on_drag(self, event):
        """Handle mouse drag events."""
        new_x = event.x - self.drag_start_pos[0]
        new_y = event.y - self.drag_start_pos[1]
        dx = new_x - self.rectangle[0]
        dy = new_y - self.rectangle[1]
        self.rectangle[0] = new_x
        self.rectangle[1] = new_y

        # Move the rectangle and label
        self.canvas.move(self.rect_id, dx, dy)
        self.canvas.move(self.label_id, dx, dy)

        # Update anchor positions
        for anchor in self.anchors_left + self.anchors_right:
            anchor.update_position((anchor.pos[0] + dx, anchor.pos[1] + dy))

        for component in self.components:
            component.update_position(dx, dy)

    def on_release(self, event):
        v.ACTIVE_NODE = self
        v.DRAG_NODE = None
        pass

    def on_mouse_enter(self, event):
        pass


    def on_mouse_leave(self, event):
        pass


    def right_click_show_options(self, event):
        menu = Menu(self.window, tearoff=0)
        menu.add_command(label="Remove Node", command=lambda: self.remove_self())
        menu.add_command(label="other options", command=lambda: None)
        menu.post(event.x_root, event.y_root)

    def remove_self(self):
        # Remove node's rectangle and label
        self.canvas.delete(self.label_id)
        self.canvas.delete(self.rect_id)

        # Remove the node from the window's node list
        if self in self.window.nodes:
            self.window.nodes.remove(self)

        # Remove all components of the node
        for component in self.components:
            component.remove_self()

        # Remove all anchors and their links
        all_anchors = self.anchors_left + self.anchors_right
        for anchor in all_anchors:
            if anchor.link:
                anchor.link.remove_self()  # Remove associated link
            anchor.remove_self()  # Remove anchor itself

        # Clear the anchor lists
        self.anchors_left.clear()
        self.anchors_right.clear()
        self.window.update_render_nodes()

    def image_operation(self,image, x_offset=0, y_offset=0):
        return image, x_offset, y_offset

    def overlay_images_anchors(self):
        image2 = v.GPU_BLACK_IMAGE
        x_offset1 = 0
        y_offset1 = 0
        x_offset2 = 0
        y_offset2 = 0
        for anchor1 in reversed(self.anchors_left):
            if anchor1.link:
                node1 = anchor1.link.anchorRight.node
                image1 = node1.image
                x_offset1 = node1.x_offset
                y_offset1 = node1.y_offset
                if image1 is not None:
                    image2, x_offset2, y_offset2 = overlay_images_GPU(image1, image2, (x_offset1-x_offset2),(y_offset1-y_offset2))

        if self.image is not None:
            image2, x_offset2, y_offset2 = overlay_images_GPU (self.image, image2, (self.x_offset-x_offset2),(self.y_offset-y_offset2))
        return image2, x_offset2, y_offset2








