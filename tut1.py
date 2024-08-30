from flask import Flask
app = Flask(__name__)

@app.route("/")
def hell0():
    return "hello World"

@app.route("/harry")
def harry():
    return "hello harry bhai"

app.run(debug=True)