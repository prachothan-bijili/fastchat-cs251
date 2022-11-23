import select
import socket
import sys
import queue
import sqlite3
import json
import random

host="127.0.0.1"
port = 65432

def generateID():
    id = ''
    while True:
        for i in range(7):
            r = random.choice([1, 2, 3])
            if r == 1:
                id += chr(random.randint(65, 90))
            elif r == 2:
                id += chr(random.randint(97, 122))
            else:
                id += str(random.randint(0,9))   
        cursor.execute('''select id from USERS '''. format(id))         
        l = cursor.fetchall()
        #print(l)
        is_pre = False
        for i in l:
            if i[0] == id:
                is_pre = True
                break
        if is_pre:
            continue
        else:
            return id

def checkname(name,password,is_log):          
    cursor.execute('''select name,password from USERS '''.format(name))    
    l = cursor.fetchall()
    #print(l)
    for pair in l:
        if pair[0] == name.upper():
            if (not is_log) or pair[1] == password:
                return True
            else:
                break
    return False

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)


server_address = (host,port)
try:
    server.bind(server_address)
    print ('starting up on %s port %s' % server_address)
except :
    print("Port is busy")
    sys.exit(1)

server.listen(5)

try:
    conn = sqlite3.connect("fastchat.db")    
    cursor = conn.cursor()
    print("connection successful")
except sqlite3.DatabaseError as e:
    print('Error code {}: {}'.format(e.pgcode, e))    
    print("Cannot connect to the database")
    sys.exit(1)
        
                                                         
inputs = [ server ]
id_dict = {}

try:
    while inputs:
        
        # Wait for at least one of the sockets to be ready for processing     
        readable, writable, exceptional = select.select(inputs,[], inputs)
        print(1)
        # Handle inputs
        for s in readable:
            print(2)
            if s is server:               
                # A "readable" server socket is ready to accept a connection
                connection, client_address = s.accept()
                print ('new connection from', client_address)
                connection.setblocking(0)
                inputs.append(connection)                
            else:                
                data = s.recv(1024)

                if data:
                    info = data.decode()
                    info = json.loads(info)
                    if(info["info-type"] == "login"):
                        if not checkname(info["name"],info["password"],1):
                            is_succ = "0"
                            s.send(is_succ.encode())
                        else:
                            cursor.execute('''update USERS set status = true where name='{0}';'''.format(info["name"].upper()))
                            cursor.execute('''select id from USERS where name='{0}';'''.format(info["name"].upper()))
                            l = cursor.fetchall()
                            id_dict[s] = l[0][0]
                            is_succ = "1"
                            s.send(is_succ.encode())
                    if(info["info-type"] == "signup"):
                        if checkname(info["name"],"",0):
                            is_succ = "0"
                            s.send(is_succ.encode())                            
                        else:                            
                            id = generateID()       
                            id_dict[s] = id             
                            print(info["public_key"])
                            type(info["public_key"])                                                                                         
                            cursor.execute(''' INSERT INTO USERS VALUES (
                                            '{0}','{1}','{2}','{3}',true);'''.format(id,info["name"].upper(),info["password"],info["public_key"]))
                            cursor.execute('''select * from USERS;''')                            
                            is_succ = "1"
                            s.send(is_succ.encode())
                    if(info["info-type"] == "online"):
                        cursor.execute(''' select name,id,public_key from USERS where status=true;''')
                        l = cursor.fetchall()
                        data = {"list":l}
                        data = json.dumps(data)
                        s.sendall(data.encode())
                    if(info["info-type"] == "message"):
                        cursor.execute(''' INSERT INTO MSG VALUES 
                                        ('{0}',false,'{1}','{2}');'''.format(info["text"],id_dict[s],info["receiver"]))                          
                    if(info["info-type"] == "unread"):
                        cursor.execute('''select message,sender_id from MSG where receiver_id='{0}';'''.format(id_dict[s]))
                        list_of_msg = cursor.fetchall()
                        list_of_msg = {"msgList":list_of_msg}
                        list_of_msg = json.dumps(list_of_msg)
                        s.send(list_of_msg.encode())                    
                else:
                    # Interpret empty result as closed connection                    
                    # Stop listening for input on the connection
                    cursor.execute(''' update USERS set status=false where id='{0}';'''.format(id_dict[s]))                                        
                    inputs.remove(s)
                    s.close() 
                    print('closing', client_address, 'after reading no data')
                    del id_dict[s]        
        # Handle "exceptional conditions"
        for s in exceptional:
            print ('handling exceptional condition for', s.getpeername())
            # Stop listening for input on the connection
            inputs.remove(s)            
            s.close()
            
except KeyboardInterrupt:
    server.close()             
    conn.close()
    
