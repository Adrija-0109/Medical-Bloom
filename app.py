from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import keras.backend as K
from datetime import datetime as dt
import numpy as np
import cv2
from cv2 import resize, INTER_AREA
import uuid
from PIL import Image
import os
import tempfile
from keras.models import load_model
import imageio
from keras.preprocessing import image
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout, Flatten
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
import keras
from keras.applications import vgg16
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.applications.imagenet_utils import decode_predictions

def resize_image_oct(image):
    resized_image = cv2.resize(image, (128,128)) 
    if(len(resized_image.shape)!=3):
        resized_image = cv2.cvtColor(resized_image,cv2.COLOR_GRAY2RGB) 
    return resized_image

def resize_image_pnm(image):
    resized_image = cv2.resize(image, (128,128)) 
    if(len(resized_image.shape)!=3):
        resized_image = cv2.cvtColor(resized_image,cv2.COLOR_GRAY2RGB) 
    return resized_image

def load_vgg16_model():
  input_shape = (224, 224, 3)

  #Instantiate an empty model
  vgg_model = Sequential([
  Conv2D(64, (3, 3), input_shape=input_shape, padding='same', activation='relu'),
  Conv2D(64, (3, 3), activation='relu', padding='same'),
  MaxPooling2D(pool_size=(2, 2), strides=(2, 2)),
  Conv2D(128, (3, 3), activation='relu', padding='same'),
  Conv2D(128, (3, 3), activation='relu', padding='same',),
  MaxPooling2D(pool_size=(2, 2), strides=(2, 2)),
  Conv2D(256, (3, 3), activation='relu', padding='same',),
  Conv2D(256, (3, 3), activation='relu', padding='same',),
  Conv2D(256, (3, 3), activation='relu', padding='same',),
  MaxPooling2D(pool_size=(2, 2), strides=(2, 2)),
  Conv2D(512, (3, 3), activation='relu', padding='same',),
  Conv2D(512, (3, 3), activation='relu', padding='same',),
  Conv2D(512, (3, 3), activation='relu', padding='same',),
  MaxPooling2D(pool_size=(2, 2), strides=(2, 2)),
  Conv2D(512, (3, 3), activation='relu', padding='same',),
  Conv2D(512, (3, 3), activation='relu', padding='same',),
  Conv2D(512, (3, 3), activation='relu', padding='same',),
  MaxPooling2D(pool_size=(2, 2), strides=(2, 2)),
  Flatten(),
  Dense(4096, activation='relu'),
  Dense(4096, activation='relu'),
  Dense(1000, activation='softmax')
  ])

  vgg_model.load_weights("/static/weights/vgg16.h5")
  return vgg_model

"""Instantiating the flask object"""
app = Flask(__name__)
CORS(app)

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/choose_disease.html')
def choose_diasese():
    return render_template('choose_disease.html')

@app.route('/brain_tumuor.html')
def brain():
    return render_template('brain_tumuor.html')

@app.route('/malaria.html')
def malaria():
    return render_template('malaria.html')

@app.route('/pneumonia.html')
def pnm():
    return render_template('pneumonia.html')

@app.route('/diabetes.html')
def retino():
    return render_template('diabetes.html')


@app.route("/", methods = ["POST", "GET"])
def index():
  print(request)
  if request.method == "POST":
    type_ = request.form.get("type", None)
    data = None
    final_json = []
    if 'img' in request.files:
      file_ = request.files['img']
      name = os.path.join(tempfile.gettempdir(), str(uuid.uuid4().hex[:10]))
      file_.save(name)
      print("[DEBUG: %s]"%dt.now(),name)

      if(type_=="mal" or type_=='brain'):
        test_image = image.load_img(name, target_size = (128, 128))
        test_image = image.img_to_array(test_image)
        test_image = test_image/255
        test_image = np.expand_dims(test_image, axis = 0)
        data=test_image

      elif(type_=='pnm' or type_=='dia_ret'):
        test_image = Image.open(name)                                  
        test_image = test_image.resize((128,128), Image.ANTIALIAS)     
        test_image = np.array(test_image)                              
        test_image = test_image/255                                    
        test_image = np.expand_dims(test_image, axis=0)                
        data = test_image

      model=get_model(type_)[0]

      if(type_=='mal'):
         preds, pred_val = translate_malaria(model["model"].predict_proba(data))
         final_json.append({"empty": False, "type":model["type"], 
                            "para":preds[0], 
                            "unin":preds[1],
                            "pred_val": pred_val})
      elif(type_=='brain'):
         preds, pred_val = translate_brain(model["model"].predict_proba(data))
         final_json.append({"empty": False, "type":model["type"], 
                            "tumor":preds[0], 
                            "normal":preds[1],
                            "pred_val": pred_val})
      elif(type_=='pnm'):
         preds, pred_val = translate_pnm(model["model"].predict_proba(data))
         final_json.append({"empty": False, "type":model["type"], 
                            "bac":preds[0], 
                            "normal":preds[1],
                            "viral":preds[2],
                            "pred_val": pred_val})

      elif(type_=='dia_ret'):
         preds, pred_val = translate_retinopathy(model["model"].predict_proba(data))
         final_json.append({"empty": False, "type":model["type"], 
                            "mild":preds[0], 
                            "mod":preds[1],
                            "norm":preds[2],
                            "severe":preds[3],
                            "pred_val": pred_val})
    else:
      warn = "Feeding blank image won't work. Please enter an input image to continue."
      pred_val =" "
      final_json.append({"pred_val": warn,"para": " ","unin": " ","tumor": " ", "can":" ",
                         "normal": " ","bac": " ","viral": " ","cnv": " ","dme": " ",
                         "drusen": " ","mild": " ","mod": " ","severe": " ","norm": " ",
                         "top1": " ","top2": " ","top3": " ","top4": " ","top5": " "}) 

    K.clear_session()
    return jsonify(final_json)
  return jsonify({"empty":True})

"""This function is used to load the model from disk."""
def load_model_(model_name):
  model_name = os.path.join("/static/weights",model_name)
  model = load_model(model_name)
  return model

"""This function is used to load the specific model for specific request calls. This
function will return a list of dictionary items, where the key will contain the loaded
models and the value will contain the request type."""
def get_model(name = None):
  model_name = []
  if(name=='mal'):
    model_name.append({"model": load_model_("malaria.h5"), "type": name})
  elif(name=='brain'):
    model_name.append({"model": load_model_("brain_tumor.h5"), "type": name})
  elif(name=='pnm'):
    model_name.append({"model": load_model_("pneumonia.h5"), "type": name})
  elif(name=='dia_ret'):
    model_name.append({"model": load_model_("diabetes_retinopathy.h5"), "type": name})
  return model_name

"""preds will contain the predictions made by the model. We will take the class probabalities and 
store them in individual variables. We will return the class probabilities and the final predictions
made by the model to the frontend. The value contained in variables total and prediction will be
displayed in the frontend HTML layout."""
def translate_malaria(preds):
  y_proba_Class0 = preds.flatten().tolist()[0] * 100
  y_proba_Class1 = 100.0-y_proba_Class0

  para_prob="Probability of the cell image to be Parasitized: {:.2f}%".format(y_proba_Class1)
  unifected_prob="Probability of the cell image to be Uninfected: {:.2f}%".format(y_proba_Class0)

  total = para_prob + " " + unifected_prob
  total = [para_prob,unifected_prob]

  if (y_proba_Class1 > y_proba_Class0):
      prediction="Inference: The cell image shows strong evidence of Malaria."
      return total,prediction
  else:
      prediction="Inference: The cell image shows no evidence of Malaria."
      return total,prediction

"""This function also does the same thing as above. Since it's a two class classification problem, 
we can subtract one probability percentage values from 100 to get the other value."""
def translate_cancer(preds):
  y_proba_Class0 = preds.flatten().tolist()[0] * 100
  y_proba_Class1 = 100.0-y_proba_Class0

  can="Probability of the histopathology image to have cancer: {:.2f}%".format(y_proba_Class1)
  norm="Probability of the histopathology image to be normal: {:.2f}%".format(y_proba_Class0)

  total = [can,norm]

  if (y_proba_Class1 > y_proba_Class0):
      prediction="Inference: The histopathology image shows strong evidence of Invasive Ductal Carcinoma."
      return total,prediction
  else:
      prediction="Inference: The cell image shows no evidence of Invasive Ductal Carcinoma."
      return total,prediction

"""Tis function will compute the values for the brain cancer model"""
def translate_brain(preds):
  y_proba_Class0 = preds.flatten().tolist()[0] * 100
  y_proba_Class1 = 100.0-y_proba_Class0

  tumor="Probability of the MRI scan to have a brain tumor: {:.2f}%".format(y_proba_Class1)
  normal="Probability of the MRI scan to not have a brain tumor: {:.2f}%".format(y_proba_Class0)

  total = [tumor, normal]

  if (y_proba_Class1 > y_proba_Class0):
      prediction="Inference: The MRI scan has a brain tumor."
      return total,prediction
  else:
      prediction="Inference: The MRI scan does not show evidence of any brain tumor."
      return total,prediction

def translate_oct(preds):
  y_proba_Class0 = preds.flatten().tolist()[0] * 100
  y_proba_Class1 = preds.flatten().tolist()[1] * 100
  y_proba_Class2 = preds.flatten().tolist()[2] * 100
  y_proba_Class3 = preds.flatten().tolist()[3] * 100

  cnv="Probability of the input image to have Choroidal Neo Vascularization: {:.2f}%".format(y_proba_Class0)
  dme="Probability of the input image to have Diabetic Macular Edema: {:.2f}%".format(y_proba_Class1)
  drusen="Probability of the input image to have Hard Drusen: {:.2f}%".format(y_proba_Class2)
  normal="Probability of the input image to be absolutely normal: {:.2f}%".format(y_proba_Class3)

  total = [cnv,dme,drusen,normal]
  
  list_proba = [y_proba_Class0,y_proba_Class1,y_proba_Class2,y_proba_Class3]
  statements = ["Inference: The image has high evidence of Choroidal Neo Vascularization in the retinal pigment epithelium.",
               "Inference: The image has high evidence of Diabetic Macular Edema in the retinal pigment epithelium.",
               "Inference: The image has high evidence of Hard Drusen in the retinal pigment epithelium.",
               "Inference: The retinal pigment epithelium layer looks absolutely normal."]
  
  
  index = list_proba.index(max(list_proba))
  prediction = statements[index]

  return total, prediction

def translate_pnm(preds):
  y_proba_Class0 = preds.flatten().tolist()[0] * 100
  y_proba_Class1 = preds.flatten().tolist()[1] * 100
  y_proba_Class2 = preds.flatten().tolist()[2] * 100

  bac="Probability of the image to be Bacterial Pneumonia: {:.2f}%".format(y_proba_Class0)
  norm="Probability of the image to be Normal: {:.2f}%".format(y_proba_Class1)
  viral="Probability of the image to be Viral Pneumonia: {:.2f}%\n".format(y_proba_Class2)

  total = [bac,norm,viral]

  list_proba = [y_proba_Class0,y_proba_Class1,y_proba_Class2]
  statements = ["Inference: The chest X-Ray image shows high evidence of Bacterial Pneumonia.",
                "Inference: The chest X-Ray image is normal.",
                "Inference: The chest X-Ray image shows high evidence of Viral Pneumonia."]
  
  index = list_proba.index(max(list_proba))
  prediction = statements[index]

  return total, prediction

def translate_retinopathy(preds):
  y_proba_Class0 = preds.flatten().tolist()[0] * 100
  y_proba_Class1 = preds.flatten().tolist()[1] * 100
  y_proba_Class2 = preds.flatten().tolist()[2] * 100
  y_proba_Class3 = preds.flatten().tolist()[3] * 100

  mild="Probability of the input image to have Mild Diabetic Retinopathy: {:.2f}%".format(y_proba_Class0)
  mod="Probability of the input image to have Moderate Diabetic Retinopathy: {:.2f}%".format(y_proba_Class1)
  norm="Probability of the input image to be Normal: {:.2f}%".format(y_proba_Class2)
  severe="Probability of the input image to have Severe Diabetic Retinopathy: {:.2f}%".format(y_proba_Class3)

  total = [mild,mod,norm,severe]
  
  list_proba = [y_proba_Class0,y_proba_Class1,y_proba_Class2,y_proba_Class3]
  statements = ["Inference: The image has high evidence for Mild Nonproliferative Diabetic Retinopathy Disease.",
               "Inference: The image has high evidence for Moderate Nonproliferative Diabetic Retinopathy Disease.",
               "Inference: The image has no evidence for Nonproliferative Diabetic Retinopathy Disease.",
               "Inference: The image has high evidence for Severe Nonproliferative Diabetic Retinopathy Disease."]
  
  index = list_proba.index(max(list_proba))
  prediction = statements[index]

  return total, prediction

#Predict image using VGG16 pretrained models

def convert_results(string):
  name = string.replace("_"," ")
  name = name.replace("-"," ")
  name = name.title()
  return name

def translate_vgg_16(preds):
  label = decode_predictions(preds)
  class_list = []
  conf_list = []

  for classes in label[0]:
      class_list.append(classes[1])
      conf_list.append(classes[2])

  top1 = convert_results(class_list[0])
  top2 = convert_results(class_list[1])
  top3 = convert_results(class_list[2])
  top4 = convert_results(class_list[3])
  top5 = convert_results(class_list[4])

  top1_proba = conf_list[0]
  top2_proba = conf_list[1]
  top3_proba = conf_list[2]
  top4_proba = conf_list[3]
  top5_proba = conf_list[4]

  top1_sent = ["Probability of the input image to be {}: {:.2f}%".format(top1,top1_proba*100)]
  top2_sent = ["Probability of the input image to be {}: {:.2f}%".format(top2,top2_proba*100)]
  top3_sent = ["Probability of the input image to be {}: {:.2f}%".format(top3,top3_proba*100)]
  top4_sent = ["Probability of the input image to be {}: {:.2f}%".format(top4,top4_proba*100)]
  top5_sent = ["Probability of the input image to be {}: {:.2f}%".format(top5,top5_proba*100)]

  total = [top1_sent,top2_sent,top3_sent,top4_sent,top5_sent]

  if(top1.endswith("s")):
    prediction = ["The image is most likely to be of {}.".format(top1)]
  else:
    prediction = ["The image is most likely to be of a {}.".format(top1)]

  return total, prediction

if __name__=="__main__":
  app.run("0.0.0.0",80, debug = False)