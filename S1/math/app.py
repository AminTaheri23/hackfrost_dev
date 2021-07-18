from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return """<H1>Welcome to the Flask Math!</H1>
                <p> Maunual: </p>
                <li> to add: <a href="/20/add/40" target="__blank__"> 127.0.0.1:5000/20/add/40 </a> </li> 
                <li> to subtract: <a href="/20/subtract/40" target="__blank__"> 127.0.0.1:5000/20/subtract/40 </a> </li>
                <li> to multiply: <a href="/20/mul/40" target="__blank__"> 127.0.0.1:5000/20/mul/40 </a> </li>
                <li> to divide: <a href="/20/div/40" target="__blank__"> 127.0.0.1:5000/20/div/40 </a> </li>"""

@app.route('/<int:number>')
def display_number(number):
    """ Displays a number back to the user as-is """
    return "<h1>The result is: \n" + str(number)

@app.route('/<int:x>/add/<int:y>')
def add(x, y):
    """ Adds x and y, returns result """
    return "<h1>The result is: \n" + str(x + y)

@app.route('/<int:x>/subtract/<int:y>')
def subtract(x, y):
    """ Subtracts y from x, returns result """
    return "<h1>The result is: \n" + str(x - y)

@app.route('/<int:x>/mul/<int:y>')
def mul(x, y):
    """ Multiplies y to x, returns result """
    return "<h1>The result is: \n" + str(x * y)

@app.route('/<int:x>/div/<int:y>')
def div(x, y):
    """ Divides y to x, returns result """
    return "<h1>The result is: \n" + str(x / y)

if __name__ == "__main__":
    app.run(debug=True)