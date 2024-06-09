from flask import Flask, render_template, request
from main.py import analyse_image

app = Flask('Image Analyser')

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/imgfile")
def getImage():
    img = request.form.imgfile
    analyse_image(img)
    