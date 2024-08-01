import os
import cv2
import json
import numpy as np
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class App:
    def __init__(self, root):
        self.initial_dir = 'dev' # Replace with your initial directory path
        self.output_dir = 'output'
        self.root = root
        self.root.title("Image and Text Input with Matplotlib")

        # Create a label to display the text input value
        self.text_label = tk.Label(root, text="Text will be displayed here", font=("Helvetica", 16))
        self.text_label.pack(pady=20)

        # Create a frame for the image
        self.image_frame = tk.Frame(root)
        self.image_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # Create a frame for the text input and buttons
        self.bottom_frame = tk.Frame(root)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # Create a StringVar to track the text entry
        self.text_var = tk.StringVar()
        self.text_var.trace_add("write", self.update_label)

        # Create a text entry widget
        self.text_entry = tk.Entry(self.bottom_frame, textvariable=self.text_var, width=50)
        self.text_entry.pack(side=tk.LEFT, padx=(0, 10))

        self.save_button = tk.Button(self.bottom_frame, text="Save", command=self.save_annotation)
        self.save_button.pack(side=tk.LEFT)
                
        # Create a button to select an image
        self.select_button = tk.Button(self.bottom_frame, text="Select Folder", command=self.select_folder)
        self.select_button.pack(side=tk.LEFT)
        
        self.update_button = tk.Button(self.bottom_frame, text="Next Image", command=self.next_image)
        self.update_button.pack(side=tk.LEFT)

        # Create a button to write out the json
        self.write_button = tk.Button(self.bottom_frame, text="Write JSON", command=self.write_json)
        self.write_button.pack(side=tk.LEFT)

        # Placeholder for matplotlib figure 
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.image_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # data stuffs
        self.selection_coords = {}
        self.annotations = []
        self.image_annotations = []
        
        self.current_label = ""
        
        self.image_files = []
        self.current_index = 0
        self.image_folder = self.initial_dir
        
        self.load_images()

    def load_images(self): 
        if self.image_folder:
            self.image_files = os.listdir(self.image_folder)
            # print(self.image_files)
            self.show_image(self.image_files[self.current_index])        
     
    def select_folder(self):
        self.image_folder = filedialog.askdirectory(initialdir=self.initial_dir)
        self.load_images()
 
    def save_annotation(self):
        label_dict = { "coordinates":{}, "label": '' }
        coord_dict = {"x":int, "y":int, "width":int, "height":int}
        x1, y1, x2, y2 = self.selection_coords['x1'], self.selection_coords['y1'], self.selection_coords['x2'], self.selection_coords['y2']
        cx = round((x1 + x2) / 2, 2)
        cy = round((y1 + y2) / 2, 2)
        width = round(abs(x2 - x1), 2)
        height = round(abs(y2 - y1), 2)
        coord_dict['x'] = cx
        coord_dict['y'] = cy
        coord_dict['width'] = width
        coord_dict['height'] = height
        label_dict['label'] = self.current_label
        label_dict['coordinates'] = coord_dict
        self.annotations.append(label_dict)        
        #image_dict = self.image_annotations[self.current_index]
        #image_dict['annotations'] = self.annotations

    def is_image_file(self, filename):
        # Check file extension
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
        return any(filename.lower().endswith(ext) for ext in image_extensions)

    def update_label(self, *args):
        self.current_label = self.text_var.get()
        #print(f"Label updated to: {self.current_label}")  # Debug statement
        self.text_label.config(text=f"Input: {self.current_label}")

    def show_image(self, file_name):
        if self.is_image_file(file_name):
            dir_file = self.image_folder + '/' + file_name
            if 0 <= self.current_index < len(self.image_annotations): 
                self.annotations = self.image_annotations[self.current_index]["annotations"]
            else: 
                image_dict = {"image":'', "annotations":[]}
                image_dict['image'] = file_name 
                self.image_annotations.append(image_dict)
            
            self.fig.clear()
            self.ax = self.fig.add_subplot(111)
            image = cv2.imread(dir_file)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            self.ax.imshow(image)
            self.ax.axis('off')
            
            self.rectangle_selector = RectangleSelector(
                self.ax, 
                self.on_select,
                #drawtype='box',
                useblit=True,
                button=[1],
                minspanx=5,
                minspany=5,
                spancoords='pixels',
                interactive=True
            )
            
            self.canvas.draw()
        
    def on_select(self, eclick, erelease):
        # Callback function for RectangleSelector
        print(f"Selected region: ({eclick.xdata}, {eclick.ydata}) to ({erelease.xdata}, {erelease.ydata})")
        self.selection_coords = {
            'x1': eclick.xdata,
            'y1': eclick.ydata,
            'x2': erelease.xdata,
            'y2': erelease.ydata
        }
    
    def next_image(self):
        if self.image_files:
            self.image_annotations
            
            self.current_index = (self.current_index + 1) % len(self.image_files)
            self.show_image(self.image_files[self.current_index])
        
    def write_json(self):
        json_file = json.dumps(self.image_annotations)
        with open(self.output_dir + '/' + 'annotations.json', 'w') as f:
            f.write(json_file)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()