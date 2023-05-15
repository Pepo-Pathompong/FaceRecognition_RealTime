import os
import pickle

import cvzone
import numpy as np
import cv2
import face_recognition

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://facerecognitionrealtime-5b265-default-rtdb.firebaseio.com/",
    'storageBucket': "facerecognitionrealtime-5b265.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')

# importing the mode image into a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
    # print(len(imgModeList))

# Load the encoding file
print("Loading Encode File ...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
# print(studentIds)
print("Encode File Loaded")

modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    # Resize img to match the size of the slice in imgBackground
    img_resized = cv2.resize(img, (380, 325))
    imgBackground[90:90 + 325, 35:35 + 380, :] = img_resized

    mode = cv2.resize(imgModeList[modeType], (340, 435))
    imgBackground[15:15 + mode.shape[0], 470:470 + mode.shape[1], :] = mode

    if faceCurFrame:
        for encodeFace, faceloc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("matches", matches)
            # print("faceDis", faceDis)

            matchIndex = np.argmin(faceDis)
            # print("Match Index", matchIndex)

            if matches[matchIndex]:
                # print("Known Face Detected")
                # print(studentIds[matchIndex])
                y1, x2, y2, x1 = faceloc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = -70 + x1, -25 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

                id = studentIds[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(imgBackground, "loading", (235, 330))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

            if counter != 0:

                if counter == 1:
                    # Get the Data
                    studentInfo = db.reference(f'Students/{id}').get()
                    print(studentInfo)
                # Get the image from the storage
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                # Update data of attendance
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                                   "%Y-%m-%d %H:%M:%S")
                secondElapsed = (datetime.now() - datetimeObject).total_seconds()
                print(secondElapsed)
                if secondElapsed > 30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('total_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    mode = cv2.resize(imgModeList[modeType], (340, 435))
                    imgBackground[15:15 + mode.shape[0], 470:470 + mode.shape[1], :] = mode

            if modeType != 3:

                if 10 < counter < 20:
                    modeType = 2
                    mode = cv2.resize(imgModeList[modeType], (340, 435))
                    imgBackground[15:15 + mode.shape[0], 470:470 + mode.shape[1], :] = mode

            if counter <= 10:
                cv2.putText(imgBackground, str(studentInfo['total_attendance']), (512, 85),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)
                cv2.putText(imgBackground, str(studentInfo['name']), (610, 314),
                                cv2.FONT_HERSHEY_COMPLEX, 0.3, (0, 0, 0), 1)
                cv2.putText(imgBackground, str(studentInfo['major']), (610, 351),
                                cv2.FONT_HERSHEY_COMPLEX, 0.3, (0, 0, 0), 1)
                cv2.putText(imgBackground, str(studentInfo['standing']), (588, 412),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 0), 1)
                cv2.putText(imgBackground, str(studentInfo['year']), (656, 412),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 0), 1)
                cv2.putText(imgBackground, str(studentInfo['starting_year']), (732, 412),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 0), 1)

            imgStudent = cv2.resize(imgStudent, (180, 140))
            imgBackground[125:125 + 140, 550:550 + 180] = imgStudent

        counter += 1

        if counter >= 20:
            counter = 0
            modeType = 0
            studentInfo = []
            imgStudent = []
            mode = cv2.resize(imgModeList[modeType], (340, 435))
            imgBackground[15:15 + mode.shape[0], 470:470 + mode.shape[1], :] = mode
    else:
        modeType = 0
        counter = 0
# cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)
