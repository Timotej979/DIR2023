import cv2, os

## CAMERA CALIBRATION ##
START_CUT_IMAGE_X=390
START_CUT_IMAGE_Y=160
END_CUT_IMAGE_X=1450
END_CUT_IMAGE_Y=1080

frame = cv2.imread("img1.jpg")        

cv2.imshow("Frame", frame)
cv2.waitKey(0)

# Cut off edeges of the image
frame = frame[START_CUT_IMAGE_Y:END_CUT_IMAGE_Y, START_CUT_IMAGE_X:END_CUT_IMAGE_X]

gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

edges = cv2.Canny(gray, 100, 200, apertureSize=7, L2gradient = False)

# Find contours 
contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 

sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)

# Find the upper left edge of the contour
x,y,w,h = cv2.boundingRect(sorted_contours[0])
upper_left = (x,y)

# Draw the upper left edge on the image
cv2.circle(frame, upper_left, 5, (0,255,0), -1)

# Draw all contours
cv2.drawContours(frame, sorted_contours[0], -1, (0, 255, 0), 3)


