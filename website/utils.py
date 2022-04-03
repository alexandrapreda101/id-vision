import face_recognition
import cv2
import numpy as np
import time
import pytesseract
from PIL import Image
import re
from flask import render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash, redirect, url_for, request, render_template
from flask_login import login_user, login_required, logout_user, current_user
from website.models import User, db

# FACE RECOGNITION


def face_rec(path):
    video_capture = cv2.VideoCapture(0)

    image1 = face_recognition.load_image_file(path)
    image1_face_encoding = face_recognition.face_encodings(image1)[0]

    known_face_encodings = [
        image1_face_encoding,
    ]
    known_face_names = [
        "known_face",
    ]

    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    timeout = time.time() + 10

    while True:

        start_time = time.time()
        ret, frame = video_capture.read()
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]
        print(rgb_small_frame)
        if process_this_frame:
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(
                rgb_small_frame, face_locations
            )

            face_names = []
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(
                    known_face_encodings, face_encoding, tolerance=0.6
                )
                name = "Unknown"
                face_distances = face_recognition.face_distance(
                    known_face_encodings, face_encoding
                )
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                face_names.append(name)

        process_this_frame = not process_this_frame
        print("Face detected -- {}".format(face_names))
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.rectangle(
                frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED
            )
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(
                frame, name, (left + 6, bottom - 6), font, 0.6, (255, 255, 255), 1
            )

        cv2.imshow("Video", frame)

        if "known_face" in face_names:
            video_capture.release()
            cv2.destroyAllWindows()
            return True

        if (start_time > timeout) | ("Unknown" in face_names):
            print("Person not recognized")
            video_capture.release()
            cv2.destroyAllWindows()
            return False


def getwidth(path):
    img = Image.open(path)
    size = img.size
    aspectRatio = size[0] / size[1]
    width = 300 * aspectRatio
    return int(width)


# OPTICAL CHARACTER RECOGNITION


# PREPROCESSING
# get grayscale image
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# noise removal
def remove_noise(image):
    return cv2.medianBlur(image, 5)


# skew correction
def deskew(image):
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )
    return rotated


# template matching
def match_template(image, template):
    return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)


# working with multiple languages


# Plot original image


def ocr(path):
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
    image = cv2.imread(path)
    b, g, r = cv2.split(image)
    rgb_img = cv2.merge([r, g, b])
    custom_config = r"-l ron+eng+fra --oem 3 --psm 6"
    # print(pytesseract.image_to_string(rgb_img, config=custom_config))

    all_text = pytesseract.image_to_string(image, config=custom_config)
    fullname = re.search("(?<=IDROU)(.*)", all_text)
    cnp = re.search("[0-9]{13}", all_text).group()
    fullname_string = fullname.group()
    fullname_split = re.split("<<", fullname_string)
    nume = fullname_split[0]
    prenume = re.sub("<", "-", fullname_split[1])
    loc_nastere = re.search("nastere.*[\r\n]([^\r\n]+)", all_text, re.MULTILINE).group(
        1
    )
    domiciliu1 = re.search("Adres.*[\r\n]([^\r\n]+)", all_text, re.MULTILINE)
    domiciliu2 = re.search("Adres.*[\r\n].*[\r\n]([^\r\n]+)", all_text, re.MULTILINE)
    domiciliu = domiciliu1.group(1) + domiciliu2.group(1)
    emis_expirare = re.search("Emis.*[\r\n]([^\r\n]+)", all_text, re.MULTILINE).group(1)
    seria = re.search("<<<<<.*[\r\n]([^\r\n]+)", all_text, re.MULTILINE)
    serie = re.split("<", seria.group(1))[0]

    print(cnp)
    print(nume)
    print(prenume)
    print(loc_nastere)
    print(domiciliu)
    print(emis_expirare)
    print(serie)

    nume_utilizator = nume + prenume[0:3] + cnp[-3:]
    parola = cnp[-6:]

    user = User.query.filter_by(cnp=cnp).first()

    if user:
        flash("CNP-ul este deja existent, mai încearcă", category="error")
    else:
        new_user = User(
            nume_utilizator=nume_utilizator,
            cnp=cnp,
            serie=serie,
            nume=nume,
            prenume=prenume,
            loc_nastere=loc_nastere,
            domiciliu=domiciliu,
            emis_expirare=emis_expirare,
            parola=generate_password_hash(parola, method="sha256"),
        )

        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        flash("Contul a fost creat!", category="success")
        return redirect(url_for("pagina_mea"))

    return render_template("inregistrare.html", user=current_user)
