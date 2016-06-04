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

@app.route("/posts/<string:username>")
def UserPosts(username):
   data = {}

   cur.execute("""\
      SELECT P.postId, P.user, P.content, P.bounty, P.class, P.postDate, P.resolved, P.tutor, P.deleted
      FROM USERS U JOIN POSTS P ON P.user = U.userId
      WHERE U.username = %s""", (username,)
   );
   
   row = cur.fetchone()
   if row is None:
      return "No data."

   data = json.dumps({'postId':row[0], 'user': row[1], 'content': row[2],
                     'bounty': row[3], 'class': row[4], 'resolved': row[6], 
                     'tutor':row[7], 'deleted':row[8]})

   # Clear any excess data.
   cur.fetchall()
   return data

@app.route("/pastHalped/<string:username>")
def UserPastHalped(username):
   data = {}

   cur.execute("""\
      SELECT P.postId, P.user, P.content, P.bounty, P.class, P.postDate, P.resolved, P.tutor, P.deleted
      FROM USERS U JOIN POSTS P ON P.tutor = U.userId
      WHERE U.username = %s AND P.resolved = TRUE""", (username,)
      
   );

   row = cur.fetchone()
   if row is None:
      return "No data."

   data = json.dumps({'postId':row[0], 'user': row[1], 'content': row[2],
                     'bounty': row[3], 'class': row[4], 'resolved': row[6],
                     'tutor':row[7], 'deleted':row[8]})

   # Clear any excess data.
   cur.fetchall()
   return data

@app.route("/currentHalped/<string:username>")
def UserCurrentHalped(username):
   data = {}

   cur.execute("""\
      SELECT P.postId, P.user, P.content, P.bounty, P.class, P.postDate, P.resolved, P.tutor, P.deleted
      FROM USERS U JOIN POSTS P ON P.tutor = U.userId
      WHERE U.username = %s AND P.resolved = FALSE""", (username,)

   );

   row = cur.fetchone()
   if row is None:
      return "No data."

   data = json.dumps({'postId':row[0], 'user': row[1], 'content': row[2],
                     'bounty': row[3], 'class': row[4], 'resolved': row[6],
                     'tutor':row[7], 'deleted':row[8]})

   # Clear any excess data.
   cur.fetchall()
   return data

@app.route("/messages/<int:post_Id>")
def PostMessages(post_Id):
   data = {}

   cur.execute("""\
      SELECT P.postId, M.messageId, M.content, M.postDate, M.user
      FROM PostMessages PM JOIN Posts P ON PM.post = P.postId JOIN Messages M ON PM.message = M.messageId
      WHERE PM.post = %s""", (str(post_Id),)

   );

   rows = cur.fetchall()
   if rows is None:
      return "No data."
   temp = []
   
   for row in rows :
      temp.append({'postId': row[0], 'messageId':  row[1], 'content':  row[2], 'user': row[4]})
   data = json.dumps(temp)
   # Clear any excess data.
   cur.fetchall()
   return data



if __name__ == "__main__":
   app.run()
