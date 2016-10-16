# File: account.py
# Author: Jon Catanio
# Description: Route for user account settings and a users profile.

from halp_db import db, cur
from _mysql_exceptions import MySQLError, IntegrityError
import bcrypt
import json
from user_tokens import validateToken 
from account_verification import validAccountT, getPasswordT
from flask import Blueprint, request

account_api = Blueprint('account_api', __name__)

@account_api.route("/profile/", methods = ['GET', 'POST'])
def profile():
   data = {}
   response = {}

   try:
      if validateToken(request.headers['Authorization']) == False:
         response['message'] = "Invalid token."
         return json.dumps(response), 403

      if not validAccountT(request.headers['Authorization']):
         response['message'] = 'Account not verified.'
         return json.dumps(response), 401 
   except MySQLError:
      response['message'] = 'Internal Server Error.'
      return json.dumps(response), 500
      
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
            request.headers['Authorization'],)
         )
         db.commit()
         
         response['message'] = 'OK.'
         return json.dumps(response), 200
      except MySQLError:
         response['message'] = 'Internal Server Error.'
         return json.dumps(response), 500
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
               AND U.deleted = FALSE""", (request.headers['Authorization'],)
         )
      except MySQLError:
         response['message'] = 'Internal Server Error.'
         return json.dumps(response), 500

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

@account_api.route("/account/", methods = ['GET', 'POST'])
def account():
   data = {}
   response = {}

   try:
      if validateToken(request.headers['Authorization']) == False:
         response['message'] = "Invalid token."
         return json.dumps(response), 403

      if not validAccountT(request.headers['Authorization']):
         response['message'] = 'Account not verified.'
         return json.dumps(response), 401 
   except MySQLError:
      response['message'] = 'Internal Server Error.'
      return json.dumps(response), 500
      
   if request.method == 'POST':
      try:
         hashedpw = getPasswordT(request.headers['Authorization'])
         if hashedpw is None:
            response['message'] = 'Internal Server Error.'
            return json.dumps(response), 500 
         hashedpw = hashedpw.encode('utf-8')

         if not validAccountT(request.headers['Authorization']):
            response['message'] = 'Account not verified.'
            return json.dumps(response), 401 

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
               request.form['phone'], newPass, request.headers['Authorization'],)
            )
            db.commit()
         else:
            response['message'] = 'Invalid password.'
            return json.dumps(response), 401 

         response['message'] = 'OK.'
         return json.dumps(response), 200
      except IntegrityError:
         response['message'] = 'Username or email already taken.'
         return json.dumps(response), 400
      except MySQLError as e:
         response['message'] = 'Internal Server Error.'
         return json.dumps(response), 500
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
               AND U.deleted = FALSE""", (request.headers['Authorization'],)
         )
      except MySQLError:
         response['message'] = 'Internal Server Error.'
         return json.dumps(response), 500

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
