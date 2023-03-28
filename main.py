import cv2, time, sys, os

import tkinter as tk
import numpy as np

from PIL import Image, ImageTk
from dotenv import load_dotenv

########################################################################################
# Load environment file
load_dotenv()

# Import environment variables
OPERATION_MODE = os.getenv("OPERATION_MODE")
START_CUT_IMAGE_X = int(os.getenv("START_CUT_IMAGE_X"))
START_CUT_IMAGE_Y = int(os.getenv("START_CUT_IMAGE_Y"))
END_CUT_IMAGE_X = int(os.getenv("END_CUT_IMAGE_X"))
END_CUT_IMAGE_Y = int(os.getenv("END_CUT_IMAGE_Y"))


# Application class
class Application(tk.Frame):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Robotic sorter and packer")
        self.canvas = tk.Canvas(self.root, width=1100, height=600)
        self.canvas.pack()

        self.button1 = tk.Button(self.root, text="Find objects")
        self.button1.place(x=0, y=0)
        self.button1.pack()
        # Bind the button to the find_objects function
        self.button1.bind("<Button-1>", self.find_objects)

        self.button2 = tk.Button(self.root, text="Insert object")
        self.button2.place(x=200, y=100)
        self.button2.pack()
        # Bind the button to the insert_object function
        self.button2.bind("<Button-2>", self.insert_object)

        self.button3 = tk.Button(self.root, text="Pack object")
        self.button3.place(x=300, y=100)
        self.button3.pack()
        # Bind the button to the pack_object function
        self.button3.bind("<Button-3>", self.pack_object)

        self.button4 = tk.Button(self.root, text="STOP")
        self.button4.place(x=400, y=100)
        self.button4.pack()
        # Bind the button to the stop function
        self.button4.bind("<Button-4>", self.stop)

        # Open the webcam
        self.cap = cv2.VideoCapture(0)

        # Check if the webcam is opened correctly
        if not self.cap.isOpened():
            print(time.strftime("[ %H:%M:%S", time.localtime()) + "." + str(int(time.time() * 1000) % 1000).zfill(3) + " ]  " + "Cannot open webcam")
            sys.exit(1)

        self.mainloop()

    def __del__(self):
        # Release the camera and close the window
        self.cap.release()
        self.root.destroy()

    ########################################################################################
    # Start the mainloop
    def mainloop(self):
        while True:
            _, frame = self.cap.read()
            frame = cv2.flip(frame, 1)
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.canvas.create_image(450, 30, image=imgtk, anchor=tk.NW)
            self.root.update()   

    ########################################################################################
    # Button functions
    def find_objects(self, event):
        print(time.strftime("[ %H:%M:%S", time.localtime()) + "." + str(int(time.time() * 1000) % 1000).zfill(3) + " ]  " + "Finding objects")

        ret, frame = self.cap.read()
        
        if ret == True:
            # Convert to grayscale, default size 640x480
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Cut off edeges of the image
            gray = gray[START_CUT_IMAGE_Y:END_CUT_IMAGE_Y, START_CUT_IMAGE_X:END_CUT_IMAGE_X]
            
            # Addaptive thresholding
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            
            cv2.imshow("Thresholded", thresh)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    def insert_object(self, event):
        print(time.strftime("[ %H:%M:%S", time.localtime()) + "." + str(int(time.time() * 1000) % 1000).zfill(3) + " ]  " + "Inserting object")




    def pack_object(self, event):
        print(time.strftime("[ %H:%M:%S", time.localtime()) + "." + str(int(time.time() * 1000) % 1000).zfill(3) + " ]  " + "Packing object")




    def stop(self, event):
        print(time.strftime("[ %H:%M:%S", time.localtime()) + "." + str(int(time.time() * 1000) % 1000).zfill(3) + " ]  " + "Stopping")
    

if __name__ == "__main__":

    if OPERATION_MODE == 'dev':
        pass
    elif OPERATION_MODE == 'prod':
        pass
    else:
        print(time.strftime("[ %H:%M:%S", time.localtime()) + "." + str(int(time.time() * 1000) % 1000).zfill(3) + " ]  " + "Error: Couldn't get OPERATION mode from environment file, please set it")


    # Create the application
    app = Application()
    
