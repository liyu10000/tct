import os
import cv2
import numpy as np

video_file = './video-sample.avi'
cap = cv2.VideoCapture(video_file)

while True:
    ret, frame = cap.read()

    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if ret:
        cv2.imshow('frame',frame)
    else:
        break
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()