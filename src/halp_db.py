# File: halp_db.py
# Author: Jon Catanio
# Description: Database connection and cursor declaration.

import MySQLdb

# Connect to the database and setup the db cursor.
db = MySQLdb.connect(host = "localhost",
                     user = "halpTestUser",
                     passwd = "",
                     db = "HalpTest")
cur = db.cursor()
