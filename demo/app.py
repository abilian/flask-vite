# Demo Flask app that render the "templates/home.j2" template on "/".

from flask import Flask, render_template

from flask_vite import Vite

app = Flask(__name__)
vite = Vite(app)


@app.route("/")
def home():
    return render_template("home.j2")
