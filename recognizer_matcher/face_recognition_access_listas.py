import configparser
import datetime
import pickle
import sys

import cv2
import face_recognition

from ffmpeg import server_open
from logger import set_logger
from mqtt import paho_start

mq_port = 'localhost'
mq_host = 1883
ff_server = 'localhost'
cam_url = ''
cam_number = 0
knn_filename_lblancas = 'maint_knn_model.clf'
knn_filename_lnegras = 'maint_knn_model.clf'
distance_threshold = 0.4
resize = 0.5
period = 10
frame_number = 0
proc = None
detected_faces_lblancas = []
detected_faces_lnegras = []


def config_start(filename):
    global mq_port
    global mq_host
    global ff_server
    global cam_url
    global cam_number
    global knn_filename_lblancas
    global knn_filename_lnegras
    global distance_threshold
    global resize
    global period
    parser = configparser.ConfigParser()
    parser.read(filename)
    mq_host = parser.get('mqtt', 'server')
    mq_port = parser.getint('mqtt', 'port')
    ff_server = parser.get('ffserver', 'output_file')
    cam_url = parser.get('camera', 'url')
    cam_number = parser.getint('camera', 'number')
    knn_filename_lblancas = parser.get('KNN', 'filename_lblancas')
    knn_filename_lnegras = parser.get('KNN', 'filename_lnegras')
    distance_threshold = parser.getfloat('KNN', 'distance_threshold')
    resize = parser.getfloat('face_recognition', 'resize')
    period = parser.getint('face_recognition', 'period')


def open_cam_input(camera_number, camera_url):
    if camera_number == -1:
        cam = cv2.VideoCapture()
        cam.open(camera_url)
    else:
        cam = cv2.VideoCapture(camera_number)

    if cam.isOpened():
        fps = cam.get(cv2.CAP_PROP_FPS)
        if fps < 7:
            cam.set(cv2.CAP_PROP_FPS, 30)
            fps = 30
        return True, fps, cam
    else:
        logger.error("Error: fail to capture video.")
        return False, 2, None


def load_face_db(filename_lblancas, filename_lnegras):
    global knn_model_lblancas
    global knn_model_lnegras
    knn_model_lblancas = pickle.load(open(filename_lblancas, 'rb'))
    knn_model_lnegras = pickle.load(open(filename_lnegras, 'rb'))
    return True


def get_next_image(cv):
    ret, image = cv.read()
    if ret is True:
        return True, image
    else:
        return False, None


def look_for_faces(frame_small):
    face_locations = face_recognition.face_locations(frame_small)
    face_encodings = face_recognition.face_encodings(frame_small, face_locations)
    return face_locations, face_encodings


def recognize_faces(x_face_locations, x_faces_encodings, model, dt):
    predictions = []
    if len(x_face_locations) > 0:
        closest_distances = model.kneighbors(x_faces_encodings, n_neighbors=4)
        are_matches = []
        for i in range(len(x_face_locations)):
            are_matches.append(min(closest_distances[0][i][0], closest_distances[0][i][1]) <= dt)
        for pred, loc, rec in zip(model.predict(x_faces_encodings), x_face_locations, are_matches):
            if rec:
                predictions.append((pred, loc))
            else:
                predictions.append(("unknown", loc))
    return predictions


def output_frame(ff_host, img):
    ff_host.stdin.write(img.tostring())


def display(faces, process, size, mq, img_frame, eslistasnegras):
    if process is None:
        logger.error('Error')
    else:
        for name, (top, right, bottom, left) in faces:
            top *= int(1 / size)
            right *= int(1 / size)
            bottom *= int(1 / size)
            left *= int(1 / size)
            #if name == 'unknown' and not eslistasnegras:
            #    color = (0, 0, 255)
            #else:
            if name != 'unknown':
                if eslistasnegras:
                    color = (255, 0, 0)
                else:
                    color = (0, 255, 0)
                logger.info('{} - {}'.format(name, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                payload = "{\"id\": \"" + name.split('@')[0] + "\"}"
                client.connect(mq_host, mq_port)
                mq.publish("person/seen", payload)
                cv2.rectangle(img_frame, (left, top), (right, bottom), color, thickness=2, lineType=8)
        output_frame(process, img_frame)


if __name__ == "__main__":
    logger = set_logger()
    logger.info("starting CVSERVICE ... ")
    config_start('frac.ini')
    logger.info("mq_port {}".format(mq_port))
    logger.info("mq_host {}".format(mq_host))
    logger.info("ff_server {}".format(ff_server))
    logger.info("cam_url {}".format(cam_url))
    logger.info("cam_number {}".format(cam_number))
    logger.info("knn_filename_lblancas {}".format(knn_filename_lblancas))
    logger.info("knn_filename_lnegras {}".format(knn_filename_lnegras))
    logger.info("distance_threshold {}".format(distance_threshold))
    logger.info("resize {}".format(resize))
    logger.info("period {}".format(period))

    try:
        client = paho_start("cvservice", True)
        try:
            client.connect(mq_host, mq_port)
        except Exception:
            logger.error("Error MQTT connecting ... ")
            exit(1)
        flag_cam, f_count, vc = open_cam_input(cam_number, cam_url)
        logger.info(f_count)
        if flag_cam is not True:
            logger.error("Error opening camera ... ")
            exit(1)
        else:
            flag_image, frame = get_next_image(vc)
            if flag_image:
                flag_proc, proc = server_open(ff_server, frame.shape[1], frame.shape[0], f_count)
                if flag_proc:
                    logger.error("Error connecting to ffserver")
                    exit(1)
        flag = load_face_db(knn_filename_lblancas, knn_filename_lnegras)
        if flag is not True:
            logger.error("Error load model")
            exit(1)
        logger.info("Started")
        while True:
            frame_number += 1
            flag_image, frame = get_next_image(vc)
            #frame = cv2.flip(frame, 1)
            if flag_image:
                if (frame_number % period) == 0:
                    small_frame = cv2.resize(frame, (0, 0), fx=resize, fy=resize)
                    rgb_small_frame = small_frame[:, :, ::-1]
                    locations, recognitions = look_for_faces(rgb_small_frame)
                    detected_faces_lnegras = recognize_faces(locations, recognitions, knn_model_lnegras, distance_threshold)
                    detected_faces_lblancas = recognize_faces(locations, recognitions, knn_model_lblancas, distance_threshold)
                display(detected_faces_lnegras, proc, resize, client, frame, True)
                display(detected_faces_lblancas, proc, resize, client, frame, False)

        client.disconnect()
        client.close()
        exit(0)
    except Exception:
        logger.error("Exception {}".format(sys.exc_info()[0]))
        exit(1)
