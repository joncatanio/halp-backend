# File: register.py
# Author: Jon Catanio
# Description: Handles user registration and the email token verification.

from halp_db import db, cur
from _mysql_exceptions import MySQLError, IntegrityError
from account_verification import sendEmailVerification
from user_tokens import purgeToken, addToken, validateToken, generateToken
import bcrypt
import json
from flask import Blueprint, request

register_api = Blueprint('register_api', __name__)

@register_api.route("/register", methods = ['POST'])
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
      return json.dumps(response), 400
   except MySQLError:
      response['message'] = 'Internal Server Error.'
      return json.dumps(response), 500

   try:
      token = generateToken()
      addToken(request.form['username'], token)
   except IntegrityError:
      response['message'] = 'Duplicate token.'
      return json.dumps(response), 500
   except MySQLError:
      response['message'] = 'Internal Server Error.'
      return json.dumps(response), 500
  
   try:
      sendEmailVerification(request.form['email'], request.form['firstName'] + ' ' +
                            request.form['lastName'], token)
   except EmailError:
      response['message'] = 'Email verification error.'
      return json.dumps(response), 500
      
   # Commit Users and Tokens table updates.
   db.commit()

   response['message'] = "OK. Pending token validation."
   return json.dumps(response), 201

@register_api.route("/verify/<string:token>")
def verify(token):
   response = {}
   
   try: 
      if validateToken(token) == False:
         response['message'] = "Invalid token."
         return json.dumps(response), 401

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
      return json.dumps(response), 500

   response['message'] = "verified"
   return json.dumps(response), 200
