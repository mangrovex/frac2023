import argparse
#import math
from sklearn import neighbors
#import os
import os.path
import pickle
#import face_recognition_access
#from face_recognition_access.face_recognition_cli import image_files_in_folder
#import face_recognition
#from face_recognition.face_recognition_cli import image_files_in_folder
import prepair_data

def determineQuantityNeighbors(length_data, verbose=False):
    """
    Determine automatically quantity of neighbors
    :param length_data: Length of data
    :param verbose: verbosity of function
    :return quanty of neighbors
    """
    # Determine how many neighbors to use for weighting in the KNN classifier
    n_neighbors = int(round(math.sqrt(len(X))))

    if verbose:
        print("Chose n_neighbors automatically:", n_neighbors)

    return n_neighbors


def trainKNN(model_save_path, X, y, n_neighbors, knn_algorithm, function_weights='distance'):
    """
    Trains a k-nearest neighbors classifier for face recognition.
    :param model_save_path: (optional) path to save trained model on disk
    :parm X: list of encoding photos
    :parm y: list of labels
    :param n_neighbors: number of neighbors to weigh in classification
    :param knn_algorithm: underlying data structure to support knn
    :param function_weights: wieght function use in clasification. Default='distance'
    :returns knn classfier that was trained on the given data
    """
    # Create and train the KNN classifier
    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algorithm, weights=function_weights)
    # fit data into knn model
    knn_clf.fit(X, y)

    # Save the trained KNN classifier
    if model_save_path is not None:
        with open(model_save_path, 'wb') as f:
            pickle.dump(knn_clf, f)
            
    return knn_clf


def trainFromFile(train_file, model_save_path=None, n_neighbors=None, knn_algo='ball_tree', verbose=False):
    """
    Trains a k-nearest neighbors classifier for face recognition. Input data is taken from a file
    :param train_file: file that contains a list of photgraphies' encodes and labels
    :param model_save_path: (optional) path to save trained model on disk
    :param n_neighbors: (optional) number of neighbors to weigh in classification. Chosen automatically if not specified
    :param knn_algo: (optional) underlying data structure to support knn.default is ball_tree
    :param verbose: verbosity of training
    :returns knn classfier that was trained on the given data
    """
    X = []
    y = []

    if train_file is None:
        if verbose:
            print("Indicate a train file")
            exit(1)

    # Read data from file that contains encode y labels
    data = prepair_data.readFileEncodeLabels(train_file)

    X = data[0]
    y = data[1]

    # Determine how many neighbors to use for weighting in the KNN classifier
    if n_neighbors is None:
        n_neighbors = determineQuantityNeighbors(len(X))

    knn_clf = trainKNN(model_save_path, X, y, n_neighbors, knn_algo, 'distance')

    return knn_clf


def trainFromDirectory(train_dir, model_save_path=None, n_neighbors=None, knn_algo='ball_tree', verbose=False):
    """
    Trains a k-nearest neighbors classifier for face recognition. Input data is taken from a directory
    :param train_dir: directory that contains a sub-directory for each known person, with its name.
     (View in source code to see train_dir example tree structure)
     Structure:
        <train_dir>/
        ├── <person1>/
        │   ├── <somename1>.jpeg
        │   ├── <somename2>.jpeg
        │   ├── ...
        ├── <person2>/
        │   ├── <somename1>.jpeg
        │   └── <somename2>.jpeg
        └── ...

    :param model_save_path: (optional) path to save model on disk
    :param n_neighbors: (optional) number of neighbors to weigh in classification. Chosen automatically if not specified
    :param knn_algo: (optional) underlying data structure to support knn.default is ball_tree
    :param verbose: verbosity of training
    :return: returns knn classifier that was trained on the given data.
    """
    X = []
    y = []

    if not os.path.isdir(train_dir):
        if verbose:
            print("There is not train file")
            exit(1)

    # Directory
    X, y = prepair_data.encodingDirectory(train_dir, None)

    # Determine how many neighbors to use for weighting in the KNN classifier
    if n_neighbors is None:
        n_neighbors = determineQuantityNeighbors(len(X))

    knn_clf = trainKNN(model_save_path, X, y, n_neighbors, knn_algo, 'distance')
        
    return knn_clf


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--option", type=int)
    ap.add_argument("-d", "--directory", type=str, default=None)
    ap.add_argument("-f", "--file_name", type=str, default=None)
    ap.add_argument("-m", "--model_name", type=str)
    args = vars(ap.parse_args())

    option = args["option"]
    directory = args["directory"]
    file_name = args["file_name"]
    model_name = args["model_name"]

    print("Training KNN classifier...")
    if option == 1:
        classifier = trainFromDirectory(directory, model_save_path=model_name, n_neighbors=4, verbose=True)
    elif option == 2:
        classifier = trainFromFile(file_name, model_save_path=model_name, n_neighbors=4, verbose=True)
    print("Training complete!")
