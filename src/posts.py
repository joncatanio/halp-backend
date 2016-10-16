# File: posts.py
# Author: Jon Catanio
# Description: Endpoints related to all Halp posts.

from halp_db import db, cur
from _mysql_exceptions import MySQLError, IntegrityError
from account_verification import validAccountT
from user_tokens import validateToken
import json
from flask import Blueprint, request

posts_api = Blueprint('posts_api', __name__)

@posts_api.route("/posts/")
def getUserPosts():
   data = []
   response = {}

   try:
      if validateToken(request.headers['Authorization']) == False:
         response['message'] = "Invalid token."
         response['status_code'] = 403
         return json.dumps(response)

      if not validAccountT(request.headers['Authorization']):
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
            AND P.resolved <> 1""", (request.headers['Authorization'],)
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

@posts_api.route("/posts/matched/")
def getMatchedPosts():
   data = []
   response = {}
   
   try:
      if validateToken(request.headers['Authorization']) == False:
         response['message'] = "Invalid token."
         response['status_code'] = 403
         return json.dumps(response)

      if not validAccountT(request.headers['Authorization']):
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
      (request.headers['Authorization'], request.headers['Authorization'],));
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

@posts_api.route("/posts/helped/")
def getUserHelpedPosts():
   data = []
   response = {}

   try:
      if validateToken(request.headers['Authorization']) == False:
         response['message'] = "Invalid token."
         response['status_code'] = 403
         return json.dumps(response)

      if not validAccountT(request.headers['Authorization']):
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
            AND P.deleted = FALSE""", (request.headers['Authorization'],)
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

@posts_api.route("/posts/helping/")
def getUserHelpingPosts():
   data = []
   response = {}

   try:
      if validateToken(request.headers['Authorization']) == False:
         response['message'] = "Invalid token."
         response['status_code'] = 403
         return json.dumps(response)

      if not validAccountT(request.headers['Authorization']):
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
            AND P.deleted = FALSE""", (request.headers['Authorization'],)
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
