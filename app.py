from flask import Flask, render_template, request, send_file
from main import analyse_image
from waitress import serve

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
    return send_file('./static/images/' + filename, mimetype='image/jpeg')
    
serve(app, port=8080)