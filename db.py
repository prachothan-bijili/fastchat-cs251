#!/usr/bin/python
import psycopg2
import sys

ID_LENGTH = 7
NAME_LENGTH = 20
PASSWORD_LENGTH = 20

try: 
    conn = psycopg2.connect("dbname=fastchatdb user=fastchat password=codebrewers")
    print("connection successful")
except psycopg2.DatabaseError as e:
    print('Error code {}: {}'.format(e.pgcode, e))    
    print("Cannot connect to the database")
    sys.exit(1)

with conn.cursor() as cursor:
    cursor.execute('drop table if exists USERS')
    cursor.execute('''create table if not exists USERS(
                    id VARCHAR(20) NOT NULL PRIMARY KEY,
                    name VARCHAR(20) NOT NULL UNIQUE,
                    password VARCHAR(20) NOT NULL,
                    status BOOL)''')
    cursor.execute('drop table if exists MSG')
    cursor.execute('''create table if not exists MSG(
                    message TEXT,
                    is_read BOOL,   
                    sender_id VARCHAR(20),
                    receiver_id VARCHAR(20),                                    
                    FOREIGN KEY (sender_id) REFERENCES USERS(id),
                    FOREIGN KEY (receiver_id) REFERENCES USERS(id))''')

conn.commit()
conn.close()