import tkinter as tk
from tkinter import Canvas

class Link:
    """A custom class to represent a line."""

    def __init__(self,window, canvas, anchor):
        self.canvas = canvas
        self.window = window
        self.start_point = [anchor.pos[0] + 5, anchor.pos[1] + 5]
        self.end_point = [anchor.pos[0] + 5, anchor.pos[1] + 5]
        self.anchorLeft = None
        self.anchorRight = None

        # Create the line on the canvas
        self.line_id = self.canvas.create_line(self.start_point[0], self.start_point[1],
                                               self.end_point[0], self.end_point[1],
                                               fill="yellow", width=2)
        self.set_anchor(anchor)

    def update_line(self):
        """Update the line's points on the canvas."""
        self.canvas.coords(self.line_id, self.start_point[0], self.start_point[1],
                           self.end_point[0], self.end_point[1])

    def set_anchor(self, anchor):
        """Set the anchor points for the line."""
        return_bool = False
        if anchor.anchor_type == "Left":
            if self.anchorLeft is None and anchor.link is None and (self.anchorRight is None or anchor.node != self.anchorRight.node):
                self.anchorLeft = anchor
                self.start_point = [anchor.pos[0] + 5, anchor.pos[1] + 5]  # Adjust to anchor center
                return_bool = True
            else:
                return_bool = False
        elif anchor.anchor_type == "Right":
            if self.anchorRight is None and anchor.link is None and (self.anchorLeft is None or anchor.node != self.anchorLeft.node):
                self.anchorRight = anchor
                self.end_point = [anchor.pos[0] + 5, anchor.pos[1] + 5]  # Adjust to anchor center
                return_bool = True
            else:
                return_bool = False
        if self.has_anchors():
            self.anchorLeft.add_link(self)
            self.anchorRight.add_link(self)
            self.canvas.itemconfig(self.line_id, fill="red")  # Change color to red when fully anchored
        self.update_line()
        return return_bool

    def has_anchors(self):
        """Check if both anchors are set."""
        return self.anchorLeft and self.anchorRight

    def anchor_moved(self, anchor):
        """Update line points when an anchor moves."""
        if anchor.anchor_type == "Left":
            self.start_point = [anchor.pos[0] + 5, anchor.pos[1] + 5]
        elif anchor.anchor_type == "Right":
            self.end_point = [anchor.pos[0] + 5, anchor.pos[1] + 5]
        self.update_line()
    
    def remove_anchor(self, anchor):
        if anchor.anchor_type == "Left" and anchor == self.anchorLeft:
            self.anchorLeft = None
        elif anchor.anchor_type == "Right" and anchor == self.anchorRight:
            self.anchorRight = None

    def remove_self(self):
        # Remove the link from the window's link list
        if self in self.window.links:
            self.window.links.remove(self)

        # Ensure associated anchors know the link is removed
        if self.anchorLeft:
            self.anchorLeft.link = None
        if self.anchorRight:
            self.anchorRight.link = None

        # Remove the link line from the canvas
        self.canvas.delete(self.line_id)

        # Clear references to anchors
        self.anchorLeft.remove_self()
        self.anchorLeft = None
        self.anchorRight.remove_self()
        self.anchorRight = None


"""
from kivy.graphics import Line, Color
from kivy.uix.widget import Widget
from kivy.properties import ListProperty, NumericProperty


class Link(Widget):

    start_point = ListProperty([0, 0])
    end_point = ListProperty([0, 0])
    anchorLeft = None
    anchorRight = None

    def __init__(self, anchor, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self.color = Color(1, 1, 0, 1)  # Yellow color
            self.line = Line(points=self.start_point + self.end_point, width=2)

        self.set_anchor(anchor)

        self.bind(start_point=self.update_line, end_point=self.update_line)


    def update_line(self, *args):
        self.line.points = self.start_point + self.end_point

    def set_anchor(self, anchor):
        return_bool = False
        if anchor.anchor_type == "Left":
            if self.anchorLeft is None and anchor.link is None and (self.anchorRight is None or anchor.node != self.anchorRight.node):
                self.anchorLeft = anchor
                self.start_point = [anchor.center_x, anchor.center_y]
                return_bool = True
            else: return_bool =  False
        elif anchor.anchor_type == "Right":
            if self.anchorRight is None and anchor.link is None and (self.anchorLeft is None or anchor.node != self.anchorLeft.node):
                self.anchorRight = anchor
                self.end_point = [anchor.center_x, anchor.center_y]
                return_bool = True
            else: return_bool = False
        if self.has_anchers():
            self.anchorLeft.add_link(self)
            self.anchorRight.add_link(self)
            self.color.rgb = (1, 0, 0)
        return return_bool

    def has_anchers(self):
        return self.anchorLeft and self.anchorRight

    def anchor_moved(self, anchor):
        if anchor.anchor_type == "Left":
            self.start_point = [anchor.center_x, anchor.center_y]
        elif anchor.anchor_type == "Right":
            self.end_point = [anchor.center_x, anchor.center_y]
            
"""

