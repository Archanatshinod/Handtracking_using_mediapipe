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
    xp, yp = 0, 0
    brushThickness = 15
    drawColor = (0, 0, 255)  # Blue color for drawing
    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)
        if lmList:
            x1, y1 = lmList[8][1:]  
            fingers = detector.fingersUp()
            if fingers[1] and not fingers[2]:
                if xp == 0 and yp == 0:
                    xp, yp = x1, y1  
                cv2.line(img, (xp, yp), (x1, y1), drawColor, brushThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)
                pygame.draw.line(DISPLAYSURF, (255, 255, 255), (xp, yp), (x1, y1), brushThickness)  
                xp, yp = x1, y1  
            else:
                xp, yp = 0, 0  
        imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
        _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
        imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, imgInv)
        img = cv2.bitwise_or(img, imgCanvas)
        cv2.imshow("Canvas", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return render(request, 'handtrack.html')
