from flask import Flask
import socketio
import eventlet
from keras.models import load_model
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import cv2

sio = socketio.Server()

app = Flask(__name__)

def img_preprocessing(img) :
  img = img[60:135,:,:]
  img = cv2.cvtColor(img,cv2.COLOR_BGR2YUV)
  img = cv2.GaussianBlur(img,(3,3),0)
  img = cv2.resize(img,(200,66))
  img = img/255
  return img

speed_limit = 3.0

@sio.on('telemetry') 
def telemetry(sid,data) :
    speed = float(data['speed'])
    image = Image.open(BytesIO(base64.b64decode(data['image'])))
    image = np.asarray(image)
    image = img_preprocessing(image)
    image = np.array([image])
    steering_angle=float(model.predict(image))
    throttle = 1.0 - speed/speed_limit
    print('{} {} {}'.format(steering_angle,throttle,speed))
    send_control(steering_angle,throttle)

@sio.on('connect')
def connect(sid,envrion) :
    print("Connected")
    send_control(0,0)

def send_control(steering_angle,throttle):
    sio.emit('steer',data={
        'steering_angle' :steering_angle.__str__(),
        'throttle': throttle.__str__()
    })

if __name__ == '__main__' :
    # model = load_model('model.h5')
    # model = load_model('model2.h5') # best
    # model = load_model('first_trial.h5')
    # model = load_model('model4.h5')
    # model = load_model('second_trial.h5')
    model = load_model('model3.h5') # best
    app = socketio.Middleware(sio,app)
    eventlet.wsgi.server(eventlet.listen(('',4567)),app)