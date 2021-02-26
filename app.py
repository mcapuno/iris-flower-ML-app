from flask import Flask, render_template, session, redirect, url_for
from flask import request, jsonify
import numpy as np
from tensorflow.keras.models import load_model
import joblib

from FlowerForm import FlowerForm
import os

#---------  prediction function --------------
def return_prediction(model, scaler, sample_json):
    sepal_length = sample_json['sepal_length']
    sepal_width = sample_json['sepal_width']
    petal_length = sample_json['petal_length']
    petal_width = sample_json['petal_width']
    
    flower = [[sepal_length, sepal_width, petal_length, petal_width]]
    
    classes = np.array(['setosa', 'versicolor', 'virginica'])
    
    flower = scaler.transform(flower)
    
    class_index = np.argmax(model.predict(flower), axis=-1)[0]
    
    return classes[class_index]


#########  Flask App #####################
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'


@app.route('/', methods=['GET', 'POST'])
def index():
    form = FlowerForm()
    
    if form.validate_on_submit():
        
        if form.sepal_length.data and form.sepal_width.data and form.petal_length.data and form.petal_width.data:
            # put those data in current session
            session['sepal_length'] = form.sepal_length.data
            session['sepal_width'] = form.sepal_width.data
            session['petal_length'] = form.petal_length.data
            session['petal_width'] = form.petal_width.data
            
            return redirect(url_for('prediction'))
    
    return render_template('home.html', form=form)

# load model and scaler
iris_model = load_model('final_iris_model.h5')
iris_scaler = joblib.load('iris_scaler.pkl')


@app.route('/prediction')
def prediction():
    content = {}
    
    # get data from session object
    content['sepal_length'] = float(session['sepal_length'])
    content['sepal_width'] = float(session['sepal_width'])
    content['petal_length'] = float(session['petal_length'])
    content['petal_width'] = float(session['petal_width'])
    
    results = return_prediction(iris_model, iris_scaler, content)
    
    return render_template('prediction.html', results=results)


@app.route('/api/iris', methods=['POST'])
def predict_flower():
    print(request.json)
    content = request.json
    results = return_prediction(iris_model, iris_scaler, content)
    return jsonify(results)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
    # port change resource
    # https://virantha.com/2013/11/14/starting-a-simple-flask-app-with-heroku/
    