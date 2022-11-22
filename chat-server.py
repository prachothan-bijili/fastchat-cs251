import select
import socket
import sys
import queue
import psycopg2
import json
import random

host="127.0.0.1"
port = 65432
# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)

# Bind the socket to the port
server_address = (host,port)
print ('starting up on %s port %s' % server_address)
try:
    server.bind(server_address)
except :
    print("Port is busy")
    sys.exit(1)

# Listen for incoming connections
server.listen(5)

try:
    conn = psycopg2.connect("dbname=fastchatdb user=fastchat password=codebrewers")    
    cursor = conn.cursor()
    print("connection successful")
except psycopg2.DatabaseError as e:
    print('Error code {}: {}'.format(e.pgcode, e))    
    print("Cannot connect to the database")
    sys.exit(1)

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
                                                                  
        

# Sockets from which we expect to read
inputs = [ server ]

# Sockets to which we expect to write
outputs = [ ]

# Outgoing message queues (socket:Queue)
message_queues = {}

#map of socket with user id's
id_dict = {}

try:
    while inputs:

        # Wait for at least one of the sockets to be ready for processing     
        readable, writable, exceptional = select.select(inputs, outputs, inputs)

        # Handle inputs
        for s in readable:

            if s is server:
                # A "readable" server socket is ready to accept a connection
                connection, client_address = s.accept()
                print ('new connection from', client_address)
                connection.setblocking(0)
                inputs.append(connection)

                # Give the connection a queue for data we want to send
                message_queues[connection] = queue.Queue()
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
                            cursor.execute('''update USERS
                                        set status = True
                                        where name='{0}';'''.format(info["name"]))
                            is_succ = "1"
                            s.send(is_succ.encode())
                    if(info["info-type"] == "signup"):
                        if checkname(info["name"],"",0):
                            is_succ = "0"
                            s.send(is_succ.encode())
                            #print('hii')
                        else:
                            #print('bye')
                            id = generateID()       
                            id_dict[s] = id                                                                                                      
                            cursor.execute(''' INSERT INTO USERS VALUES (
                                            '{0}','{1}','{2}',True);'''.format(id,info["name"].upper(),info["password"]))
                            cursor.execute('''select * from USERS;''')
                            #print(cursor.fetchall())
                            is_succ = "1"
                            s.send(is_succ.encode())
                    if(info["info-type"] == "online"):
                        cursor.execute(''' select name,id from USERS where status=True;''')
                        l = cursor.fetchall()
                        data = {"list":l}
                        data = json.dumps(data)
                        s.sendall(data.encode())
                    if(info["info-type"] == "message"):
                        cursor.execute(''' insert into MSG values
                                        ('{0}',False,'{1}','{2}');'''.format(info["text"],id_dict[s],info["receiver"]))                          
                    if(info["info-type"] == "unread"):
                        cursor.execute('''select message,sender_id from MSG where receiver_id = '{0}';'''.format(id_dict[s]))
                        list_of_msg = cursor.fetchall()
                        list_of_msg = {"msgList":list_of_msg}
                        list_of_msg = json.dumps(list_of_msg)
                        s.send(list_of_msg.encode())
                    # Add output channel for response
                    if s not in outputs:
                        outputs.append(s)
                else:
                    # Interpret empty result as closed connection
                    print('closing', client_address, 'after reading no data')
                    # Stop listening for input on the connection
                    cursor.execute(''' update USERS set status = False where id='{0}';'''.format(id_dict[s]))
                    if s in outputs:
                        outputs.remove(s)
                    inputs.remove(s)
                    s.close()
                    
        # Handle outputs
        for s in writable:
            try:
                next_msg = message_queues[s].get_nowait()
            except queue.Empty:
                # No messages waiting so stop checking for writability.
                print ('output queue for', s.getpeername(), 'is empty')
                outputs.remove(s)
            else:
                print('sending "%s" to %s' % (next_msg, s.getpeername()))
                s.send(next_msg)    
        # Handle "exceptional conditions"
        for s in exceptional:
            print ('handling exceptional condition for', s.getpeername())
            # Stop listening for input on the connection
            inputs.remove(s)
            if s in outputs:
                outputs.remove(s)
            s.close()
            
except KeyboardInterrupt:
    server.close()             
    conn.close()
    
