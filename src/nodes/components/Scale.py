from nodes.components.Component import Component


class Scale(Component):
    x_value = 1
    y_value = 1


    def __init__(self, node):
        self.node = node

        super().__init__("Scale")