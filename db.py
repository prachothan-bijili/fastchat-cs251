#!/usr/bin/python
import psycopg2
import sys
import sqlite3

ID_LENGTH = 7
NAME_LENGTH = 20
PASSWORD_LENGTH = 20
PUBLIC_KEY_LENGTH = 1024

try: 
    conn = sqlite3.connect('fastchat.db')
    print("connection successful")
except psycopg2.DatabaseError as e:
    print('Error code {}: {}'.format(e.pgcode, e))    
    print("Cannot connect to the database")
    sys.exit(1)

with conn as cursor: 
    cursor.execute('drop table if exists USERS')
    cursor.execute('''create table if not exists USERS(
                    id CHAR({0}) NOT NULL PRIMARY KEY,
                    name VARCHAR({1}) NOT NULL UNIQUE,
                    password VARCHAR({2}) NOT NULL,
                    public_key CHAR({3}) NOT NULL UNIQUE,
                    status BOOL);'''.format(ID_LENGTH,NAME_LENGTH,PASSWORD_LENGTH,PUBLIC_KEY_LENGTH))
    cursor.execute('drop table if exists MSG ')
    cursor.execute('''create table if not exists MSG(
                    message TEXT,
                    is_read BOOL,   
                    sender_id VARCHAR({0}),
                    receiver_id VARCHAR({1}),                      
                    FOREIGN KEY (sender_id) REFERENCES USERS(id),
                    FOREIGN KEY (receiver_id) REFERENCES USERS(id));'''.format(NAME_LENGTH,PASSWORD_LENGTH))  


conn.commit()
conn.close()