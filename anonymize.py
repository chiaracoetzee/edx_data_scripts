#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb
import hashlib
import os
import random
import re
import string
import sys

def get_connection(database_name):
    return MySQLdb.connect('localhost', 'root', password, database_name)

def get_databases(con):
    cur = con.cursor()
    cur.execute("SHOW DATABASES")
    return [row[0] for row in cur.fetchall()]

def get_tables(db):
    con = get_connection(db)
    cur = con.cursor()
    cur.execute("SHOW TABLES")
    return [row[0] for row in cur.fetchall()]

def anonymize_value(value):
    m = hashlib.sha1()
    m.update(salt)
    m.update(value)
    return m.hexdigest()

def anonymize_field(con, table, primary_key, field, new_field):
    print("  Anonymizing field " + table + "." + field + "...")
    cur = con.cursor()
    cur.execute("ALTER TABLE " + table + " ADD `" + new_field + "` char(" + str(hash_length) + ")")
    cur.execute("SELECT `" + primary_key + "`,`" + field + "` FROM `" + table + "`")
    for row in cur.fetchall():
        cur.execute("UPDATE `" + table + "` " + \
                    "   SET `" + new_field + "`='" + anonymize_value(str(row[1])) + "' " + \
                    " WHERE `" + primary_key + "`=" + str(row[0]))
    if primary_key == field:
        cur.execute("ALTER TABLE " + table + " DROP PRIMARY KEY")
        cur.execute("ALTER TABLE " + table + " ADD PRIMARY KEY (`" + new_field + "`)")
    cur.execute("ALTER TABLE " + table + " DROP COLUMN `" + field + "`")

def drop_fields(con, table, fields):
    print("  Dropping fields from " + table + ": " + str(fields) + "...")
    cur = con.cursor()
    for field in fields:
        cur.execute("ALTER TABLE " + table + " DROP COLUMN `" + field + "`")

def reset_salt():
    global salt
    salt = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(20))

def main():
    if len(sys.argv) == 1:
        print("Please specify password of root MySQL account as command-line parameter.")
        sys.exit(0)
    global password
    password = sys.argv[1]
    global hash_length
    hash_length = len(hashlib.sha1().hexdigest())

    con = get_connection('')
    databases = get_databases(con)
    databases = [db for db in databases if 'courseware_studentmodule' in get_tables(db)]
    for db in databases:
        # Reset salt for each database - prevents student correlation between classes
        reset_salt()
        
        print("Database: " + db)
        con = get_connection(db)

        drop_fields(con, 'auth_user', ['username', 'first_name', 'last_name', 'email', 'password', 'date_of_birth'])
        anonymize_field(con, 'auth_user', 'id', 'id', 'anon_id')

        drop_fields(con, 'auth_userprofile', ['name', 'location', 'meta', 'mailing_address'])
        anonymize_field(con, 'auth_userprofile', 'id', 'user_id', 'anon_user_id')

        drop_fields(con, 'certificates_generatedcertificate', ['download_url', 'key', 'verify_uuid', 'download_uuid', 'name'])
        anonymize_field(con, 'certificates_generatedcertificate', 'id', 'user_id', 'anon_user_id')

        anonymize_field(con, 'courseware_studentmodule', 'id', 'student_id', 'anon_student_id')

        anonymize_field(con, 'student_courseenrollment', 'id', 'user_id', 'anon_user_id')

        # Reset salt for each of these so that matching integer values don't produce same hash
        reset_salt()
        anonymize_field(con, 'auth_userprofile', 'id', 'id', 'anon_id')

        reset_salt()
        anonymize_field(con, 'certificates_generatedcertificate', 'id', 'id', 'anon_id')

        reset_salt()
        anonymize_field(con, 'student_courseenrollment', 'id', 'id', 'anon_id')

main()
