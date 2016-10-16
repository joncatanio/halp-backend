# File: post_messages.py
# Author: Jon Catanio
# Description: Handles all endpoints for messages associated with a user post.

from halp_db import db, cur
from _mysql_exceptions import MySQLError, IntegrityError
from user_tokens import validateToken
import json
from flask import Blueprint, request

post_messages_api = Blueprint('post_messages_api', __name__)

@post_messages_api.route("/messages/<int:postId>")
def PostMessages(postId):
   data = []
   response = {}

   try:
      if validateToken(request.headers['Authorization']) == False:
         response['message'] = "Invalid token."
         return json.dumps(response), 403

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
         )""", (request.headers['Authorization'], postId)
      )
      col = cur.fetchone()
      if col[0] == 0:
         response['message'] = 'Forbidden'
         return json.dumps(response), 403

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
      return json.dumps(response), 500

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

   return json.dumps(data), 200
