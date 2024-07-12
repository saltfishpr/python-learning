# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author: SaltFish
# @file: main.py
# @date: 2020/05/30
import face_recognition
import cv2
import numpy as np

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

# 加载样本图片并学习如何识别它。
obama_image = face_recognition.load_image_file("pictures/obama.jpeg")
obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

biden_image = face_recognition.load_image_file("pictures/biden.jpeg")
biden_face_encoding = face_recognition.face_encodings(biden_image)[0]

saltfish_image = face_recognition.load_image_file("pictures/saltfish.png")
saltfish_face_encoding = face_recognition.face_encodings(saltfish_image)[0]

# 创建已知面部编码及其名称的数组
known_face_encodings = [
    obama_face_encoding,
    biden_face_encoding,
    saltfish_face_encoding,
]
known_face_names = ["Barack Obama", "Joe Biden", "Salt Fish"]

# 初始化一些变量
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

while True:
    # 抓取一帧视频
    ret, frame = video_capture.read()
    # 将视频帧调整为1/4尺寸以加快人脸识别处理
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    # 将图像从BGR颜色（OpenCV使用的颜色）转换为RGB颜色（face_recognition使用的颜色）
    rgb_small_frame = small_frame[:, :, ::-1]

    # 仅处理其他视频帧以节省时间
    if process_this_frame:
        # 查找当前视频帧中的所有面部和面部编码
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(
            rgb_small_frame, face_locations
        )

        face_names = []
        for face_encoding in face_encodings:
            # 查看面孔是否与已知面孔相匹配
            matches = face_recognition.compare_faces(
                known_face_encodings, face_encoding, tolerance=0.6
            )
            name = "Unknown"
            # 使用距离新脸最近的已知脸
            face_distances = face_recognition.face_distance(
                known_face_encodings, face_encoding
            )
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            face_names.append(name)

            # 由于处理前缩小了尺寸，这里放大
            face_locations = (np.array(face_locations) * 4).tolist()
            # 记录下每个面部的位置
            frame_images = []
            for (top, right, bottom, left) in face_locations:
                frame_images.append(frame[top:bottom, left:right])
            frame = cv2.GaussianBlur(frame, (99, 99), 30)
            for (top, right, bottom, left), frame_img in zip(
                face_locations, frame_images
            ):
                frame[top:bottom, left:right] = frame_img

            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # 在脸上画一个框
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                # 在面部下方绘制名称标签
                cv2.rectangle(
                    frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED
                )
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(
                    frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1
                )
            # 显示结果图像
            cv2.imshow("Video", frame)

    process_this_frame = not process_this_frame

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
