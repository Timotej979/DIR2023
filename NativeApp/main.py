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
        
        # Create canvas
        self.canvas = tk.Canvas(self.root, width=1100, height=540)
        self.canvas.pack()

        ########################################################################################
        # GUI elements

        self.button1 = tk.Button(self.root, text="Find objects")
        self.button1.place(x=0, y=0)
        self.button1.pack()
        # Bind the button to the find_objects function
        self.button1.bind("<Button-1>", self.find_objects)

        self.button2 = tk.Button(self.root, text="Insert object")
        self.button2.place(x=200, y=100)
        self.button2.pack()
        # Bind the button to the insert_object function
        self.button2.bind("<Button-1>", self.insert_object)

        self.button3 = tk.Button(self.root, text="Pack object")
        self.button3.place(x=300, y=100)
        self.button3.pack()
        # Bind the button to the pack_object function
        self.button3.bind("<Button-1>", self.pack_object)

        self.button4 = tk.Button(self.root, text="STOP")
        self.button4.place(x=400, y=100)
        self.button4.pack()
        # Bind the button to the stop function
        self.button4.bind("<Button-1>", self.stop_robot)

        self.button5 = tk.Button(self.root, text="Scan QR")
        self.button5.place(x=500, y=100)
        self.button5.pack()
        # Bind the button to the stop function
        self.button5.bind("<Button-1>", self.scan_qr)

        ########################################################################################
        # Position GUI elements
        # Zero top left corner is about 50 pixels down and 250 pixels right
        self.canvas.create_text(230, 30, text="ROBOTIC SORTER AND PACKER", font=("Arial", 20))
        self.canvas.create_window(80, 70, window=self.button1)
        self.canvas.create_window(80, 110, window=self.button2)
        self.canvas.create_window(80, 150, window=self.button3)
        self.canvas.create_window(80, 190, window=self.button4)
        self.canvas.create_window(80, 230, window=self.button5)

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
        sys.exit(0)

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

            # Cut off edeges of the image
            frame = frame[START_CUT_IMAGE_Y:END_CUT_IMAGE_Y, START_CUT_IMAGE_X:END_CUT_IMAGE_X]

            edges = cv2.Canny(frame, 100, 200)

            # Find contours 
            contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 

            sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)

            # Draw all contours
            cv2.drawContours(frame, [sorted_contours[0], sorted_contours[1]], -1, (0, 255, 0), 3)

            cv2.imshow("Frame", frame)
            cv2.imshow("Edges", edges)
            cv2.waitKey(0)


            

    def insert_object(self, event):
        print(time.strftime("[ %H:%M:%S", time.localtime()) + "." + str(int(time.time() * 1000) % 1000).zfill(3) + " ]  " + "Inserting object")




    def pack_object(self, event):
        print(time.strftime("[ %H:%M:%S", time.localtime()) + "." + str(int(time.time() * 1000) % 1000).zfill(3) + " ]  " + "Packing object")




    def stop_robot(self, event):
        print(time.strftime("[ %H:%M:%S", time.localtime()) + "." + str(int(time.time() * 1000) % 1000).zfill(3) + " ]  " + "Stopping")

    def scan_qr(self, event):
        detect = cv2.QRCodeDetector()
        _, frame = self.cap.read()
        try:
            value, points, straight_qrcode = detect.detectAndDecode(frame)
            print(value)
        except:
            print("Scan failed")

    

if __name__ == "__main__":

    if OPERATION_MODE == 'dev':
        pass
    elif OPERATION_MODE == 'prod':
        pass
    else:
        print(time.strftime("[ %H:%M:%S", time.localtime()) + "." + str(int(time.time() * 1000) % 1000).zfill(3) + " ]  " + "Error: Couldn't get OPERATION mode from environment file, please set it")


    # Create the application
    app = Application()
    
