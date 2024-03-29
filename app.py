from flask import Flask, request, render_template, url_for, Response
from flask.helpers import send_file
import cv2
import os
import keras
from tensorflow.keras.models import model_from_json
import numpy as np
import matplotlib.pyplot as plt
import base64
app = Flask(__name__)



@app.route('/')
def home():
	return render_template("index.html")
	
@app.route('/upload', methods=['GET','POST'])	
def upload():
	global photo_path
	photo_path = None
	if request.method == 'POST':
		uploaded_file = request.files['image']
				
		
		if not uploaded_file:
			return render_template("index.html")

		
		uploaded_file.save('static/uploads/'+uploaded_file.filename)
		
		photo_path = 'static/uploads/'+uploaded_file.filename
		
		return render_template('index.html', photo_path = photo_path)
		
@app.route('/capture', methods=['GET','POST'])	
def capture():
	global image_path
	image_path = None
	
	cap =cv2.VideoCapture(0)
	
	if not cap.isOpened():
		return render_template("index.html")
	
	_,frame = cap.read()
	
	cap.release()

	image_path='static/uploads/'
	os.makedirs(image_path, exist_ok = True)
	image_path = os.path.join(image_path, 'captured_photo.jpeg')
	cv2.imwrite(image_path,frame)
		
	return render_template('index.html', image_path = image_path)	
		

@app.route('/predict', methods=['GET', 'POST'])
def predict():
	
	
	json_file = open('model.json','r')
	loaded_model_json = json_file.read()
	json_file.close()
	
	loaded_model = model_from_json(loaded_model_json)
	
	loaded_model.load_weights("model.h5")
	
	loaded_model.compile(loss='binary_crossentropy',optimizer='adam',metrics=['accuracy'])
	facec = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
	eyes = cv2.CascadeClassifier('haarcascade_eye_tree_eyeglasses.xml')
	if photo_path == None:
		return render_template('index.html', photo_path = photo_path)
		
	img = cv2.imread(photo_path)	
	gray_image = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	faces = facec.detectMultiScale(gray_image, 1.3, 5)
	if faces == ():
		return render_template('error.html', photo_path = photo_path)
	prediction=None
	for x,y,w,h in faces:
		face_roi = gray_image[y:y+h, x:x+w]
		eye = eyes.detectMultiScale(face_roi)
		for ex,ey,ew,eh in eye:
			eye_x = x+ex
			eye_y = y+ey
			eye_w = ew
			eye_h = eh
			eye_roi = img[eye_y:eye_y+eye_h, eye_x:eye_x+eye_w]
			resized_eye = cv2.resize(eye_roi, (24, 24))
			resized_eye = resized_eye / 255.0
			input_data = np.reshape(resized_eye, (1, 24, 24, 3))
			prediction = loaded_model.predict(input_data)
			
			
	if prediction:
		return render_template('open.html', photo_path = photo_path)
		
	else:
		return render_template('close.html', photo_path = photo_path)
	

@app.route('/predict_cap', methods=['GET', 'POST'])
def predict_cap():
	
	
	json_file = open('model.json','r')
	loaded_model_json = json_file.read()
	json_file.close()
	
	loaded_model = model_from_json(loaded_model_json)
	
	loaded_model.load_weights("model.h5")
	
	loaded_model.compile(loss='binary_crossentropy',optimizer='adam',metrics=['accuracy'])
	facec = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
	eyes = cv2.CascadeClassifier('haarcascade_eye_tree_eyeglasses.xml')
	
	if image_path == None:
		return render_template('index.html', image_path = image_path)
	
	img = cv2.imread(image_path)	
	gray_image = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	faces = facec.detectMultiScale(gray_image, 1.3, 5)
	if faces == ():
		return render_template('error.html', image_path = image_path)
	prediction=None
	for x,y,w,h in faces:
		face_roi = gray_image[y:y+h, x:x+w]
		eye = eyes.detectMultiScale(face_roi)
		for ex,ey,ew,eh in eye:
			eye_x = x+ex
			eye_y = y+ey
			eye_w = ew
			eye_h = eh
			eye_roi = img[eye_y:eye_y+eye_h, eye_x:eye_x+eye_w]
			resized_eye = cv2.resize(eye_roi, (24, 24))
			resized_eye = resized_eye / 255.0
			plt.imshow(resized_eye)
			plt.axis('off')  # Optional: Turn off axis labels
			plt.show()
			input_data = np.reshape(resized_eye, (1, 24, 24, 3))
			prediction = loaded_model.predict(input_data)
			
			
	if prediction:
		return render_template('open.html', image_path = image_path)
		
	else:
		return render_template('close.html', image_path = image_path)
	

	
if __name__ == "__main__":
	app.run(debug=True)
