import argparse
import os
import os.path
import pickle
import face_recognition
from face_recognition.face_recognition_cli import image_files_in_folder

def detectionFace(image_path):
    image = face_recognition.load_image_file(image_path)
    return image, face_recognition.face_locations(image)


def encodigFace(train_dir, class_dir, verbose=True):
    X = []
    y = []

    dir_images = os.path.join(train_dir, class_dir)

    if not os.path.isdir(dir_images):
        return X, y

    label = class_dir

    # Loop through each training image for the current person
    for image_path in image_files_in_folder(dir_images):
        image, face_bounding_boxes = detectionFace(image_path)

        if len(face_bounding_boxes) != 1:
            # If there are no people (or too many people) in a training image, skip the image.
            if verbose:
                print("Image {} not suitable for training: {}".format(image_path, "Didn't find a face" if len(face_bounding_boxes) < 1 else "Found more than one face"))
        else:
            print("Image {}".format(image_path))
            # Add face encoding for current image to the training set
            X.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
            y.append(class_dir)

    return X, y


def encodingDirectory(train_dir, class_dir):
    X = []
    y = []

    #print(class_dir)

    if class_dir is None:
        # Loop through each person in the training set
        for directory in os.listdir(train_dir):
            if not os.path.isdir(os.path.join(train_dir, directory)):
               continue

            encode, labels = encodigFace(train_dir, directory)
            X += encode
            y += labels
    else:
        X, y = encodigFace(train_dir, class_dir)

    #print(X)
    #print(y)

    return X, y


def generateNewFileEncodeLabels(train_dir, class_dir, file_name):
    X, y = encodingDirectory(train_dir, class_dir)

    data = [X, y]

    saveFileEncodeLabels(data, file_name)
            
    return data


def appendFileEncodeLabels(train_dir, class_dir, file_name):
    data_org = readFileEncodeLabels(file_name)

    X = data_org[0]
    y = data_org[1]

    new_encodes, new_labels = encodingDirectory(train_dir, class_dir)
    X += new_encodes
    y += new_labels

    data = [X, y]

    saveFileEncodeLabels(data, file_name)


def saveFileEncodeLabels(data, file_name):
    # Save the prepaired data
    if file_name is not None:
        with open(file_name, 'wb') as f:
            pickle.dump(data, f)


def readFileEncodeLabels(file_name):
     f = pickle.load(open(file_name, "rb"))
     #print(f)
     return f


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--option", type=int)
    ap.add_argument("-t", "--train_dir", type=str, default=None)
    ap.add_argument("-c", "--class_dir", type=str, default=None)
    ap.add_argument("-f", "--file_name", type=str, default=None)
    args = vars(ap.parse_args())

    option = args["option"]
    train_dir = args["train_dir"]
    class_dir = args["class_dir"]
    file_name = args["file_name"]

    if option == 1:
        generateNewFileEncodeLabels(train_dir, class_dir, file_name)
    elif option == 2:
        appendFileEncodeLabels(train_dir, class_dir, file_name)
    elif option == 3:
        readFileEncodeLabels(file_name)
