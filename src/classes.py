# File: classes.py
# Author: Jon Catanio
# Description: Endpoints related to classes and receiving class information.

from halp_db import db, cur
from _mysql_exceptions import MySQLError, IntegrityError
import json
from flask import Blueprint, request

classes_api = Blueprint('classes_api', __name__)

@classes_api.route("/class/<int:classId>")
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

@classes_api.route("/classes/<int:schoolId>")
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
               AND CN.unlisted = FALSE""", [row[0]]
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
