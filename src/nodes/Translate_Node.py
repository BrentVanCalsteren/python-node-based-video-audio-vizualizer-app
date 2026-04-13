import cv2
import numpy as np

from nodes.Node import Node
from nodes.components.cButton import cButton



class Translate_Node(Node):
    x_offset = 100
    y_offset = 100
    def __init__(self,window,canvas, rectangle):
        self.busy = False
        self.image_path = "No image loaded"
        # Initialize components
        self.components = [
            cButton(
            self, canvas, rectangle, command=self.increase_x,args=1, text="open file select", size=(50,50))
            #Scale(self),
            #Translate(self),
        ]

        # Call parent initializer
        super().__init__(window,canvas,"Translate", rectangle, anchor_option="LR")

    def increase_x(self, value):
        self.x_offset += value


    def image_operation(self, image, x_offset, y_offset):
        return image, self.x_offset+x_offset , self.y_offset+y_offset