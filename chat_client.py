import socket
import sys
import json
from get_json import json_splitter
import threading
import select
import hashlib
from encryp import *



class Client:
    """
    | Client of Client-Server Program connected via sockets, allowing clients to send or read messages personally or through groups
    """

    def __init__(self):
        """
        | Constructor method
        """
        
        self.host = "127.0.0.1"
        # port to ask which port to connect to
        self.superport = 6000
        self.super_server_address = (self.host, self.superport)
        # ports that each server will be binded to
        self.port = [60000,50000,40000,30000,20000]
        self.server_address = [(self.host, self.port[0]),(self.host, self.port[1]),(self.host, self.port[2]),(self.host, self.port[3]),(self.host, self.port[4])]
        # name of current user
        self.usr_nam = ''
        # id of current user
        self.user_id = ''
        # private key of the current user
        self.private_key = 0
        # maps user ids to their names
        self.all_memb = {}
        # maps users ids to their public keys
        self.all_pubkeys = {}
        # maps group names to groups ids in which current user is in
        self.all_groups = {}
        # maps group ids to group members in the groups current user is in
        self.group_members = {}
        # list of users and their status(Online/Offline)
        self.userlist = []
        self.is_update_userlist = False
        # size of string to receive from server
        self.BUFFER_SIZE = 40000
        # Create a TCP/IP socket           
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

    def listener(self, recv_sock):    
        """
        | Listens to any data from servers

        :param recv_sock: socket that is connected to the server 
        :type recv_sock: socket
        """
        
        inputs = [recv_sock]
        while inputs:        
            readable, writable, exceptional = select.select(inputs,[], inputs)             
            for s in readable:            
                if s is recv_sock:
                    try:                   
                        # data received from server
                        data = s.recv(self.BUFFER_SIZE)     
                        if data:                
                            # decode from bytes to utf-8
                            jsonstr = data.decode()              
                            # splits string into jsons as server sends with multiple jsons in one string              
                            for jsonobj in json_splitter(jsonstr):
                                # info is used to mention what kind of data sent by server
                                info = json.loads(jsonobj) 
                                # new user has joined
                                if info["info-type"] == "new_user" or info["info-type"] == "old_user":                                                                
                                    self.all_memb[info["id"]] = info["name"].upper()
                                    self.all_pubkeys[info["id"]] = info["public_key"]
                                    print("=> {0} joined the server".format(info["name"]))
                                # close connection
                                elif info["info-type"] == "kill":                                
                                    return
                                # receive notifications that user has received when he/she has gone offline
                                elif(info["info-type"] == "Notifications"):                        
                                    unread = info["unread"]
                                    grp_unread = info["grp-unread"]
                                    memblist =  info["list"]                  
                                    new_group = info["new_group"]     
                                    group_list = info["group_list"]    
                                    new_group_list = info["new_group_list"]
                                    for entry in new_group_list:
                                        self.group_members[entry[0]] = []
                                        for memb_id in entry[1]:
                                            self.group_members[entry[0]].append(memb_id[0])             
                                    if(len(memblist) == 1):
                                        print("No users on the server")                                    
                                        self.user_id = memblist[0][1]
                                    else:
                                        print("Users:")
                                        num = 0 
                                        p = []
                                        for pair in memblist:
                                            if not pair[0] == self.usr_nam.upper():
                                                num+=1
                                                if pair[2]:
                                                    print("     {0}. {1} -> Online".format(num, pair[0]))
                                                else:
                                                    print("     {0}. {1} -> Offline".format(num, pair[0]))
                                                self.all_memb[pair[1]] = pair[0]
                                                self.all_pubkeys[pair[1]] = pair[3]
                                            else:
                                                p = pair
                                        self.user_id = p[1]
                                        memblist.remove(p)  
                                    if group_list != []:
                                        print("Groups:")
                                        num = 0
                                        for grp in group_list:
                                            num+=1
                                            print("     {0}. {1}".format(num,grp[0]))
                                            self.all_groups[grp[1]] = grp[0]
                                    if unread != []:
                                        print("Notifications:")
                                        for i in unread:                                                      
                                            i[1] = decrypt(i[1], self.private_key)                
                                            print("     {0} sent {1} ".format(self.all_memb[i[0]],i[1]))
                                    if new_group != [] or grp_unread != []:
                                        print("Group Notifications:")
                                        for j in new_group:
                                            print("     {0} added you to the group {1}".format(self.all_memb[j[1]],j[0]))                                     
                                        for k in grp_unread:
                                            k[1] = decrypt(k[1], self.private_key)
                                            print("     {0} sent {1} in the group {2}".format(self.all_memb[k[0]],k[1], self.all_groups[k[2]]))
                                elif(info["info-type"] == "get-users"):
                                    num=0                                
                                    if(len(info["list"]) != 1):                                                 
                                        temp = []                 
                                        for i in info["list"]:
                                            if not i[0] == self.usr_nam.upper():
                                                num+=1
                                                print("{0}. {1}".format(num,i[0]))            
                                            else:
                                                temp = i                            
                                        self.userlist = info["list"]
                                        self.userlist.remove(temp)
                                    self.is_update_userlist = True                                    

                                elif(info["info-type"] == "inst-msg"):     
                                    info["text"] = decrypt(info["text"], self.private_key)
                                    print("=>", self.all_memb[info["sender"]]," sent ",info["text"])

                                elif(info["info-type"] == "group_added"):
                                    self.all_groups[info["group_id"]] = info["group_name"]           
                                    self.group_members[info["group_id"]] = info["group_members"]                     
                                    if(info["admin"] != self.user_id):
                                        print("=> {0} added you to the group {1}".format(self.all_memb[info["admin"]],info["group_name"]))
                                
                                elif(info["info-type"] == "grp-inst-msg"):
                                    if(info["sender"] != self.user_id):
                                        info["text"] = decrypt(info["text"], self.private_key)
                                        print("=>", self.all_memb[info["sender"]],"sent", info["text"] ,"in the group",self.all_groups[info["group_id"]])
                            
                    except KeyboardInterrupt:
                        print("closing connection")  
                        return
                    
    def refresh(self, refr):
        """
        | Refreshes the chat page

        :param refr: socket that is connected to the server 
        :type refr: socket
        """
        
        info = {"info-type": "start_notifications", "name": self.usr_nam.upper()}
        info = json.dumps(info)
        try:
            refr.sendall(info.encode())
        except:
            print("connection lost!")
            refr.close()
            sys.exit(1)

    def authenticator(self):
        """
        | Allow user to either login or signup
        """

        # global usr_nam
        # global private_key    
        while True:
            choice =input("Enter 1 to login OR Enter 2 to sign up: ")
            try:
                choice = int(choice)
                if choice not in [1,2]:
                    print("invalid entry!")
                    continue
            except:
                print("invalid entry!")
                continue
            if choice == 1:
                user_name = input("Enter your username: ")
                password = input("Enter password: ")
                saltedPass = user_name.upper()+password
                password = hashlib.sha256(str.encode(saltedPass)).hexdigest()
                info={"info-type":"login", "name":user_name,"password":password}       
                try:
                    self.sock.sendall(json.dumps(info).encode())
                    is_succ = self.sock.recv(self.BUFFER_SIZE).decode()
                except:
                    print('Cannot login currently! please try again later')
                    sys.exit(1)            
                if(is_succ == "1"):
                    self.usr_nam = user_name
                    self.private_key = loadPrivateKey(user_name)
                    if(self.private_key is None):
                        print("private key lost")
                        exit()
                    print("login successfull!\n")
                    return
                else:
                    print("incorrect username or password!")
            elif choice == 2:
                name = input("Enter your username: ")
                if name == "":
                    print("Enter a valid username")
                    continue
                password = input("Create a password: ")
                if password == "":
                    print("Enter a valid password")
                    continue
                
                new_public_key, new_private_key = rsa.newkeys(1024)
                pubkey = str(new_public_key)

                saltedPass = name.upper()+password
                password = hashlib.sha256(str.encode(saltedPass)).hexdigest()
                info = {"info-type":"signup", "name":name,"password":password, "public_key":pubkey}
                try:
                    self.sock.sendall(json.dumps(info).encode())
                    is_succ = self.sock.recv(self.BUFFER_SIZE).decode()
                except:
                    print('Cannot sing up currently! please try again later')
                    sys.exit(1)
                
                if(is_succ == "1"):
                    self.usr_nam = name
                    storePrivateKey(name, new_private_key)
                    self.private_key = new_private_key
                    print("successfully created an account\n")
                    return
                else:
                    print("Username already taken. please choose another username")
            else:
                continue    
    
    
    def run_client(self):     
        """
        | Connects to server having minimum no of clients connected to it, authenticates the user and allow user to send message, create groups
        """

        try:          
            self.sock.connect(self.super_server_address)
            print("connected to port {0}".format(self.superport))
            con=json.dumps({"info-type":"add-connection"})
            try:
                self.sock.sendall(con.encode())
                port_to_connect = int(self.sock.recv(4000).decode())
                self.sock.close()
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.host, port_to_connect))
                print("connected to port {0}".format(port_to_connect))
            except:
                print('Cannot connect to the superserver!') 
                sys.exit(1)  
        except:
            print('Cannot connect to the server!') 
            sys.exit(1)  



        try:
            self.authenticator()
            thread = threading.Thread(target=self.listener, args=(self.sock,))
            thread.start()
        except KeyboardInterrupt:
            sys.exit(1)
        
        try:
            self.refresh(self.sock)            
            print("!-----------------------------------------------------------------------------!")
            print(" r to refresh q to quit c to create group s to send message sg to send grp msg")
            print("!-----------------------------------------------------------------------------!\n")
            
            while True:        
                user_enrty = input()                                                          
                if(user_enrty=="r"):
                    self.refresh(self.sock)
                    continue
                elif(user_enrty=="q"):
                    kill_thread = {"info-type":"kill_thread"}
                    kill_thread = json.dumps(kill_thread)
                    self.sock.sendall(kill_thread.encode())                       
                    thread.join()
                    self.sock.close() 
                    break
                elif(user_enrty=="c"):                          
                    curr_usr = self.user_id
                    allusers = {"info-type":"get-users"}
                    allusers = json.dumps(allusers)            
                    self.sock.sendall(allusers.encode())
                    while not self.is_update_userlist:
                        continue
                    self.is_update_userlist = False
                    if(len(self.userlist) == 0):
                        print("No people on the serve")
                        continue
                    else:                  
                        print("enter group name")              
                        grp_name = input() 
                        memb = [self.user_id]                 
                        while True:
                            print("select member or enter e to end")
                            memb_select = input()
                            if(memb_select == "e"):
                                break
                            try:
                                memb_select = int(memb_select)
                                if self.userlist[memb_select-1][1] not in memb:
                                    memb.append(self.userlist[memb_select-1][1])
                                else:
                                    print("user already added")
                            except:
                                print("invalid input")
                        
                        new_grp_info = {"info-type":"create-grp","group-name":grp_name,"admin":curr_usr, "members":memb}
                        new_grp_info = json.dumps(new_grp_info)
                        if len(memb) > 1:
                            self.sock.sendall(new_grp_info.encode()) 
                            print("Successfully created the group")
                elif(user_enrty=="s"):
                    sent_succ = (len(self.all_memb) == 0)
                    if sent_succ:
                        print("no users on the server")
                    while not sent_succ:
                        print("enter user name")
                        friend_name = input().upper()
                        if friend_name not in self.all_memb.values():
                            print("user does not exists")
                            break
                        else:
                            friend_id = ''                    
                            friend_pubkey = 0
                            for key, value in self.all_memb.items():
                                if friend_name == value:
                                    friend_id = key
                                    break
                            friend_pubkey = self.all_pubkeys[friend_id]
                            print("enter meassage")
                            message = input()
                            message = encrypt(message, friend_pubkey)

                            msg_info = {"info-type":"send-message","text":message,"receiver":friend_id}
                            msg_info = json.dumps(msg_info)
                            self.sock.sendall(msg_info.encode())        
                            print("sent successfully")            
                            break
                elif user_enrty == "sg":
                    grp_sent_succ = (len(self.all_groups) == 0)
                    if grp_sent_succ:
                        print("no groups on the server")
                    while not grp_sent_succ:
                        print("enter group name")
                        group_name = input()
                        if group_name not in self.all_groups.values():
                            print("group does not exist")
                            break
                        else:
                            group_id = ''
                            for key, values in self.all_groups.items():
                                if group_name == values:
                                    group_id = key
                            print("enter message")
                            message = input()                            
                            for friend_id in self.group_members[group_id]: 
                                if friend_id != self.user_id:                                                           
                                    enc_msg = encrypt(message, self.all_pubkeys[friend_id])
                                    msg_info = {"info-type":"group-message","text":enc_msg,"receiver":friend_id,"group_id":group_id}
                                    msg_info = json.dumps(msg_info)
                                    self.sock.sendall(msg_info.encode())
                            print("sent successfully")
                            break            
                else:
                    print("invalid input")
                    continue                           
                
        except : 
            try : 
                kill_thread = {"info-type":"kill_thread"}
                kill_thread = json.dumps(kill_thread)
                self.sock.sendall(kill_thread.encode()) 
            except:
                print("server down")
                self.sock.close()
                sys.exit(1)                      
            thread.join()
            self.sock.close()

if __name__ == "__main__":
    client = Client()
    client.run_client()