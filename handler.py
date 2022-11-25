import socket
import json
from generator import generateID
from checkname import checkname
from get_json import json_splitter

BUFFER_SIZE = 4000
def handler(s,cursor,id_dict,getPort):
    """
    | handles user inputs, login, signup, create group, send messagem etc and saves data in database

    :param s: socket to which user is connected
    :type s: socket
    :param cursor: object that allows us to access postgresql database
    :type cursor: connection
    :param id_dict: maps sockets to user IDs
    :type id_dict: dictionary
    :param get_Port: Returns Port number having minimum number of clients
    :type get_Port: int

    """
    try:
        data = s.recv(BUFFER_SIZE)   
    except:
        return False 
    
    if data:
        jsonstr = data.decode()    
        for jsonobj in json_splitter(jsonstr):
            info = json.loads(jsonobj)    
            
            if info["info-type"] == "add-connection":
                is_succ = getPort()
                print("Sending port number to client", is_succ)
                s.sendall(str(is_succ).encode())    
                
            elif(info["info-type"] == "login"):
                if not checkname(info["name"],info["password"],1,cursor):
                    is_succ = "0"
                    s.sendall(is_succ.encode())
                else:
                    cursor.execute('''update USERS set status = true where name='{0}';'''.format(info["name"].upper()))
                    cursor.execute('''select id,public_key from USERS where name='{0}';'''.format(info["name"].upper()))
                    l = cursor.fetchall()
                    id_dict[s] = l[0][0]
                    is_succ = "1"
                    s.sendall(is_succ.encode())                    
                    
                    old_usr_log = {"info-type":"old_user","name":info["name"],"id":l[0][0], "public_key":l[0][1]}
                    old_usr_log = json.dumps(old_usr_log)                    
                    for key in id_dict:                        
                        if key != s:                            
                            key.sendall(old_usr_log.encode())
                            
            elif(info["info-type"] == "signup"):
                if checkname(info["name"],"",0,cursor):
                    is_succ = "0"
                    s.sendall(is_succ.encode())                            
                else:                            
                    id = generateID("USERS",cursor)       
                    id_dict[s] = id                                                                                                                  
                    cursor.execute(''' INSERT INTO USERS VALUES (
                                    '{0}','{1}','{2}','{3}',true);'''.format(id,info["name"].upper(),info["password"],info["public_key"]))

                    cursor.execute('''select * from USERS;''')                            
                    is_succ = "1"
                    s.sendall(is_succ.encode()) 

                    new_usr_msg = {"info-type":"new_user","name":info["name"],"id":id, "public_key": info["public_key"]}  
                    new_usr_msg = json.dumps(new_usr_msg)   
                    for key in id_dict: 
                        if key != s: 
                            key.sendall(new_usr_msg.encode())      
                                                  
            elif(info["info-type"] == "start_notifications"):
              
                cursor.execute('''select sender_id,message from MSG where receiver_id ='{0}' and is_read=false and is_group = false; '''.format(id_dict[s]))                                  
                list_of_unread = cursor.fetchall()               
                
                cursor.execute('''select sender_id,message,group_id from MSG where receiver_id = '{0}' and is_read=false and is_group = true;'''.format(id_dict[s]))
                list_of_gp_unread = cursor.fetchall()
                
                cursor.execute('''update MSG set is_read = true where receiver_id = '{0}';'''.format(id_dict[s]))
                list_of_notify = {"info-type":"Notifications","unread":list_of_unread,"grp-unread":list_of_gp_unread}
                
                cursor.execute('''select name,admin_id from grp as A inner join grp_memb as B on B.member_id = '{0}' and B.group_id=A.id and B.is_known=false;'''.format(id_dict[s]))                
                new_grp = cursor.fetchall()
                list_of_notify["new_group"] = new_grp
                
                cursor.execute('''select group_id from grp_memb where member_id = '{0}' and is_known=false;'''.format(id_dict[s]))
                new_grp_id = cursor.fetchall()                
                new_grp_memb_list = []
                for gp_id in new_grp_id:
                    cursor.execute('''select member_id from grp_memb where group_id = '{0}';'''.format(gp_id[0]))
                    memb_list = cursor.fetchall()                   
                    new_grp_memb_list.append((gp_id[0],memb_list))
                
                list_of_notify["new_group_list"] = new_grp_memb_list
                cursor.execute('''update grp_memb set is_known=true where member_id='{0}';'''.format(id_dict[s]))
                cursor.execute(''' select name,id,status,public_key from USERS''')
                l = cursor.fetchall()
                #l = l[:min(10,len(l))]
                list_of_notify["list"] = l                              
                
                cursor.execute('''select name,id from grp as A inner join grp_memb as B on B.member_id = '{0}' and B.group_id=A.id;'''.format(id_dict[s]))                                
                gl = cursor.fetchall()
                list_of_notify["group_list"] = gl
                
                list_of_notify = json.dumps(list_of_notify)
                s.sendall(list_of_notify.encode())

            elif(info["info-type"] == "kill_thread"):
                kill_info = {"info-type":"kill"}
                kill_info = json.dumps(kill_info)
                s.sendall(kill_info.encode())               

            elif(info["info-type"] == "send-message"):
                cursor.execute('''insert into MSG values
                                ('{0}',false,false,NULL,'{1}','{2}');'''.format(info["text"],id_dict[s],info["receiver"]))   
                
                for key, value in id_dict.items():
                    if info["receiver"] == value and key != s:
                        notify = {"info-type":"inst-msg","text":info["text"],"sender":id_dict[s]}
                        notify = json.dumps(notify)
                        cursor.execute('''update MSG set is_read=true where receiver_id ='{0}' and sender_id = '{1}' and is_group=false'''.format(info["receiver"],id_dict[s]))     
                        key.sendall(notify.encode())  

            elif(info["info-type"] == "create-grp"):
                gp_name = info["group-name"]
                admin = info["admin"]
                members = info["members"]
                group_id = generateID("grp",cursor)                 

                cursor.execute('''insert into grp values(
                                '{0}','{1}','{2}');'''.format(group_id,gp_name,admin))
                                
                for memb in members:   
                    cursor.execute('''insert into grp_memb values(
                                    '{0}','{1}',false);'''.format(memb,group_id))                                       
                    for key,value in id_dict.items(): 
                        if value == memb:                                      
                            cursor.execute('''update grp_memb set is_known=true where member_id='{0}' and group_id='{1}' ;'''.format(memb,group_id))                
                            add_to_grp = {"info-type":"group_added","group_name":info["group-name"],"admin":info["admin"],"group_id":group_id,"group_members":members}
                            add_to_grp = json.dumps(add_to_grp)                                                                      
                            key.sendall(add_to_grp.encode()) 
                            
                    
            elif(info["info-type"] == "get-users"):
                cursor.execute('''select name,id from USERS''')
                l = cursor.fetchall()
                l = {"info-type":"get-users","list":l}
                l = json.dumps(l)
                s.sendall(l.encode())

            elif(info["info-type"] == "group-message"):
                cursor.execute('''insert into MSG values
                                ('{0}',false,true,'{3}','{1}','{2}');'''.format(info["text"],id_dict[s],info["receiver"],info["group_id"]))
                                
                for key, value in id_dict.items():                    
                    if info["receiver"] == value :
                        notify = {"info-type":"grp-inst-msg","text":info["text"],"sender":id_dict[s],"group_id":info["group_id"]}
                        notify = json.dumps(notify)
                        cursor.execute('''update MSG set is_read=true where receiver_id ='{0}' and sender_id = '{1}' and is_group=true'''.format(info["receiver"],id_dict[s]))     
                        key.sendall(notify.encode()) 
                                   
    else:            
        if s in id_dict.keys():
            cursor.execute(''' update USERS set status=false where id='{0}';'''.format(id_dict[s]))    
            del id_dict[s]
        return False
    return True
                
            