# A Flask app that serves the Heroku website
from flask import Flask, render_template

app = Flask(__name__)

# Landing page
@app.route("/")
def home():
    return render_template('home.html')
    
if __name__ == "__main__":
    manager.run()
