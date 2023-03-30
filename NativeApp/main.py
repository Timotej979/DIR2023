import cv2, time, sys, os, csv

import numpy as np
import pandas as pd
import time
import lib.robot as robotComm


import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import numpy as np

from pyzbar.pyzbar import decode
from PIL import Image, ImageTk
from dotenv import load_dotenv


########################################################################################
# Point cloud

ZAPOREDJE_TOCK_SKATLJA = [
    'Skatlja_prehodna',
    'Skatlja_pobiranje_zgoraj',
    'Skatlja_pobiranje',
    'suction_on',
    'Skatlja_pobiranje_zgoraj_po',
    'Skatlja_prehodna',
    'Skatlja_odpiranje_zacetek',
    'Skatlja_odpiranje_spodaj',
    'Skatlja_odpiranje_posevno',
    'Skatlja_odpiranje_posevno_popravek',
    'Skatlja_odpiranje_konec',
    'Skatlja_vstavljanje_zacetek',
    'suction_off',
    'Skatlja_vstavljanje_spust',
    'Stevec_potisk_pred',
    'Stevec_v_skatlji_potisk_pred_rotiran',
    'Skatlja_potisk_koncna',
    'Skatlja_prehod_po',
]


ZAPOREDJE_TOCK_STEVEC = [
    'Stevec_prehodna',
    'Pobiranje_stevca_zgoraj',
    'Pobiranje_stevca',
    'suction_on',
    'Pobiranje_stevca_zgoraj',
    'Stevec_prehodna',
    'Stevec_prehodna_rotiran',
    'Stevec_vstavljanje_pred',
    'Stevec_vstavljanje_spust',
    'suction_off',
    'Stevec_potisk_pred1',
    'Stevec_potisk_pred',
    'Stevec_potisk_pred_rotiran',
    'Stevec_potisnjen',
    'Stevec_v_skatlji_pobiranje_pred',
    'Stevec_v_skatlji_pobiranje_nad',
    'Stevec_v_skatlji_pobiranje',
    'suction_on',
    'Stevec_v_skatlji_rotacija_spodaj',
    'Stevec_v_skatlji_rotacija_pred',
    'Stevec_v_skatlji_rotacija_polovicno',
    'Stevec_v_skatlji_rotiran',
    'Stevec_v_skatlji_vstavljanje_pred',
    'suction_off',
    #dodatna mal nad
    'Stevec_potisk_pred',
    'Stevec_potisk_pred_rotiran',
    'Stevec_v_skatlji_potisk_pred_rotiran',
    'Stevec_v_skatlji_potisk_koncna',
    #dodat mal nazaj
    'Stevec_v_skatlji_potisk_koncna_po',
    'Stevec_spakiran_pobiranje_zgoraj',
    'Stevec_spakiran_pobiranje',
    'suction_on',
    'Stevec_spakiran_prehod',
]


ZAPOREDJE_TOCK_PREPRIJEM_OZJI_ROB = [
    'Stevec_spakiran_obracanje',
    'Stevec_spakiran_ozji_bok_nad',
    'Stevec_spakiran_ozji_bok',
    'Stevec_spakiran_preprijem_ozji_bok_prehod',
    'Stevec_spakiran_preprijem_ozji_bok_nad',
    'Stevec_spakiran_preprijem_ozji_bok_pred',
    'Stevec_spakiran_preprijem_ozji_bok',
    'Stevec_spakiran_preprijem_ozji_bok_nad',
]

ZAPOREDJE_TOCK_PREPRIJEM_DALJSI_ROB = [
    'Stevec_spakiran_obracanje',
    'Stevec_spakiran_daljsi_bok_prehod',
    'Stevec_spakiran_daljsi_bok_nad',
    'Stevec_spakiran_daljsi_bok_pred',
    'Stevec_spakiran_daljsi_bok_pred1',
    'Stevec_spakiran_daljsi_bok',
    'Stevec_spakiran_preprijem_daljsi_bok_prehod',
    'Stevec_spakiran_preprijem_daljsi_bok_pred',
    'Stevec_spakiran_preprijem_daljsi_bok_nad',
    'Stevec_spakiran_preprijem_daljsi_bok_nad1',
    'Stevec_spakiran_preprijem_daljsi_bok',
    'Stevec_spakiran_preprijem_daljsi_bok_nad_po',
]

ZAPOREDJE_TOCK_ODLAGANJE =[]
ZAPOREDJE_TOCK_ODLAGANJE_OZJI_ROB =[]
ZAPOREDJE_TOCK_ODLAGANJE_DALJSI_ROB =[]

########################################################################################
# Load environment file
load_dotenv()

# Import environment variables
OPERATION_MODE = os.getenv("OPERATION_MODE")
START_CUT_IMAGE_X = int(os.getenv("START_CUT_IMAGE_X"))
START_CUT_IMAGE_Y = int(os.getenv("START_CUT_IMAGE_Y"))
END_CUT_IMAGE_X = int(os.getenv("END_CUT_IMAGE_X"))
END_CUT_IMAGE_Y = int(os.getenv("END_CUT_IMAGE_Y"))


# Console class for logging
class Console(tk.Text):
    def __init__(self, *args, **kwargs):
        kwargs.update({"state": "disabled"})
        tk.Text.__init__(self, *args, **kwargs)
        self.bind("<Destroy>", self.reset)
        self.old_stdout = sys.stdout
        sys.stdout = self
    
    def delete(self, *args, **kwargs):
        self.config(state="normal")
        self.delete(*args, **kwargs)
        self.config(state="disabled")
    
    def write(self, content):
        self.config(state="normal")
        self.insert("end", content)
        self.config(state="disabled")
    
    def reset(self, event):
        sys.stdout = self.old_stdout


# Application class
class Application(tk.Frame):

    packing_string = None

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Robotic sorter and packer")
        
        # Create canvas
        self.canvas = tk.Canvas(self.root, width=1400, height=600)
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

        # Create a drop down menu
        Application.packing_string = tk.StringVar(self.root)
        Application.packing_string.set("X") # default value
        self.options = ["X", "Y", "Z"]

        self.drop_down = tk.OptionMenu(self.root, Application.packing_string, *self.options)
        self.drop_down.pack()

        self.button3 = tk.Button(self.root, text="Pack object")
        self.button3.place(x=300, y=100)
        self.button3.pack()
        # Bind the button to the pack_object function
        self.button3.bind("<Button-1>", self.pack_object)

        self.button4 = tk.Button(self.root, text="Stop robot")
        self.button4.place(x=400, y=100)
        self.button4.pack()
        # Bind the button to the stop function
        self.button4.bind("<Button-1>", self.stop_robot)

        self.button5 = tk.Button(self.root, text="Scan QR")
        self.button5.place(x=500, y=100)
        self.button5.pack()
        # Bind the button to the stop function
        self.button5.bind("<Button-1>", self.scan_qr)

        # Scrolled text command widget
        self.log_widget = Console(self.root, height=9, width=70, font=("Arial", "8"))
        self.log_widget.pack()
       

        ########################################################################################
        # Position GUI elements
        # Zero top left corner is about 50 pixels down and 250 pixels right
        self.canvas.create_text(230, 30, text="ROBOTIC SORTER AND PACKER", font=("Arial", 20))

        self.canvas.create_text(150, 80, text="Find objects using CV and set\nthem to respected starting positions", font=("Arial", 12))
        self.canvas.create_window(80, 120, window=self.button1)

        self.canvas.create_text(110, 160, text="Insert object into the box", font=("Arial", 12))
        self.canvas.create_window(80, 190, window=self.button2)

        self.canvas.create_text(65, 230, text="Pack object", font=("Arial", 12))
        self.canvas.create_window(152, 260, window=self.button3)

        self.canvas.create_text(70, 300, text="Stop the robot", font=("Arial", 12))
        self.canvas.create_window(72, 330, window=self.button4)
        
        self.canvas.create_text(70, 370, text="Scan QR code", font=("Arial", 12))
        self.canvas.create_window(70, 400, window=self.button5)

        self.log_widget.place(x=10, y=440)

        self.drop_down.place(x=20, y=242)

        # Open the webcam
        self.cap = cv2.VideoCapture(1)
        self.cap.set(3, 1920) # Width
        self.cap.set(4, 1080) # Height

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
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            
            # Resize image
            width, height = cv2image.shape[:2]
            resized_image = cv2.resize(cv2image, (int(width/2), int(height/2)))
            
            img = Image.fromarray(resized_image)
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

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            edges = cv2.Canny(gray, 100, 200, apertureSize=7, L2gradient = False)

            # Find contours 
            contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 

            sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)

            packaging_contour = sorted_contours[0]
            counter_contour = sorted_contours[2]

            # Draw all contours
            cv2.drawContours(frame, [packaging_contour, counter_contour], -1, (0, 255, 0), 3)

            cv2.imshow("Frame", frame)
            cv2.waitKey(0)

            

    def insert_object(self, event):
        print(time.strftime("[ %H:%M:%S", time.localtime()) + "." + str(int(time.time() * 1000) % 1000).zfill(3) + " ]  " + "Inserting object")

        robot = robotComm.HC10('192.168.0.1')

        #incilizacija robota 


        info = {}
        if robot.ERROR_SUCCESS == robot.acquire_system_info(robot.SystemInfoType.R1, info):
            print("Robot version:")
            print(info)
            print("\n")
            
        if robot.ERROR_SUCCESS != robot.reset_alarm(robot.RESET_ALARM_TYPE_ALARM):
            print("failed resetting alarms, err={}".format(hex(robot.errno)))
            
        if robot.switch_power(robot.POWER_TYPE_SERVO, robot.POWER_SWITCH_ON) > 1:
            print("failed turning on servo power supply, err={}".format(hex(robot.errno)))

        # 0x3450 
        status = {}
        try:
            if robot.ERROR_SUCCESS == robot.get_status(status):
                print("Robot status:")
                print(status)
                print("\n")
        except:
            pass

        time.sleep(1)

        # premikanje po točkah
        path = '~/Documents/DIR2023/points_data'

        #sharnjene točke
        positions = pd.read_csv(path + '/positions.csv',index_col=0)
        #preverjanje stanja servo motorjev
        status = {}
        if robot.ERROR_SUCCESS == robot.get_status(status):
            if not status['servo_on']:
                robot.switch_power(robot.POWER_TYPE_SERVO, robot.POWER_SWITCH_ON)

        
        for i in range(len(ZAPOREDJE_TOCK_SKATLJA)):
            #pojdi čez vse točke
            next_point = ZAPOREDJE_TOCK_SKATLJA[i]
            if next_point == 'suction_on':
                robot.select_job('GRIP_O')
                robot.play_job()
                time.sleep(1)
            elif next_point == 'suction_off':
                robot.select_job('GRIP_C')
                robot.play_job()
                time.sleep(1)
            elif next_point == 'Stevec_prehodna_rotiran':
                pos = positions[next_point].values
                robot.one_move(robot.MOVE_TYPE_LINEAR_ABSOLUTE_POS, robot.MOVE_COORDINATE_SYSTEM_BASE, robot.MOVE_SPEED_CLASS_MILLIMETER, 300, pos,tool_no=0)
                while(self.move_complete(robot=robot) != True):
                    pass
            else:
                pos = positions[next_point].values
                robot.one_move(robot.MOVE_TYPE_LINEAR_ABSOLUTE_POS, robot.MOVE_COORDINATE_SYSTEM_BASE, robot.MOVE_SPEED_CLASS_MILLIMETER, 600, pos,tool_no=0)
                while(self.move_complete(robot=robot) != True):
                    pass

        for i in range(len(ZAPOREDJE_TOCK_STEVEC)):
            #pojdi čez vse točke
            next_point = ZAPOREDJE_TOCK_STEVEC[i]
            if next_point == 'suction_on':
                robot.select_job('GRIP_O')
                robot.play_job()
                time.sleep(1)
            elif next_point == 'suction_off':
                robot.select_job('GRIP_C')
                robot.play_job()
                time.sleep(1)
            elif next_point == 'Stevec_prehodna_rotiran':
                pos = positions[next_point].values
                robot.one_move(robot.MOVE_TYPE_LINEAR_ABSOLUTE_POS, robot.MOVE_COORDINATE_SYSTEM_BASE, robot.MOVE_SPEED_CLASS_MILLIMETER, 300, pos,tool_no=0)
                while(self.move_complete(robot=robot) != True):
                    pass
            else:
                pos = positions[next_point].values
                robot.one_move(robot.MOVE_TYPE_LINEAR_ABSOLUTE_POS, robot.MOVE_COORDINATE_SYSTEM_BASE, robot.MOVE_SPEED_CLASS_MILLIMETER, 600, pos,tool_no=0)
                while(self.move_complete(robot=robot) != True):
                    pass




    def pack_object(self, event):
        print(time.strftime("[ %H:%M:%S", time.localtime()) + "." + str(int(time.time() * 1000) % 1000).zfill(3) + " ]  " + "Packing object")

        # Check packaging string variable
        if Application.packing_string.get() == "X":
            print(time.strftime("[ %H:%M:%S", time.localtime()) + "." + str(int(time.time() * 1000) % 1000).zfill(3) + " ]  " + "Packing object for X orientation")

        elif Application.packing_string.get() == "Y":
            print(time.strftime("[ %H:%M:%S", time.localtime()) + "." + str(int(time.time() * 1000) % 1000).zfill(3) + " ]  " + "Packing object for Y orientation")
        
        elif Application.packing_string.get() == "Z":
            print(time.strftime("[ %H:%M:%S", time.localtime()) + "." + str(int(time.time() * 1000) % 1000).zfill(3) + " ]  " + "Packing object for Z orientation")
        
        else:
            print(time.strftime("[ %H:%M:%S", time.localtime()) + "." + str(int(time.time() * 1000) % 1000).zfill(3) + " ]  " + "Wrong packaging string")




    def stop_robot(self, event):
        print(time.strftime("[ %H:%M:%S", time.localtime()) + "." + str(int(time.time() * 1000) % 1000).zfill(3) + " ]  " + "Stopping")


    def scan_qr(self, event):
        
        ret, frame = self.cap.read()
        
        if ret == True:

            # Cut off edeges of the image
            frame = frame[START_CUT_IMAGE_Y:END_CUT_IMAGE_Y, START_CUT_IMAGE_X:END_CUT_IMAGE_X]

            try:
                # Find QR code
                data, bbox, rectifiedImage = cv2.QRCodeDetector().detectAndDecode(frame)
                
                if len(data) > 0:
                    print(time.strftime("[ %H:%M:%S", time.localtime()) + "." + str(int(time.time() * 1000) % 1000).zfill(3) + " ]  " + "Decoded Data : {}".format(data))

                    with open('NativeApp/data.csv', 'w', newline='') as csvfile:
                        writer = csv.writer(csvfile, delimiter=',')

                        writer.writerow(["QR-code", str(data)])


                else:
                    print(time.strftime("[ %H:%M:%S", time.localtime()) + "." + str(int(time.time() * 1000) % 1000).zfill(3) + " ]  " + "QR Code not detected")

            except Exception as e:
                print(time.strftime("[ %H:%M:%S", time.localtime()) + "." + str(int(time.time() * 1000) % 1000).zfill(3) + " ]  " +"Scan failed")
                print(e)

        else:
            print(time.strftime("[ %H:%M:%S", time.localtime()) + "." + str(int(time.time() * 1000) % 1000).zfill(3) + " ]  " +"Couldn't read frame")
    

    def move_complete(self, robot):
        # se se robot premika je vrednost TRUE drugace fallse 
    
        status = {}
        if robot.ERROR_SUCCESS == robot.get_status(status):
            if status['running'] != True:
                return True
            
            else:
                return False
        return False



##########################################################################################################################################
if __name__ == "__main__":

    if OPERATION_MODE == 'dev':
        pass
    elif OPERATION_MODE == 'prod':
        pass
    else:
        print(time.strftime("[ %H:%M:%S", time.localtime()) + "." + str(int(time.time() * 1000) % 1000).zfill(3) + " ]  " + "Error: Couldn't get OPERATION mode from environment file, please set it")


    # Create the application
    app = Application()
    
