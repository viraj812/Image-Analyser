from flask import Flask, render_template, request, send_file
from main import analyse_image
from waitress import serve
import os

app = Flask('Image Analyser')

app.config['ENV'] = 'production'
app.config['DEBUG'] = False

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/test")
def analysed():
    return render_template('analysed.html')

@app.route("/analysed", methods=['GET', 'POST'])
def getImage():
    img = request.files.get('imgfile')
    img.save("./imgfile.jpg")
    analyse_image("./imgfile.jpg")
    return render_template("analysed.html")

@app.route("/<filename>")
def handleFile(filename):
    flag = os.path.exists('./static/images/' + filename)
    if(flag):
        return send_file('static/images/' + filename, mimetype='image/jpeg')
    else:
        return "Resource Not Found", 404
    
serve(app, port=8080)