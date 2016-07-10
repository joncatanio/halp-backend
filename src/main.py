# File: main.py
# Author: Jon Catanio
# Description: Main Halp api file. 

from flask import Flask
from register import register_api
from login import login_api
from account import account_api
from posts import posts_api
from post_messages import post_messages_api
from classes import classes_api

# Create the app. 
app = Flask(__name__)

# Register blueprints.
app.register_blueprint(register_api)
app.register_blueprint(login_api)
app.register_blueprint(account_api)
app.register_blueprint(posts_api)
app.register_blueprint(post_messages_api)
app.register_blueprint(classes_api)

@app.route("/")
def main():
   return {"Halp"}, 200

if __name__ == "__main__":
   app.debug = True
   app.run()
