# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author: SaltFish
# @file: generate_images.py
# @date: 2020/05/30
import cv2
import time
import os

cap = cv2.VideoCapture(0)

if __name__ == "__main__":
    # 等待相机曝光
    while True:
        ret, frame = cap.read()
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # 拍摄5张照片
    for i in range(1):
        ret, frame = cap.read()
        img_path = os.path.join("pictures", "{0}.png".format(i),)
        cv2.imwrite(img_path, frame)
        time.sleep(0.2)
    cap.release()
    cv2.destroyAllWindows()
