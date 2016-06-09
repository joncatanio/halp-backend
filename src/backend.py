import MySQLdb
from _mysql_exceptions import MySQLError, IntegrityError
import bcrypt
import json
import random
import datetime
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request

# Create the app. 
app = Flask(__name__)

# Connect to the database and setup the db cursor.
db = MySQLdb.connect(host = "localhost",
                     user = "halpTestUser",
                     passwd = "",
                     db = "HalpTest")
cur = db.cursor()

# TODO Break out into multiple packages, create custom module.
# Custom Exceptions
class EmailError(Exception):
   def __init__(self, value):
      self.value = value
   def __str__(self):
      return repr(self.value)

# Helper functions
# Returns a True or False value if an account has been verified by email.
def validAccount(username):
   try:
      cur.execute("""\
         SELECT verifiedAccount
         FROM Users
         WHERE username = %s""", (username,)
      )
      db.commit()
   except MySQLError:
      raise
   
   row = cur.fetchone()
   if row is None or row[0] == 0:
      return False

   cur.fetchall()
   return True

# Same as validAccount() but verifies with a token.
def validAccountT(token):
   try:
      cur.execute("""\
         SELECT verifiedAccount
         FROM
            Users AS U
            INNER JOIN Tokens AS T ON U.userId = T.user
         WHERE token = %s""", (token,)
      )
      db.commit()
   except MySQLError:
      raise
   
   row = cur.fetchone()
   if row is None or row[0] == 0:
      return False

   cur.fetchall()
   return True

# Get the password for <username>.
def getPassword(username):
   try:
      cur.execute("""\
         SELECT password
         FROM Users
         WHERE username = %s""", (username,)
      )
      db.commit()
   except MySQLError:
      raise

   pw = cur.fetchone()
   if pw is None:
      return None

   cur.fetchall()
   return pw[0]

# Get the password for the user with token: <token>
def getPasswordT(token):
   try:
      cur.execute("""\
         SELECT password
         FROM
            Users AS U
            INNER JOIN Tokens AS T ON U.userId = T.user
         WHERE token = %s""", (token,)
      )
      db.commit()
   except MySQLError:
      raise

   pw = cur.fetchone()
   if pw is None:
      return None

   cur.fetchall()
   return pw[0]

# Purge the preexisting token for <username>. 
# purgeToken and addToken are committed together.
def purgeToken(username):
   try:
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
      )
   except MySQLError:
      raise

# Add a token for <username>. 
def addToken(username, token):
   try:
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
      )
   except IntegrityError:
      raise
   except MySQLError:
      raise

# Validates a token. Returns true if token is valid and false otherwise.
def validateToken(token):
   try:
      cur.execute("""\
         SELECT
            revoked,
            TIMESTAMPDIFF(SECOND, NOW(), expire)
         FROM Tokens
         WHERE token = %s""", (token,)
      )
      db.commit()
   except MySQLError:
      raise

   row = cur.fetchone()
   if row is None or row[0] == 1 or row[1] <= 0:
      return False

   cur.fetchall()
   return True

# Generates a random token represented as a 64 character hexidecimal string. 
def generateToken():
   return '%064x' % random.randrange(16**64)

# Forms and sends an email to verify a users account.
# Returns
def sendEmailVerification(email, name, token):
   try:
      content = "Please click the link below to verify your account\n" +\
                "http://localhost:5000/verify/" + token
      msg = MIMEText(content, 'plain')
      msg['From'] = "noreply <noreply@joncatanio.com>"
      msg['To'] = name + " <" + email + ">"
      msg['Subject'] = "Verify Halp Account"

      server = smtplib.SMTP('mail.joncatanio.com', 26)
      server.starttls()
      server.login('noreply@joncatanio.com', '[emailnoreplyaccount616]')
      server.sendmail("noreply@joncatanio.com", email, msg.as_string())
      server.quit()
   except Exception:
      raise EmailError('')
 
# API Routes
@app.route("/")
def main():
   return "Welcome to Halp!"

@app.route("/register", methods = ['POST'])
def register():
   response = {}
   hashedpw = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
   
   try:
      cur.execute("""\
         INSERT INTO Users VALUES
            (NULL, %s, %s, %s, %s, NULL, NULL, NULL, NULL, %s, %s, %s, NULL, 0, NOW(), 0, 0)""",
         (request.form['firstName'], request.form['lastName'], request.form['username'],
         request.form['email'], hashedpw, request.form['schoolId'],
         request.form['majorId'],)
      );
   except IntegrityError:
      response['message'] = 'Username or email already taken.'
      response['status_code'] = 400
      return json.dumps(response)
   except MySQLError:
      response['message'] = 'Internal Server Error.'
      response['status_code'] = 500
      return json.dumps(response)

   try:
      token = generateToken()
      addToken(request.form['username'], token)
   except IntegrityError:
      response['message'] = 'Duplicate token.'
      response['status_code'] = 500
      return json.dumps(response)
   except MySQLError:
      response['message'] = 'Internal Server Error.'
      response['status_code'] = 500
      return json.dumps(response)
  
   try:
      sendEmailVerification(request.form['email'], request.form['firstName'] + ' ' +
                            request.form['lastName'], token)
   except EmailError:
      response['message'] = 'Email verification error.'
      response['status_code'] = 500
      return json.dumps(response)
      
   # Commit Users and Tokens table updates.
   db.commit()

   response['message'] = "OK. Pending token validation."
   response['status_code'] = 201
   return json.dumps(response)

@app.route("/verify/<string:token>")
def verify(token):
   response = {}
   
   try: 
      if validateToken(token) == False:
         response['message'] = "Invalid token."
         response['status_code'] = 401
         return json.dumps(response)

      cur.execute("""\
         UPDATE 
            Users AS U
            INNER JOIN Tokens AS T ON U.userId = T.user 
         SET
            verifiedAccount = 1
         WHERE token = %s""", (token,)
      )
      db.commit()
   except MySQLError:
      response['message'] = 'Internal Server Error.'
      response['status_code'] = 500
      return json.dumps(response)

   response['message'] = "verified"
   response['status_code'] = 200
   return json.dumps(response)

@app.route("/login", methods = ['POST'])
def login():
   data = {}
   response = {}

   try:
      hashedpw = getPassword(request.form['username'])
      if hashedpw is None:
         response['message'] = 'Invalid username.'
         response['status_code'] = 401
         return json.dumps(response) 
      hashedpw = hashedpw.encode('utf-8')

      if not validAccount(request.form['username']):
         response['message'] = 'Account not verified.'
         response['status_code'] = 401
         return json.dumps(response) 

      if hashedpw == bcrypt.hashpw(request.form['password'].encode('utf-8'), hashedpw):
         token = generateToken()
         purgeToken(request.form['username'])
         addToken(request.form['username'], token)
         db.commit()

         data['token'] = token
      else:
         response['message'] = 'Invalid password.'
         response['status_code'] = 401
         return json.dumps(response) 
   except IntegrityError:
      response['message'] = 'Duplicate token.'
      response['status_code'] = 500
      return json.dumps()
   except MySQLError:
      response['message'] = 'Internal Server Error.'
      response['status_code'] = 500
      return json.dumps(response)

   return json.dumps(data) 

@app.route("/profile/", methods = ['GET', 'POST'])
def profile():
   data = {}
   response = {}

   try:
      if validateToken(request.headers['authentication']) == False:
         response['message'] = "Invalid token."
         response['status_code'] = 403
         return json.dumps(response)

      if not validAccountT(request.headers['authentication']):
         response['message'] = 'Account not verified.'
         response['status_code'] = 401
         return json.dumps(response) 
   except MySQLError:
      response['message'] = 'Internal Server Error.'
      response['status_code'] = 500
      return json.dumps(response)
      
   if request.method == 'POST':
      try:
         cur.execute("""\
            UPDATE
               Users AS U
               INNER JOIN Tokens AS T ON U.userId = T.user
            SET
               U.firstName = %s,
               U.lastName = %s,
               U.dateOfBirth = %s,
               U.bio = %s,
               U.gender = %s,
               U.school = %s,
               U.major = %s,
               U.year = %s
            WHERE
               T.token = %s""",
            (request.form['firstName'], request.form['lastName'],
            request.form['dateOfBirth'], request.form['bio'],
            request.form['gender'], request.form['school'],
            request.form['major'], request.form['year'],
            request.headers['authentication'],)
         )
         db.commit()
         
         response['message'] = 'OK.'
         response['status_code'] = 200
         return json.dumps(response)
      except MySQLError:
         response['message'] = 'Internal Server Error.'
         response['status_code'] = 500
         return json.dumps(response)
   elif request.method == 'GET':
      try:
         cur.execute("""\
            SELECT
               U.userId,
               U.firstName,
               U.lastName,
               U.username,
               U.dateOfBirth,
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
               AND U.deleted = FALSE""", (request.headers['authentication'],)
         )
      except MySQLError:
         response['message'] = 'Internal Server Error.'
         response['status_code'] = 500
         return json.dumps(response)

      row = cur.fetchone()
      if row is None:
         return "No data."

      data['userId'] = row[0]
      data['firstName'] = row[1]
      data['lastName'] = row[2]
      data['username'] = row[3]
      data['birthday'] = row[4].isoformat()
      data['bio'] = row[5]
      data['gender'] = row[6]
      data['schoolId'] = row[7]
      data['majorId'] = row[8]
      data['year'] = row[9]
      data['verifiedTutor'] = row[10]
      data['school'] = row[11]
      data['major'] = row[12]
      data['majorAbbreviation'] = row[13]
      
      # Clear any excess data. 
      cur.fetchall()

   db.commit()
   return json.dumps(data)

@app.route("/account/", methods = ['GET', 'POST'])
def account():
   data = {}
   response = {}

   try:
      if validateToken(request.headers['authentication']) == False:
         response['message'] = "Invalid token."
         response['status_code'] = 403
         return json.dumps(response)

      if not validAccountT(request.headers['authentication']):
         response['message'] = 'Account not verified.'
         response['status_code'] = 401
         return json.dumps(response) 
   except MySQLError:
      response['message'] = 'Internal Server Error.'
      response['status_code'] = 500
      return json.dumps(response)
      
   if request.method == 'POST':
      try:
         hashedpw = getPasswordT(request.headers['authentication'])
         if hashedpw is None:
            response['message'] = 'Internal Server Error.'
            response['status_code'] = 500
            return json.dumps(response) 
         hashedpw = hashedpw.encode('utf-8')

         if not validAccountT(request.headers['authentication']):
            response['message'] = 'Account not verified.'
            response['status_code'] = 401
            return json.dumps(response) 

         if hashedpw == bcrypt.hashpw(request.form['password'].encode('utf-8'), hashedpw):
            newPass = bcrypt.hashpw(request.form['newPassword'].encode('utf-8'), bcrypt.gensalt())

            cur.execute("""\
               UPDATE
                  Users AS U
                  INNER JOIN Tokens AS T ON U.userId = T.user
               SET
                  U.username = %s,
                  U.email = %s,
                  U.phone = %s,
                  U.password = %s
               WHERE
                  T.token = %s""",
               (request.form['username'], request.form['email'],
               request.form['phone'], newPass, request.headers['authentication'],)
            )
            db.commit()
         else:
            response['message'] = 'Invalid password.'
            response['status_code'] = 401
            return json.dumps(response) 

         response['message'] = 'OK.'
         response['status_code'] = 200
         return json.dumps(response)
      except IntegrityError:
         response['message'] = 'Username or email already taken.'
         response['status_code'] = 400
         return json.dumps(response)
      except MySQLError as e:
         response['message'] = 'Internal Server Error.'
         response['status_code'] = 500
         return json.dumps(response)
   elif request.method == 'GET':
      try:
         cur.execute("""\
            SELECT
               U.username,
               U.email,
               U.phone
            FROM
               Tokens AS T
               INNER JOIN Users AS U ON T.user = U.userId
            WHERE
               T.token = %s
               AND U.deleted = FALSE""", (request.headers['authentication'],)
         )
      except MySQLError:
         response['message'] = 'Internal Server Error.'
         response['status_code'] = 500
         return json.dumps(response)

      row = cur.fetchone()
      if row is None:
         return json.dumps({})

      data['username'] = row[0]
      data['email'] = row[1]
      data['phone'] = row[2]

      # Clear any excess data. 
      cur.fetchall()

   db.commit()
   return json.dumps(data)

@app.route("/posts/matched/")
def getMatchedPosts():
   data = []
   response = {}
   
   try:
      if validateToken(request.headers['authentication']) == False:
         response['message'] = "Invalid token."
         response['status_code'] = 403
         return json.dumps(response)

      if not validAccountT(request.headers['authentication']):
         response['message'] = 'Account not verified.'
         response['status_code'] = 401
         return json.dumps(response) 

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
            AND (P.tutor IS NULL OR P.tutor = 0)""",
      (request.headers['authentication'], request.headers['authentication'],));
      db.commit()
   except MySQLError:
      response['message'] = 'Internal Server Error.'
      response['status_code'] = 500
      return json.dumps(response)
   
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

@app.route("/posts/")
def getUserPosts():
   data = []
   response = {}

   try:
      if validateToken(request.headers['authentication']) == False:
         response['message'] = "Invalid token."
         response['status_code'] = 403
         return json.dumps(response)

      if not validAccountT(request.headers['authentication']):
         response['message'] = 'Account not verified.'
         response['status_code'] = 401
         return json.dumps(response) 

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
            AND P.resolved <> 1""", (request.headers['authentication'],)
      );
      db.commit()
   except MySQLError:
      response['message'] = 'Internal Server Error.'
      response['status_code'] = 500
      return json.dumps(response)
   
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

@app.route("/posts/helped/")
def getUserHelpedPosts():
   data = []
   response = {}

   try:
      if validateToken(request.headers['authentication']) == False:
         response['message'] = "Invalid token."
         response['status_code'] = 403
         return json.dumps(response)

      if not validAccountT(request.headers['authentication']):
         response['message'] = 'Account not verified.'
         response['status_code'] = 401
         return json.dumps(response) 

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
            AND P.deleted = FALSE""", (request.headers['authentication'],)
      );
      db.commit()
   except MySQLError:
      response['message'] = 'Internal Server Error.'
      response['status_code'] = 500
      return json.dumps(response)

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

@app.route("/posts/helping/")
def getUserHelpingPosts():
   data = []
   response = {}

   try:
      if validateToken(request.headers['authentication']) == False:
         response['message'] = "Invalid token."
         response['status_code'] = 403
         return json.dumps(response)

      if not validAccountT(request.headers['authentication']):
         response['message'] = 'Account not verified.'
         response['status_code'] = 401
         return json.dumps(response) 

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
            AND P.deleted = FALSE""", (request.headers['authentication'],)
      );
      db.commit()
   except MySQLError:
      response['message'] = 'Internal Server Error.'
      response['status_code'] = 500
      return json.dumps(response)

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
   response = {}
   
   try:
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
   except MySQLError:
      response['message'] = 'Internal Server Error.'
      response['status_code'] = 500
      return json.dumps(response)

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

@app.route("/classes/<int:schoolId>")
def getClasses(schoolId):
   data = []
   response = {}

   try:
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
      )
   except MySQLError:
      response['message'] = 'Internal Server Error.'
      response['status_code'] = 500
      return json.dumps(response)

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

      try:
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
      except MySQLError:
         response['message'] = 'Internal Server Error.'
         response['status_code'] = 500
         return json.dumps(response)

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

@app.route("/messages/<int:postId>")
def PostMessages(postId):
   data = []
   response = {}

   try:
      if validateToken(request.headers['authentication']) == False:
         response['message'] = "Invalid token."
         response['status_code'] = 403
         return json.dumps(response)

      cur.execute("""\
         SELECT %s
         IN (
            SELECT token
            FROM
               PostMessages AS PM
               INNER JOIN Messages AS M ON PM.message = M.messageId
               INNER JOIN Users AS U ON M.user = U.userId
               INNER JOIN Tokens AS T ON U.userId = T.user
            WHERE
               PM.post = %s
         )""", (request.headers['authentication'], postId)
      )
      col = cur.fetchone()
      if col[0] == 0:
         response['message'] = 'Forbidden'
         response['status_code'] = 403
         return json.dumps(response)

      cur.execute("""\
         SELECT
            P.postId,
            M.messageId,
            M.content,
            M.postDate,
            U.username,
            U.firstName,
            U.lastName
         FROM 
            PostMessages AS PM 
            INNER JOIN Posts P ON PM.post = P.postId
            INNER JOIN Messages M ON PM.message = M.messageId
            INNER JOIN Users AS U ON M.user = U.userId
         WHERE PM.post = %s""", (postId,)
      )
   except MySQLError:
      response['message'] = 'Internal Server Error.'
      response['status_code'] = 500
      return json.dumps(response)

   rows = cur.fetchall()
   if rows is None:
      return "No data."
   
   for row in rows :
      obj = {}
      obj['postId'] = row[0]
      obj['messageId'] = row[1]
      obj['content'] = row[2]
      obj['postDate'] = row[3].isoformat()
      obj['username'] = row[4]
      obj['firstName'] = row[5]
      obj['lastName'] = row[6]
      data.append(obj)

   return json.dumps(data)

if __name__ == "__main__":
   app.debug = True
   app.run()
