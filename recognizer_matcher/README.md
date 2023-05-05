# Reference Implementation: How-to Build a Face Access Control Solution

python encode_faces.py --dataset dataset --encodings encodings.pickle

python faces_recognition.py --encodings maint_knn_model.clf \
	--image examples/example_01.png

python faces_recognition.py --encodings maint_knn_model.clf \
	--output output/webcam_face_recognition_output.avi --display 0 

python faces_recognition.py --encodings maint_knn_model.clf \
	--input videos/lunch_scene.mp4 --display 0 
