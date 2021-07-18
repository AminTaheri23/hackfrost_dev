import random
from flask import Flask

app = Flask(__name__)

def random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

@app.route("/")
def rainbow():
    return f"""
<head>
    <style>
        body {{
            background-color: {random_color()}
        }}
    </style>
</head>
<body>
    <p>Rainbow Flask</p>
</body>
    """

if __name__ == "__main__":
    app.run(debug=True)