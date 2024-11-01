from flask import Flask, render_template, request, send_file
from main import analyse_image

app = Flask('Image Analyser')

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/analysed")
def analysed():
    return render_template('analysed.html')

@app.route("/imgfile", methods=['GET', 'POST'])
def getImage():
    img = request.files.get('imgfile')
    img.save("./imgfile.jpg")
    analyse_image("./imgfile.jpg")
    return render_template("analysed.html")

@app.route("/<filename>")
def handleFile(filename):
    return send_file('./static/images/' + filename, mimetype='image/jpeg')
    
app.run(debug=True)