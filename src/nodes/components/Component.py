
class Component:
    widgets = []
    id = 0
    def __init__(self,parent, canvas, rectangle, offset = (5,15)):
        self.parent = parent
        self.offset = offset
        self.canvas = canvas
        self.pos = [rectangle[0], rectangle[1]]


