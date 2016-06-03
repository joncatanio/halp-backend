import MySQLdb
import bcrypt
from flask import Flask

# Create the app. 
app = Flask(__name__)

# Connect to the database and setup the db cursor.
db = MySQLdb.connect(host = "localhost",
                     user = "halpTestUser",
                     passwd = "",
                     db = "HalpTest")
cur = db.cursor()


@app.route("/")
def hello():
   return "Hello World!"

@app.route("/findUsers")
def findUsers():
   return "found users"

if __name__ == "__main__":
   app.run()
