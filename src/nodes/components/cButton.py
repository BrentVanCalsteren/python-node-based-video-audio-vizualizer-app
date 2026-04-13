class cButton():
    command = None

    def __init__(self, node, canvas, rectangle,command,args, text="",offset = (15, 40), size=(110,25), times=1):
        self.offset = offset
        self.size = size
        self.args = args
        self.times = times
        self.pos = ( rectangle[0] + self.offset[0],rectangle[1] + self.offset[1])
        self.canvas = canvas
        self.node = node
        self.rectangle = self.canvas.create_rectangle(self.pos[0],self.pos[1],
                                                      self.pos[0]+ self.size[0], self.pos[1]+ self.size[1])
        self.canvas.itemconfig(self.rectangle, fill="#404345")
        self.command = command
        #self.canvas.tag_bind(self.rectangle, "<ButtonRelease-1>", self.on_mouse_release)

    def redraw(self):
        self.canvas.delete(self.rectangle)
        self.rectangle = self.canvas.create_rectangle(self.pos[0], self.pos[1],
                                                      self.pos[0] + self.size[0],self.pos[1] + self.size[1])
    def get_bbox(self):
        return self.canvas.bbox(self.rectangle)

    def get_shape(self):
        return self.rectangle

    def remove_self(self):
        self.node.components.remove(self)
        self.canvas.delete(self.rectangle)

    def mouse_press(self, event):
        if self.args:
            self.command(self.args)
        else:
            self.command()

    def on_mouse_enter(self, event):
        self.canvas.itemconfig(self.rectangle, fill="#6d88a1")

    def on_mouse_leave(self, event):
        self.canvas.itemconfig(self.rectangle, fill="#404345")

    def on_release(self, event):
        pass

    def update_position(self, dx, dy):
        """Update the position of the anchor."""
        self.pos = (self.pos[0]+ dx, self.pos[1] + dy)
        self.canvas.move(self.rectangle, dx, dy)

    def check_in_bounding_box(self, event):
        bbox = self.canvas.bbox(self.rectangle)
        if bbox and bbox[0] <= event.x <= bbox[2] and bbox[1] <=event.y <= bbox[3]:
            return True
        return False