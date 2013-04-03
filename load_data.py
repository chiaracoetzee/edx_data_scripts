#!/usr/bin/python
# -*- coding: utf-8 -*-

# Python script to import .sql dump files from edX (released to partner universities)
# into MySQL. Should be run while working directory contains the .sql files.
# Imports into MySQL server running on localhost using account "root" with password
# provided on command line (modify get_connection() below to change this).
# It will import all classes in the current directory, erasing and recreating any
# existing databases. (Any modifications to these databases will be lost!)
# Tables and their schemas are inferred from the edX documentation at:
# http://data.edx.org/internal_data_formats/sql_schema.html

# All rights released under CC0 Waiver.

# Portions based on http://zetcode.com/db/mysqlpython/
import MySQLdb
import warnings
import sys
import re
import os

# warnings.filterwarnings('ignore', category=MySQLdb.Warning)

def get_connection(database_name):
    return MySQLdb.connect('localhost', 'root', password, database_name)

def database_exists(con, name):
    cur = con.cursor()
    cur.execute("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '" + name + "'")
    return True if cur.rowcount != 0 else False

def recreate_database(con, name):
    cur = con.cursor()
    if database_exists(con, name):
        cur.execute("DROP DATABASE `" + name + "`")
    cur.execute("CREATE DATABASE `" + name + "`")

def ascii_table_to_create_table(table_name, ascii_table_lines):
    result = 'CREATE TABLE `' + table_name + '` (' + "\n"
    key_fields = []
    index_fields = []
    for line in ascii_table_lines:
        m = re.match(r'^\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(\S*)\s*\|\s*(\S*)', line)
        field_name = m.group(1)
        field_type = m.group(2)
        field_not_null = (m.group(3) == 'NO')
        field_primary_key = (m.group(4) == 'PRI')
        field_unique = (m.group(4) == 'UNI')
        field_indexed = (m.group(4) == 'MUL')
        field_auto_increment = (m.group(5) == 'auto_increment')

        if field_primary_key:
            key_fields.append(field_name)
        if field_indexed:
            index_fields.append(field_name)
        result += '  `' + field_name + '` ' + field_type + ' ' + ('NOT NULL' if field_not_null else 'NULL') + (' AUTO_INCREMENT' if field_auto_increment else '') + ",\n"
    result += "  PRIMARY KEY (" + ','.join(['`' + field_name + '`' for field_name in key_fields]) + ")"
    if len(index_fields) > 0:
        result += ",\n  INDEX (" + ','.join(['`' + field_name + '`' for field_name in index_fields]) + ")\n"
    else:
        result += "\n"
    result += ");"
    return result

def load_class(class_name):
    print('Creating database for class ' + class_name + '...');
    recreate_database(get_connection(''), class_name)
    con = get_connection(class_name)

    cur = con.cursor()
    print("   Creating tables...")
    table_list = []
    with open('table_data.txt') as f:
        contents = f.read().split("\n")
        table_state = 0
        ascii_table = []
        for line in contents:
            m = re.match(r"^TABLE (.*)$", line)
            if m:
                table_name = m.group(1)
                table_list.append(table_name)
            if line.startswith('+'):
                table_state = (table_state + 1) % 3
                if table_state == 0:
                    create_table = ascii_table_to_create_table(table_name, ascii_table)
                    cur.execute(create_table)
                    ascii_table = []
            elif table_state == 2:
                ascii_table.append(line)

    cur = con.cursor()
    for table_name in table_list:
        print("   Loading data for table " + table_name + "...")

        # Load file and replace NULL by \N which MySQL expects
        filename = class_name + "-" + table_name + ".sql"
        with open(filename) as f:
            contents_nulls_fixed = f.read().replace('NULL', '\N')
            with open('temp.sql', 'w') as temp:
                temp.write(contents_nulls_fixed)

        cur.execute("LOAD DATA LOCAL INFILE 'temp.sql' INTO TABLE " + table_name + " IGNORE 1 LINES")

        os.remove('temp.sql')

    con.commit()

def main():
    if len(sys.argv) == 1:
        print("Please specify password of root MySQL account as command-line parameter.")
        sys.exit(0)
    global password
    password = sys.argv[1]

    # Get classes by searching for .sql files in current directory
    classes = []
    for f in os.listdir('.'):
        m = re.match('^(.*)-auth_user.sql$', f)
        if m:
            classes.append(m.group(1))

    try:
        for class_name in classes:
            load_class(class_name)
    
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)

main()
