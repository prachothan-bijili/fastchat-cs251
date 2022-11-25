#!/usr/bin/python
import psycopg2
import sys

ID_LENGTH = 8
NAME_LENGTH = 20
PASSWORD_LENGTH = 100
PUBLIC_KEY_LENGTH = 1024

try: 
    conn = psycopg2.connect("dbname=fastchatdb user=fastchat password=codebrewers")
    #print("Database connection successful")
except psycopg2.DatabaseError as e:
    print('Error code {}: {}'.format(e.pgcode, e))    
    print("Cannot connect to the database")
    sys.exit(1)

with conn.cursor() as cursor: 
    cursor.execute('drop table if exists USERS cascade')
    cursor.execute('''create table if not exists USERS(
                    id VARCHAR({0}) NOT NULL PRIMARY KEY,
                    name VARCHAR({1}) NOT NULL UNIQUE,
                    password VARCHAR({2}) NOT NULL,
                    public_key VARCHAR({3}) NOT NULL,
                    status BOOL);'''.format(ID_LENGTH,NAME_LENGTH,PASSWORD_LENGTH,PUBLIC_KEY_LENGTH))
    cursor.execute('drop table if exists MSG ')
    cursor.execute('''create table if not exists MSG(
                    message TEXT,
                    is_read BOOL,
                    is_group BOOL,
                    group_id VARCHAR({0}),
                    sender_id VARCHAR({0}),
                    receiver_id VARCHAR({0}),                      
                    time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,                              
                    FOREIGN KEY (sender_id) REFERENCES USERS(id),
                    FOREIGN KEY (receiver_id) REFERENCES USERS(id));'''.format(ID_LENGTH))  
    cursor.execute('drop table if exists grp cascade')  
    cursor.execute('''create table if not exists grp(
                    id VARCHAR({0}) NOT NULL PRIMARY KEY,
                    name VARCHAR({1}) NOT NULL,
                    admin_id VARCHAR({0}) NOT NULL,                    
                    FOREIGN KEY (admin_id) REFERENCES USERS(id));'''.format(ID_LENGTH,NAME_LENGTH)) 
    cursor.execute('drop table if exists grp_memb')
    cursor.execute('''create table if not exists grp_memb(
                    member_id VARCHAR({0}) NOT NULL,
                    group_id VARCHAR({0}) NOT NULL,       
                    is_known BOOL,             
                    FOREIGN KEY (member_id) REFERENCES USERS(id),
                    FOREIGN KEY (group_id) REFERENCES grp(id));'''.format(ID_LENGTH))    
conn.commit()
conn.close()