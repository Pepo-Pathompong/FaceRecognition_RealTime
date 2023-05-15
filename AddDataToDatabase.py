import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://facerecognitionrealtime-5b265-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    "png1":
        {
            "name": "Pathompong",
            "major": "Computer Science",
            "starting_year": 2017,
            "total_attendance": 7,
            "standing": "G",
            "year": 4,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "png2":
        {
                "name": "Dominic",
                "major": "Economics",
                "starting_year": 2021,
                "total_attendance": 12,
                "standing": "B",
                "year": 2,
                "last_attendance_time": "2022-12-11 00:54:34"
         },
    "png3":
         {
                "name": "Brian",
                "major": "Physics",
                "starting_year": 2020,
                "total_attendance": 14,
                "standing": "B",
                "year": 3,
                "last_attendance_time": "2022-12-11 00:54:34"
         },

}

for key,value in data.items():
    ref.child(key).set(value)