#Anggota Kelompok
#-----------------------
#6A - 19090012 - Arief Rachman
#6a - 19090142 - M Rizqi Fauzi Maksum

import numpy as np
import keras
from keras.models import Sequential
from keras.layers import Dense,Conv2D,MaxPool2D,Dropout,BatchNormalization,Flatten,Activation
from keras.preprocessing import image 
from keras.preprocessing.image import ImageDataGenerator
from keras.utils.vis_utils import plot_model
import pickle
from flask import Flask, jsonify,request,flash,redirect,render_template, session,url_for
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from itsdangerous import json
from werkzeug.utils import secure_filename
import os
from flask_cors import CORS
from flask_restful import Resource, Api
import pymongo
from pymongo import MongoClient
import re
import hashlib
import datetime

app = Flask(__name__)

jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'bigtuing'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)

UPLOAD_FOLDER = 'foto_tanaman'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

MONGO_ADDR = 'mongodb://localhost:27017'
MONGO_DB = "herbalia"

app.secret_key = "bigprojek"
conn = pymongo.MongoClient(MONGO_ADDR)
db = conn[MONGO_DB]
users_collection = db["admin"]

api = Api(app)
CORS(app)

from tensorflow.keras.models import load_model
MODEL_PATH = 'model/model.h5'
model = load_model(MODEL_PATH,compile=False)

pickle_inn = open('model/num_class_herbal.pkl','rb')
num_classes_bird = pickle.load(pickle_inn)

@app.route("/api/v1/users", methods=["POST"])
def register():
	new_user = request.get_json()
	new_user["password"] = new_user["password"]
	doc = users_collection.find_one({"username": new_user["username"]})
	if not doc:
		users_collection.insert_one(new_user)
		return jsonify({'msg': 'User Admin berhasil dibuat'}), 201
	else:
		return jsonify({'msg': 'Username sudah pernah dibuat'}), 409
	return jsonify({'msg': 'Username atau Password Salah'}), 401

@app.route("/api/v1/login", methods=["POST"])
def loginApi():
	login_details = request.get_json()
	user_from_db = users_collection.find_one({'username': login_details['username']})

	if user_from_db:
		password = login_details['password']
		if password == user_from_db['password']:
			access_token = create_access_token(identity=user_from_db['username'])
			return jsonify(access_token=access_token), 200

@app.route("/api/v1/user", methods=["GET"])
@jwt_required()
def profile():
	current_user = get_jwt_identity()
	user_from_db = users_collection.find_one({'username' : current_user})
	if user_from_db:
		del user_from_db['_id'], user_from_db['password']
		return jsonify({'profile' : user_from_db }), 200
	else:
		return jsonify({'msg': 'Profil admin tidak ditemukan'}), 404


def allowed_file(filename):     
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class index(Resource):
  def post(self):

    if 'image' not in request.files:
      flash('No file part')
      return jsonify({
            "pesan":"tidak ada form image"
          })
    file = request.files['image']
    if file.filename == '':
      return jsonify({
            "pesan":"tidak ada file image yang dipilih"
          })
    if file and allowed_file(file.filename):
      path_del = r"foto_tanaman\\" #sesuai folder
      for file_name in os.listdir(path_del):
        
        file_del = path_del + file_name
        if os.path.isfile(file_del):
            print('Deleting file:', file_del)
            os.remove(file_del)
            print("file "+file_del+" telah terhapus")
      filename = secure_filename(file.filename)
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      path=("foto_tanaman/"+filename)

      #def predict(dir):
      img=keras.utils.load_img(path,target_size=(224,224))
      img1=keras.utils.img_to_array(img)
      img1=img1/255
      img1=np.expand_dims(img1,[0])
      predict=model.predict(img1)
      classes=np.argmax(predict,axis=1)
      for key,values in num_classes_bird.items():
          if classes==values:
            accuracy = float(round(np.max(model.predict(img1))*100,2))
            info = db['tanamanHerbal'].find_one({'nama': str(key)}) #nama collection database

            if accuracy > 50:
              print("Prediksi tanaman herbal: "+str(key)+" dengan probabilitas "+str(accuracy)+"%")
        
              return jsonify({
                "nama":str(key),
                "Accuracy":str(accuracy)+"%",
                "deskripsi": info['deskripsi'], #nama column
                "khasiat" : info['khasiat'],            
              })
            else :
              print("Prediksi tanaman herbal: "+str(key)+" dengan probabilitas "+str(accuracy)+"%")
              return jsonify({
                "Message":str("Apa ini ?? "),
                "Accuracy":str(accuracy)+"%"               
                
              })
      
    else:
      return jsonify({
        "Message":"bukan file image"
      })

@app.route('/admin') #database admin
def admin():
    return render_template("login.html")


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db['admin'].find_one({'username': str(username)})
        print(user)

        if user is not None and len(user) > 0:
            if password == user['password']:
                
                session['username'] = user['username']
                return redirect(url_for('dataTanaman'))
            else:
                return redirect(url_for('login'))
        else:
            return redirect(url_for('login'))
    else:
        return render_template('login.html')
    
    return render_template('dataTanaman.html')

@app.route('/dataTanaman')
def dataTanaman():
    data = db['tanamanHerbal'].find({})
    print(data)
    return render_template('dataTanaman.html',dataTanaman  = data)



@app.route('/editTanaman/<nama>', methods = ['POST', 'GET'])
def editTanaman(nama):
  
    data = db['tanamanHerbal'].find_one({'nama': nama})
    print(data)
    return render_template('editTanaman.html', editTanaman = data)

#melakukan roses edit data
@app.route('/updateTanaman/<nama>', methods=['POST'])
def updateTanaman(nama):
    if request.method == 'POST':
        nama = request.form['nama']
        deskripsi = request.form['deskripsi']
        khasiat = request.form['khasiat']
        if not re.match(r'[A-Za-z]+', nama):
            flash("Format huruf ga boleh angka")
        else:
          db.tanamanHerbal.update_one({'nama': nama}, 
          {"$set": {
            'nama': nama,  
            'deskripsi': deskripsi, 
            'khasiat': khasiat
            }
            })

          flash('Data berhasil diupdate')
          return render_template("popUpEdit.html")

    return render_template("dataTanaman.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


api.add_resource(index, "/api/image", methods=["POST"])

if __name__ == '__main__':
  app.run(debug = True, port=5000, host='0.0.0.0')
