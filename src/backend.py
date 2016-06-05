import MySQLdb
import bcrypt
import json
import random
import datetime
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
# Get the password for <username>.
def getPassword(username):
   cur.execute("""\
      SELECT password
      FROM Users
      WHERE username = %s""",
      (username,)
   );
   db.commit()

   pw = cur.fetchone()
   if pw is None:
      return None
   cur.fetchall()

   return pw[0]

# Purge the preexisting token for <username>. 
# purgeToken and addToken are committed together.
def purgeToken(username):
   cur.execute("""\
      UPDATE Tokens
      SET revoked = 1
      WHERE
         revoked = 0
         AND user = (
               SELECT userId
               FROM Users
               WHERE username = %s
            )""", (username,)
   );

# Add a token for <username>. 
def addToken(username, token):
   cur.execute("""\
      INSERT INTO Tokens (
         user,
         token,
         expire,
         revoked
      )
      SELECT
         userId,
         %s,
         NOW() + INTERVAL 15 DAY,
         0
      FROM Users
      WHERE username = %s""", (token, username,)
   );

# Validates a token. Returns true if token is valid and false otherwise.
def validateToken(token):
   cur.execute("""\
      SELECT
         revoked,
         TIMESTAMPDIFF(SECOND, NOW(), expire)
      FROM Tokens
      WHERE token = %s""", (token,)
   );
   db.commit()
   
   row = cur.fetchone()
   if row is None or row[0] == 1 or row[1] <= 0:
      return False

   cur.fetchall()
   return True

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

   if hashedpw == bcrypt.hashpw(request.form['password'].encode('utf-8'), hashedpw):
      token = '%064x' % random.randrange(16**64)
      purgeToken(request.form['username'])
      addToken(request.form['username'], token)
      db.commit()

      data = json.dumps({'token': token})
   else:
      data = "Invalid password."

   return data

@app.route("/user/<string:token>")
def getUser(token):
   data = {}
   
   cur.execute("""\
      SELECT
         U.userId,
         U.firstName,
         U.lastName,
         U.username,
         U.email,
         U.phone,
         U.bio,
         G.description,
         U.school,
         U.major,
         U.year,
         U.verifiedTutor,
         S.name,
         M.name,
         M.abbreviation
      FROM
         Tokens AS T
         INNER JOIN Users AS U ON T.user = U.userId
         INNER JOIN Genders AS G ON U.gender = G.genderId
         INNER JOIN Schools AS S ON U.school = S.schoolId
         INNER JOIN Majors AS M ON U.major = M.majorId
      WHERE
         T.token = %s
         AND U.deleted = FALSE""", (token,)
   );
   db.commit()

   row = cur.fetchone()
   if row is None:
      return "No data."

   data['userId'] = row[0]
   data['firstName'] = row[1]
   data['lastName'] = row[2]
   data['username'] = row[3]
   data['email'] = row[4]
   data['phone'] = row[5]
   data['bio'] = row[6]
   data['gender'] = row[7]
   data['schoolId'] = row[8]
   data['majorId'] = row[9]
   data['year'] = row[10]
   data['verifiedTutor'] = row[11]
   data['school'] = row[12]
   data['major'] = row[13]
   data['majorAbbreviation'] = row[14]
   data = json.dumps(data)
   
   # Clear any excess data. 
   cur.fetchall()
   return data

@app.route("/posts/matched/<string:token>")
def getMatchedPosts(token):
   data = []
   
   if validateToken(token) == False:
      return "Bad token."

   cur.execute("""\
      SELECT
         P.postId,
         PostUser.username,
         P.content,
         P.bounty,
         P.class,
         P.postDate
      FROM
         Tokens AS T
         INNER JOIN Users AS ThisUser ON T.user = ThisUser.userId
         INNER JOIN Posts AS P
         INNER JOIN Users AS PostUser ON P.user = PostUser.userId
      WHERE
         T.token = %s
         AND P.class IN (
               SELECT class
               FROM
                  Tutors AS T
                  INNER JOIN Tokens AS TOK ON T.user = TOK.user
               WHERE
                  TOK.token = %s
                  AND T.unlisted = FALSE
            )
         AND PostUser.school = ThisUser.school
         AND P.resolved = FALSE
         AND P.deleted = FALSE
         AND (P.tutor IS NULL OR P.tutor = 0)""", (token, token,)
   );
   db.commit()
   
   rows = cur.fetchall()
   if rows is None:
      return "No data."

   for row in rows:
      obj = {}
      obj['postId'] = row[0]
      obj['author'] = row[1]
      obj['content'] = row[2]
      obj['bounty'] = row[3]
      obj['classId'] = row[4]
      obj['postDate'] = row[5].isoformat()
      data.append(obj)

   return json.dumps(data)

@app.route("/posts/<string:token>")
def getUserPosts(token):
   data = []

   if validateToken(token) == False:
      return "Bad token."

   cur.execute("""\
      SELECT
         P.postId,
         P.content,
         P.bounty,
         P.class,
         P.postDate,
         P.tutor
      FROM 
         Tokens AS T
         INNER JOIN Posts AS P ON T.user = P.user
      WHERE
         T.token = %s
         AND P.deleted <> 1
         AND P.resolved <> 1""", (token,)
   );
   db.commit()
   
   rows = cur.fetchall()
   if rows is None:
      return "No data."

   for row in rows:
      obj = {}
      obj['postId'] = row[0]  
      obj['content'] = row[1] 
      obj['bounty'] = row[2]
      obj['class'] = row[3]
      obj['postDate'] = row[4].isoformat()
      obj['tutor'] = row[5]
      data.append(obj)

   return json.dumps(data)

@app.route("/posts/helped/<string:token>")
def getUserHelpedPosts(token):
   data = []

   if validateToken(token) == False:
      return "Bad token."

   cur.execute("""\
      SELECT
         P.postId,
         P.content,
         P.bounty,
         P.postDate,
         P.class,
         HelpedUser.username
      FROM
         Tokens AS T
         INNER Join Users AS ThisUser ON T.user = ThisUser.userId
         INNER JOIN Posts AS P ON ThisUser.userId = P.tutor
         INNER JOIN Users AS HelpedUser ON P.user = HelpedUser.userId
      WHERE
         T.token = %s
         AND P.user <> P.tutor
         AND P.resolved = TRUE
         AND P.deleted = FALSE""", (token,)
   );
   db.commit()

   rows = cur.fetchall()
   if rows is None:
      return "No data."

   for row in rows:
      obj = {}
      obj['postId'] = row[0]
      obj['content'] = row[1]
      obj['bounty'] = row[2]
      obj['postDate'] = row[3].isoformat()
      obj['classId'] = row[4]
      obj['postAuthor'] = row[5]
      data.append(obj)

   return json.dumps(data)

# Any way to optimize?
@app.route("/posts/helping/<string:token>")
def getUserHelpingPosts(token):
   data = []

   if validateToken(token) == False:
      return "Bad token."

   cur.execute("""\
      SELECT
         P.postId,
         P.content,
         P.bounty,
         P.postDate,
         P.class,
         HelpedUser.username
      FROM
         Tokens AS T
         INNER Join Users AS ThisUser ON T.user = ThisUser.userId
         INNER JOIN Posts AS P ON ThisUser.userId = P.tutor
         INNER JOIN Users AS HelpedUser ON P.user = HelpedUser.userId
      WHERE
         T.token = %s
         AND P.user <> P.tutor
         AND P.resolved = FALSE
         AND P.deleted = FALSE""", (token,)
   );
   db.commit()

   rows = cur.fetchall()
   if rows is None:
      return "No data."

   for row in rows:
      obj = {}
      obj['postId'] = row[0]
      obj['content'] = row[1]
      obj['bounty'] = row[2]
      obj['postDate'] = row[3].isoformat()
      obj['classId'] = row[4]
      obj['postAuthor'] = row[5]
      data.append(obj)

   return json.dumps(data)

@app.route("/class/<int:classId>")
def getClass(classId):
   data = {}
   
   cur.execute("""\
      SELECT
         C.info,
         CN.abbreviation,
         CN.name,
         S.name,
         S.schoolId,
         M.name,
         M.abbreviation,
         COL.name
      FROM
         Classes AS C
         INNER JOIN ClassNames AS CN ON C.classId = CN.class
         INNER JOIN Schools AS S ON C.school = S.schoolId
         INNER JOIN Majors AS M ON CN.major = M.majorId
         INNER JOIN Colleges AS COL ON M.college = COL.collegeId
      WHERE
         C.classId = %s
         AND C.deleted = FALSE
         AND CN.unlisted = FALSE""", (classId,)
   );
   db.commit()

   rows = cur.fetchall()
   if rows is None:
      return "No data."

   # Get overarching info about the class first.
   iterrows = iter(rows)
   row = next(iterrows)

   data['info'] = row[0]
   data['schoolName'] = row[3]
   data['schoolId'] = row[4]

   names = []
   for row in rows:
      obj = {}
      obj['abbreviation'] = row[1]
      obj['fullName'] = row[2]
      obj['majorName'] = row[5]
      obj['majorAbbreviation'] = row[6]
      obj['collegeName'] = row[7]
      names.append(obj)
   data['names'] = names

   return json.dumps(data)

# TODO Question for Eriq: How do should I split up routes with different params?
# I want to also have an endpoint that gets classes per major. Or should I leave
# that up to the front end devs? 
@app.route("/classes/<int:schoolId>")
def getClasses(schoolId):
   data = []

   cur.execute("""\
      SELECT
         C.classId,
         C.info,
         S.name,
         S.schoolId
      FROM
         Classes AS C
         INNER JOIN Schools AS S ON C.school = S.schoolId
      WHERE
         C.school = %s
         AND C.deleted = FALSE""", (schoolId,)
   );

   rows = cur.fetchall()
   if rows is None:
      return "No data."

   # Get overarching info about the class first.
   for row in rows:
      obj = {}
      obj['classId'] = row[0]
      obj['info'] = row[1]
      obj['schoolName'] = row[2]
      obj['schoolId'] = row[2]

      cur.execute("""\
         SELECT
            CN.abbreviation,
            CN.name,
            M.name,
            M.abbreviation,
            COL.name
         FROM
            Classes AS C
            INNER JOIN ClassNames AS CN ON C.classId = CN.class
            INNER JOIN Schools AS S ON C.school = S.schoolId
            INNER JOIN Majors AS M ON CN.major = M.majorId
            INNER JOIN Colleges AS COL ON M.college = COL.collegeId
         WHERE
            C.classId = %s
            AND C.deleted = FALSE
            AND CN.unlisted = FALSE""", (row[0],)
      )

      innerRows = cur.fetchall()
      if rows is not None:
         names = []
         for innerRow in innerRows:
            innerObj = {}
            innerObj['abbreviation'] = innerRow[0]
            innerObj['fullName'] = innerRow[1]
            innerObj['majorName'] = innerRow[2]
            innerObj['majorAbbreviation'] = innerRow[3]
            innerObj['collegeName'] = innerRow[4]
            names.append(innerObj)

         obj['names'] = names
         data.append(obj)

   db.commit()

   return json.dumps(data)

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
