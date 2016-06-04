import MySQLdb
import bcrypt
import json
import random
from flask import Flask, request

# Create the app. 
app = Flask(__name__)

# Connect to the database and setup the db cursor.
db = MySQLdb.connect(host = "localhost",
                     user = "halpTestUser",
                     passwd = "",
                     db = "HalpTest")
cur = db.cursor()

# Helper functions
def getPassword(username):
   cur.execute("""\
      SELECT password
      FROM Users
      WHERE username = %s""",
      (username,)
   );

   pw = cur.fetchone()
   if pw is None:
      return None
   cur.fetchall()

   return pw[0]

# API Routes
@app.route("/")
def main():
   return "Welcome to Halp!"

@app.route("/login", methods=['POST'])
def login():
   data = {}
   hashedpw = getPassword(request.form['username'])

   if hashedpw is None:
      return "Invalid username."
   hashedpw = hashedpw.encode('utf-8')

   # TODO store the new token in the Tokens table and purge the other one if it exists.
   if hashedpw == bcrypt.hashpw(request.form['password'].encode('utf-8'), hashedpw):
      token = '%064x' % random.randrange(16**64)
      data = json.dumps({'token': token})
   else:
      data = "Invalid password."

   return data

@app.route("/user/<string:username>")
def findUsers(username):
   data = {}
   
   cur.execute("""\
      SELECT *
      FROM Users
      WHERE username = %s""",
      (username,)
   );

   row = cur.fetchone()
   if row is None:
      return "No data."

   data = json.dumps({'userId':row[0], 'firstName': row[1], 'lastName': row[2],
                     'username': row[3], 'email': row[4], 'phone': row[5],
                     'bio': row[6], 'gender':row[7]})
   
   # Clear any excess data. 
   cur.fetchall()
   return data

if __name__ == "__main__":
   app.run()
