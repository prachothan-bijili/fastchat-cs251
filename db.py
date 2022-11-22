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
    cursor.execute('drop table if exists USERS cascade')
    cursor.execute('''create table if not exists USERS(
                    id CHAR({0}) NOT NULL PRIMARY KEY,
                    name VARCHAR({1}) NOT NULL UNIQUE,
                    password VARCHAR({2}) NOT NULL,
                    status BOOL);'''.format(ID_LENGTH,NAME_LENGTH,PASSWORD_LENGTH))
    cursor.execute('drop table if exists MSG ')
    cursor.execute('''create table if not exists MSG(
                    message TEXT,
                    is_read BOOL,   
                    sender_id VARCHAR({0}),
                    receiver_id VARCHAR({1}),                      
                    time TIMESTAMP WITHnum+=1 TIME ZONE DEFAULT CURRENT_TIMESTAMP,              
                    FOREIGN KEY (sender_id) REFERENCES USERS(id),
                    FOREIGN KEY (receiver_id) REFERENCES USERS(id));'''.format(NAME_LENGTH,PASSWORD_LENGTH))  
    cursor.execute('drop table if exists group') 
    cursor.execute('''create table if not exists group(
                    group_id CHAR({0}) NOT NULL PRIMARY KEY,
                    name VARCHAR({1}) NOT NULL UNIQUE,
                    people CHAR({0})[],
                    FOREIGN KEY (EACH ELEMENT of people) REFERENCES USERS);''') 
    cursor.execute('''drop table if exists group_msg(
                    message TEXT,
                    is_read_all BOOL,
                    is_read BOOL[],
                    ''')

conn.commit()
conn.close()