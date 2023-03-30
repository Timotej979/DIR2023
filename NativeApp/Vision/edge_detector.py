import cv2, os

## CAMERA CALIBRATION ##
START_CUT_IMAGE_X=600
START_CUT_IMAGE_Y=500
END_CUT_IMAGE_X=1100
END_CUT_IMAGE_Y=800

cap = cv2.VideoCapture(1)

cap.set(3, 1920)
cap.set(4, 1080)

ret, frame = cap.read()

# Cut off edeges of the image
frame = frame[START_CUT_IMAGE_Y:END_CUT_IMAGE_Y, START_CUT_IMAGE_X:END_CUT_IMAGE_X]


cv2.imshow("Calib", frame)
cv2.waitKey(0)
