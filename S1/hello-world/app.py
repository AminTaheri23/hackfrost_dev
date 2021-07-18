# This is a hello world example for flask. 
# IF the name of the file wan not app.py, you should do `export FLASK_APP=hello` 
# To run this, you sould run `flask run` in the directory that app.py exists. 
# To activate the debugger: 
# export FLASK_ENV=development

from flask import Flask, render_template
from flask.templating import render_template_string
from markupsafe import escape

app = Flask(__name__)

@app.route("/<name>") # to use vairiables and pass them to functino we use <Variable> notatino, 
# Also, if you want to convert the variable we can use for example, <string:Variable> or <int:Variable>
# Kinds of converter 
# string = (default) accepts any text without a slash
# int = accepts positive integers
# float = accepts positive floating point values
# path = like string but also accepts slashes
# uuid = accepts UUID strings
def hello_world_escape(name):
    return f"Hello, {escape(name)}" # escaping will prevent script injectino attacks!
    
@app.route("/")
def hello_world():
    return "Hello World!" # Hello world

@app.route("/template")
def hello_world_template():
    return render_template("hello.html") # Hello world with template

if __name__ == "__main__":
    app.run(debug=True)