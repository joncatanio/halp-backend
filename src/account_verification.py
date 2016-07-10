# File: account_verification.py
# Author: Jon Catanio
# Description: Utility functions for account verification and validation.

from halp_db import db, cur
from _mysql_exceptions import MySQLError, IntegrityError
import smtplib
from email.mime.text import MIMEText

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

# Custom Exceptions
class EmailError(Exception):
   def __init__(self, value):
      self.value = value
   def __str__(self):
      return repr(self.value)

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
