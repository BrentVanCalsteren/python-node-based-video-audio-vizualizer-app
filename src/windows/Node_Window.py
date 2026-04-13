import tkinter as tk
from tkinter import Canvas, Menu
from nodes.Audio_Node import Audio_Node
from nodes.Image_Node import Image_Node
from nodes.Render_node import Render_Node
from nodes.Translate_Node import Translate_Node
from nodes.tools.Link import Link
from VALUES import v


class NodeWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Node Window")
        self.size = (800, 600)
        self.canvas = Canvas(self, bg="#2B2B2B", scrollregion=(0, 0, 2000, 2000))
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Timeline frame
        self.timeline_frame = tk.Frame(self, bg="#1E1E1E", height=100)
        self.timeline_frame.pack(side=tk.BOTTOM, fill=tk.X)
        # Add timeline components -> timeline does not work correctly
        self.playing = False
        self.current_time = 0
        self.total_time = 300  #NEEDS TO BE CHANGED
        self.timeline_width = 2000  #
        self.pixels_in_second = 30
        self.add_timeline_components()


        self.menu_bar = Menu(self)
        self.set_up_menubar()

        self.nodes = []
        self.links = []
        self.temp_link = None

        self.bind_buttons_to_canvas()
        v.NODE_WINDOW =  self
        v.NODE_CANVAS = self.canvas


    def set_up_menubar(self):
        file_menu = Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Open Other Window", command=self.open_other_window)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        self.config(menu=self.menu_bar)

    def bind_buttons_to_canvas(self):
        self.canvas.bind("<Button-1>", self.left_click)
        self.canvas.bind("<Button-3>", self.right_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def open_other_window(self):
        print("Open Other Window action triggered")

    def left_click(self, event):
        canvas_x, canvas_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

        anchor, node = self.find_anchor_node(canvas_x, canvas_y)
        self.active_node = node

        if anchor:
            if not self.temp_link and not anchor.link:
                self.temp_link = Link(self, self.canvas, anchor)
                self.links.append(self.temp_link)
        elif node:
            node.mouse_press(event)

    def right_click(self, event):
        canvas_x, canvas_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.show_context_menu(event, canvas_x, canvas_y)

    def on_drag(self, event):
        canvas_x, canvas_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

        if self.temp_link:
            self.temp_link.end_point = [canvas_x, canvas_y]
            self.temp_link.update_line()
        elif v.DRAG_NODE:
            v.DRAG_NODE.on_drag(event)

    def on_release(self, event):
        if v.DRAG_NODE:
            v.DRAG_NODE.on_release(event)
            return

        canvas_x, canvas_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        anchor, node = self.find_anchor_node(canvas_x, canvas_y)

        if self.temp_link:
            if anchor and self.temp_link.set_anchor(anchor):
                self.update_render_nodes()
                self.temp_link = None
            else:
                self.canvas.delete(self.temp_link.line_id)
                self.links.remove(self.temp_link)
                self.temp_link = None

        elif node:
            node.on_release(event)

    def show_context_menu(self, event, x, y):
        context_menu = Menu(self, tearoff=0)
        context_menu.add_command(label="Image Node", command=lambda: self.add_node(x, y,"im"))
        context_menu.add_command(label="Render Node", command=lambda: self.add_node(x, y,"render"))
        context_menu.add_command(label="Translate Node", command=lambda: self.add_node(x, y, "translate"))
        context_menu.add_command(label="Audio Node", command=lambda: self.add_node(x, y, "audio"))
        context_menu.post(event.x_root, event.y_root)

    def add_node(self, x, y, type):
        rectangle = [x, y, 150, 80]  # Default size of the node
        node = None
        if type == "im":
            node = Image_Node(self, self.canvas, rectangle)
        elif type == "render":
            node = Render_Node(self, self.canvas, rectangle)
        elif type == "translate":
            node = Translate_Node(self, self.canvas, rectangle)
        elif type == "audio":
            node = Audio_Node(self, self.canvas, rectangle)

        if node is not None:
            self.nodes.append(node)

    def find_anchor_node(self, x, y):
        for node in self.nodes:
            bbox_node = self.canvas.bbox(node.rect_id)
            for anchor in node.anchors_left + node.anchors_right:
                bbox_anchor = self.canvas.bbox(anchor.circle)
                if bbox_anchor and bbox_anchor[0] <= x <= bbox_anchor[2] and bbox_anchor[1] <= y <= bbox_anchor[3]:
                    return anchor, node
            if bbox_node and bbox_node[0] <= x <= bbox_node[2] and bbox_node[1] <= y <= bbox_node[3]:
                return None, node
        return None, None

    def update_render_nodes(self):
        for node in self.nodes:
            if type(node) is Render_Node:
                node.calculate_node_list()

        # Add timeline components

    def add_timeline_components(self):
        # Play/Pause button
        self.play_button = tk.Button(self.timeline_frame, text="Play", command=self.toggle_playback)
        self.play_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Canvas for timeline
        self.timeline_canvas = Canvas(self.timeline_frame, bg="#1E1E1E", height=50, width=self.size[0])
        self.timeline_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


        # Draw timeline
        self.timeline_bar = self.timeline_canvas.create_rectangle(
            0, 20, self.timeline_width, 30, fill="gray"
        )

        self.generate_lines()

        # Current position indicator
        self.current_position = self.timeline_canvas.create_line(
            0, 0, 0, 50, fill="red", width=2
        )

        self.timeline_canvas.bind("<Button-1>", self.select_time)


    def generate_lines(self, position=0):
        time = 0
        while position < self.timeline_width:
            self.timeline_canvas.create_line(
                position, 0, position, 20, fill="black", width=2
            )
            self.timeline_canvas.create_text(position+5,10,text=str(time),fill="white")
            time += 1
            position += self.pixels_in_second



    def toggle_playback(self):
        self.playing = not self.playing
        self.play_button.config(text="Pause" if self.playing else "Play")
        if self.playing:
            self.update_timeline()
            if v.ACTIVE_AUDIO_NODE:
                v.ACTIVE_AUDIO_NODE.play_audio()
        else:
            if v.ACTIVE_AUDIO_NODE:
                v.ACTIVE_AUDIO_NODE.pause_audio()


    def update_timeline(self):
        if self.playing:
            self.current_time += (1 / v.FPS)  # Increment time (for simplicity, this assumes 1 second per call)
            x = int(self.current_time * self.pixels_in_second)
            self.timeline_canvas.coords(self.current_position, x, 0, x, 50)
            v.CURRENT_FRAME+=1
            if v.ACTIVE_RENDER_NODE:
                    v.ACTIVE_RENDER_NODE.update_frame()
            self.after(int(1000/v.FPS), self.update_timeline)  # Update every second (adjust for frame rate)

    def select_time(self, event):
        x = self.timeline_canvas.canvasx(event.x)
        self.current_time = x / self.pixels_in_second
        v.CURRENT_FRAME = self.current_time * v.FPS
        self.timeline_canvas.coords(self.current_position, x, 0, x, 50)
        if v.ACTIVE_AUDIO_NODE:
            v.ACTIVE_AUDIO_NODE.pause_audio()
            if self.playing:
                v.ACTIVE_AUDIO_NODE.play_audio()



