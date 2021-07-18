#  This is a hello world example for flask. 
#  IF the name of the file wan not app.py, you should do `export FLASK_APP=hello` 
# To run this, you sould run `flask run` in the directory that app.py exists. 
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template("hello.html") #hello world

#To activate the debugger: 
# export FLASK_ENV=development