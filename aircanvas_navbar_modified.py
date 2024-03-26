from django.shortcuts import render
import cv2
import numpy as np
import pygame

import sys
import os

# Assuming HandTrackingModule.py is in the same directory as views.py
module_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(module_dir)

from HandTrackingModule import handDetector
import time

def index(request):
    return render(request, 'handtrack.html')
def aircanvas(request):
     cap = cv2.VideoCapture(0)
     width, height = 1280, 720 
     cap.set(3, width)  
     cap.set(4, height) 
     imgCanvas = np.zeros((height, width, 3), np.uint8)
     pygame.init()
     DISPLAYSURF = pygame.display.set_mode((width, height), flags=pygame.HIDDEN)
     detector = handDetector(detectionCon=0.85)
     x1,y1=0,0
     xp, yp = 0, 0
     brushThickness = 15
     eraserThickness = 30   
     drawColor = (0,0,255) 

     color_dict = {
        ord('b'): (135, 206, 235),  # Skin
        ord('g'): (0, 255, 0),   # Green
        ord('r'): (0, 0, 255),   # Red  
        ord('y'): (0, 255, 255), # Yellow
        ord('w'): (255, 255, 255), # White
        ord('e'): (0, 0, 0)  # Eraser (Black color)
     }
     while True:
        success, img = cap.read()
        img = cv2.flip(img, 1) 

       
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False) 
        if len(lmList) > 0:
            x1, y1 = lmList[8][1:]
            x2, y2 = lmList[12][1:] 

            fingers = detector.fingersUp()  

           
            if fingers[1] and fingers[2] == False:
                if xp == 0 and yp == 0:
                    xp, yp = x1, y1  

                
                if drawColor == (0, 0, 0):
                    cv2.circle(img, (x1, y1), eraserThickness, (0, 0, 0), cv2.FILLED)
                    cv2.circle(imgCanvas, (x1, y1), eraserThickness, (0, 0, 0), cv2.FILLED)
                else:
                    cv2.line(img, (xp, yp), (x1, y1), drawColor, brushThickness)
                    cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)
                    pygame.draw.line(DISPLAYSURF, (255, 255, 255), (xp, yp), (x1, y1), brushThickness) 

                xp, yp = x1, y1 
            else:
                xp, yp = 0, 0  

        imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
        _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
        imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)

        img = cv2.bitwise_or(img, imgCanvas)

        for i, (key, color) in enumerate(color_dict.items()):
            cv2.rectangle(img, (i * int(width / len(color_dict)), 0), ((i + 1) * int(width / len(color_dict)), 50), color, cv2.FILLED)
        cv2.rectangle(img, (width - 50, 0), (width, 50), (0, 0, 0), cv2.FILLED)
        cv2.putText(img, "X", (width - 40, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

       
        if y1 < 50:
            selected_option_index = int(x1 / (width / len(color_dict)))
            if selected_option_index < len(color_dict):
                selected_option_key = list(color_dict.keys())[selected_option_index]
                if selected_option_key == ord('e'): 
                    drawColor = (0, 0, 0) 
                else:
                    drawColor = color_dict[selected_option_key]

        
        if x1 > width - 50 and y1 < 50:
            break 
        cv2.imshow("Canvas", img)
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break
     cap.release()
     cv2.destroyAllWindows()
