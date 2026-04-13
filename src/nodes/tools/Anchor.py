
import tkinter as tk
from tkinter import Canvas

class Anchor:
    """Anchor widget for connecting nodes."""

    def __init__(self,window, canvas, node, anchor_type, pos, **kwargs):
        """Initialize the anchor with its parent node, type, and position."""
        self.canvas = canvas
        self.window = window
        self.node = node
        self.anchor_type = anchor_type  # Type of anchor (e.g., "left", "right")
        self.pos = pos  # Position as (x, y) tuple
        self.size = 10  # Diameter of the anchor
        self.is_selected = False
        self.link = None

        # Draw the anchor (circle)
        self.circle = self.canvas.create_oval(
            self.pos[0], self.pos[1],
            self.pos[0] + self.size, self.pos[1] + self.size,
            fill="red", outline=""
        )

        # Bind mouse events
        self.canvas.tag_bind(self.circle, "<Button-1>", self.on_mouse_press)
        self.canvas.tag_bind(self.circle, "<Enter>", self.on_mouse_enter)
        self.canvas.tag_bind(self.circle, "<Leave>", self.on_mouse_leave)
        self.canvas.tag_bind(self.circle, "<ButtonRelease-1>", self.on_mouse_release)

    def update_position(self, pos):
        """Update the position of the anchor."""
        self.pos = pos
        self.canvas.coords(
            self.circle,
            self.pos[0], self.pos[1],
            self.pos[0] + self.size, self.pos[1] + self.size
        )
        if self.link is not None:
            self.link.anchor_moved(self)

    def add_link(self, link):
        """Add a link to the anchor."""
        if self.link is None:
            self.link = link
            if self.anchor_type == "Left":
                self.node.add_anchor_left()
            elif self.anchor_type == "Right":
                self.node.add_anchor_right()

    def remove_self(self):
        # Ensure the link is removed before deleting the anchor
        if self.link:
            self.link.remove_self()
            self.link = None

        # Remove the anchor circle from the canvas
        self.canvas.delete(self.circle)

        # Remove the anchor from its parent's anchor list
        if self in self.node.anchors_left or self in self.node.anchors_right:
            self.node.remove_anchor(self)

    #################################################
    # Mouse events
    #################################################

    def on_mouse_press(self, event):
        """Handle mouse press event."""
        self.is_selected = True
        self.canvas.itemconfig(self.circle, fill="yellow")  # Change to yellow

    def on_mouse_enter(self, event):
        """Highlight the anchor when the mouse hovers over it."""
        if not self.is_selected:
            self.canvas.itemconfig(self.circle, fill="yellow")

    def on_mouse_leave(self, event):
        """Remove highlight when the mouse leaves the anchor."""
        if not self.is_selected:
            self.canvas.itemconfig(self.circle, fill="red")

    def on_mouse_release(self, event):
        """Revert color when the mouse button is released."""
        self.is_selected = False
        self.canvas.itemconfig(self.circle, fill="red")





