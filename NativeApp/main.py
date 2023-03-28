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

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Increase the saturation and value of the image
            hsv[:, :, 1] = (hsv[:, :, 1] * 1.5)
            hsv[:, :, 2] = (hsv[:, :, 2] * 1.5)

            bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

            # Convert to grayscale, default size 640x480
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

            # Cut off edeges of the image
            frame = frame[START_CUT_IMAGE_Y:END_CUT_IMAGE_Y, START_CUT_IMAGE_X:END_CUT_IMAGE_X]
            gray = gray[START_CUT_IMAGE_Y:END_CUT_IMAGE_Y, START_CUT_IMAGE_X:END_CUT_IMAGE_X]

            # Apply median filter
            median_gray = cv2.medianBlur(gray,3)
 
            # Apply Gaussian filter
            gaussian_gray = cv2.GaussianBlur(median_gray,(5,5),0)

            # Addaptive thresholding
            thresh = cv2.adaptiveThreshold(gaussian_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

            # Find contours
            contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # sort contours by area
            sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)

            # remove the longest contour from the list
            packaging_contour = sorted_contours[1]
            counter_contour = sorted_contours[3]

            x1,y1,w1,h1 = cv2.boundingRect(packaging_contour)
            cv2.rectangle(frame, (x1,y1), (x1+w1, y1+h1), (0,255,0), 2)

            x2,y2,w2,h2 = cv2.boundingRect(counter_contour)
            cv2.rectangle(frame, (x2,y2), (x2+w2, y2+h2), (0,255,0), 2)

            # rotate the rectangle to match it best
            M1 = cv2.getRotationMatrix2D((x1+w1/2,y1+h1/2),90,1)
            dst1 = cv2.warpAffine(frame,M1,(frame.shape[1],frame.shape[0]))



            # Show the image
            cv2.imshow('Image', frame)
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
    
